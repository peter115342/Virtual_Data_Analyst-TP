"""
Azure Entra ID JWT token validation for FastAPI.
Validates bearer tokens issued by Microsoft Entra ID.
"""

from typing import Any

import httpx
import jwt
import jwt.algorithms
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()

_BROAD_TENANT_ALIASES = {"common", "consumers", "organizations"}
_JWT_V1 = "1.0"
_metadata_cache: dict[str, dict[str, Any]] = {}
_jwks_cache: dict[str, dict[str, Any]] = {}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _server_auth_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def _csv_values(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [item.strip() for item in value if item.strip()]


def _allowed_tenants() -> list[str]:
    configured = _csv_values(settings.azure_ad_allowed_tenants)
    if configured:
        tenants = configured
    else:
        tenants = [settings.azure_ad_tenant_id.strip()]

    normalized_tenants = [tenant.lower() for tenant in tenants if tenant]
    if not normalized_tenants:
        raise _server_auth_error("Azure AD allowed tenant is not configured")

    if any(tenant in _BROAD_TENANT_ALIASES for tenant in normalized_tenants):
        raise _server_auth_error("Azure AD allowed tenants must be tenant-specific IDs")

    return list(dict.fromkeys(normalized_tenants))


def _allowed_audiences() -> list[str]:
    audiences = _csv_values(settings.azure_ad_allowed_audiences)

    client_id = settings.azure_ad_client_id.strip()
    if client_id:
        audiences.extend([client_id, f"api://{client_id}"])

    unique_audiences = list(dict.fromkeys(audiences))
    if not unique_audiences:
        raise _server_auth_error("Azure AD API audience is not configured")
    return unique_audiences


def _token_tenant_id(payload: dict[str, Any]) -> str:
    token_tenant = str(payload.get("tid", "")).strip().lower()
    if not token_tenant:
        raise _unauthorized("Token is missing tenant ID")
    return token_tenant


def _openid_config_url(token_version: str, tenant_id: str) -> str:
    base_url = f"https://login.microsoftonline.com/{tenant_id}"
    if token_version == _JWT_V1:
        return f"{base_url}/.well-known/openid-configuration"
    return f"{base_url}/v2.0/.well-known/openid-configuration"


async def _get_openid_config(token_version: str, tenant_id: str) -> dict[str, Any]:
    config_url = _openid_config_url(token_version, tenant_id)
    if config_url in _metadata_cache:
        return _metadata_cache[config_url]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(config_url)
        response.raise_for_status()
        metadata = response.json()

    if not isinstance(metadata.get("issuer"), str) or not isinstance(metadata.get("jwks_uri"), str):
        raise _server_auth_error("Azure AD metadata is missing issuer or signing keys")

    _metadata_cache[config_url] = metadata
    return metadata


async def _get_jwks(token_version: str, tenant_id: str) -> dict[str, Any]:
    metadata = await _get_openid_config(token_version, tenant_id)
    jwks_uri = metadata["jwks_uri"]
    if jwks_uri in _jwks_cache:
        return _jwks_cache[jwks_uri]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(jwks_uri)
        response.raise_for_status()
        jwks = response.json()

    _jwks_cache[jwks_uri] = jwks
    return jwks


def _get_unverified_claims(token: str) -> dict[str, Any]:
    try:
        claims = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc}") from exc

    if not isinstance(claims, dict):
        raise _unauthorized("Invalid token claims")
    return claims


def _get_signing_key(token: str, jwks: dict[str, Any]) -> Any:
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token header: {exc}") from exc

    kid = unverified_header.get("kid")
    if not kid:
        raise _unauthorized("Token header is missing signing key ID")

    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

    raise _unauthorized("Unable to find matching signing key")


def _validate_tenant(payload: dict[str, Any]) -> None:
    token_tenant = _token_tenant_id(payload)
    if token_tenant not in _allowed_tenants():
        raise _unauthorized("Invalid token tenant")


def _validate_required_scope(payload: dict[str, Any]) -> None:
    required_scope = settings.azure_ad_required_scope.strip()
    if not required_scope:
        return

    token_scopes = str(payload.get("scp", "")).split()
    if required_scope not in token_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is missing the required API scope",
        )


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """
    FastAPI dependency that validates an Azure Entra ID bearer token.

    Returns the decoded token payload (claims) if valid.
    Raises HTTPException 401/403 if invalid.
    """
    token = credentials.credentials

    if settings.fastapi_env == "development" and token == "dev":  # nosec
        return {"sub": "dev-user-001", "name": "Dev User", "preferred_username": "dev@localhost"}

    if not settings.azure_ad_client_id or not settings.azure_ad_tenant_id:
        raise _server_auth_error("Azure AD authentication is not configured")

    unverified_claims = _get_unverified_claims(token)
    token_version = str(unverified_claims.get("ver", "2.0"))

    try:
        token_tenant = _token_tenant_id(unverified_claims)
        _validate_tenant(unverified_claims)

        metadata = await _get_openid_config(token_version, token_tenant)
        jwks = await _get_jwks(token_version, token_tenant)
        signing_key = _get_signing_key(token, jwks)

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=_allowed_audiences(),
            issuer=metadata["issuer"],
            options={"require": ["exp", "aud", "iss", "tid"]},
        )
        _validate_tenant(payload)
        _validate_required_scope(payload)
        return payload

    except jwt.ExpiredSignatureError as exc:
        raise _unauthorized("Token has expired") from exc
    except jwt.InvalidAudienceError as exc:
        raise _unauthorized("Invalid token audience") from exc
    except jwt.InvalidIssuerError as exc:
        raise _unauthorized("Invalid token issuer") from exc
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc}") from exc
    except httpx.HTTPError as exc:
        _metadata_cache.clear()
        _jwks_cache.clear()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify token - could not reach identity provider",
        ) from exc
