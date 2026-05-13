import axios from "axios";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { apiTokenRequest, loginRequest, msalInstance } from "../auth/msalConfig";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

const devAuthEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_AUTH_BYPASS === "true";
const tokenMode = import.meta.env.VITE_AZURE_AD_TOKEN_MODE || "access_token";
const useIdToken = tokenMode === "id_token";

const authTokenRequest = useIdToken ? loginRequest : apiTokenRequest;
const tokenTypeLabel = useIdToken ? "ID token" : "API access token";

const getBearerToken = (response) => {
  const token = useIdToken ? response.idToken : response.accessToken;
  if (!token) {
    throw new Error(`Azure AD did not return an ${tokenTypeLabel}`);
  }
  return token;
};

// Attach an Azure AD access token to every request, or a static token in local development.
api.interceptors.request.use(async (config) => {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    try {
      const response = await msalInstance.acquireTokenSilent({
        ...authTokenRequest,
        account: accounts[0],
      });
      config.headers.Authorization = `Bearer ${getBearerToken(response)}`;
    } catch (error) {
      if (!(error instanceof InteractionRequiredAuthError)) {
        throw error;
      }

      const response = await msalInstance.acquireTokenPopup(authTokenRequest);
      config.headers.Authorization = `Bearer ${getBearerToken(response)}`;
    }
  } else if (devAuthEnabled) {
    config.headers.Authorization = "Bearer dev";
  } else {
    await msalInstance.loginRedirect(loginRequest);
    throw new Error("No signed-in Azure AD account");
  }
  return config;
});

export default api;
