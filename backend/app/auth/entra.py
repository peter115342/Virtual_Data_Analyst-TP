"""
Azure Entra ID JWT token validation for FastAPI.
Validates tokens issued by Microsoft Entra ID using JWKS (JSON Web Key Sets).
"""

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()

# Cache for JWKS keys
_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    """Fetch Microsoft's public signing keys (JWKS) for token verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def _get_signing_key(token: str, jwks: dict) -> jwt.algorithms.RSAAlgorithm:
    """Extract the correct signing key from JWKS based on the token's kid header."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key_data in jwks.get("keys", []):
        if key_data["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find matching signing key",
    )


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency that validates an Azure Entra ID access token.

    Returns the decoded token payload (claims) if valid.
    Raises HTTPException 401 if invalid.
    """
    token = credentials.credentials

    if settings.fastapi_env == "development" and token == "dev":
        return {"sub": "dev-user-001", "name": "Dev User", "preferred_username": "dev@localhost"}

    if not settings.azure_ad_client_id or not settings.azure_ad_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure AD authentication is not configured",
        )

    try:
        jwks = await _get_jwks()
        signing_key = _get_signing_key(token, jwks)

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.azure_ad_client_id,
            options={"require": ["exp", "aud"], "verify_iss": False},
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience",
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except httpx.HTTPError:
        # Clear cache so next request retries
        global _jwks_cache
        _jwks_cache = None
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify token - could not reach identity provider",
        )
