import { PublicClientApplication } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_AZURE_AD_CLIENT_ID;
const tenantId = import.meta.env.VITE_AZURE_AD_TENANT_ID;
const defaultApiScope = clientId ? `api://${clientId}/access_as_user` : "";
const authorityTenant = import.meta.env.VITE_AZURE_AD_AUTHORITY || tenantId;
const authority = authorityTenant?.startsWith("https://")
  ? authorityTenant
  : `https://login.microsoftonline.com/${authorityTenant}`;

const msalConfig = {
  auth: {
    clientId,
    authority,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ["openid", "profile"],
};

export const apiTokenRequest = {
  scopes: [import.meta.env.VITE_AZURE_AD_API_SCOPE || defaultApiScope],
};

export const msalInstance = new PublicClientApplication(msalConfig);
