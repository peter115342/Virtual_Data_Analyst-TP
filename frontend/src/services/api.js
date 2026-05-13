import axios from "axios";
import { apiTokenRequest, loginRequest, msalInstance } from "../auth/msalConfig";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

const devAuthEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_AUTH_BYPASS === "true";

// Attach an Azure AD access token to every request, or a static token in local development.
api.interceptors.request.use(async (config) => {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    try {
      const response = await msalInstance.acquireTokenSilent({
        ...apiTokenRequest,
        account: accounts[0],
      });
      if (!response.accessToken) {
        throw new Error("Azure AD did not return an API access token");
      }
      config.headers.Authorization = `Bearer ${response.accessToken}`;
    } catch {
      await msalInstance.acquireTokenRedirect(apiTokenRequest);
      throw new Error("Redirecting to Azure AD for API token acquisition");
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
