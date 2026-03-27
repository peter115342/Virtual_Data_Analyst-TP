import axios from "axios";
import { msalInstance, loginRequest } from "../auth/msalConfig";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach Azure AD ID token to every request
api.interceptors.request.use(async (config) => {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    try {
      const response = await msalInstance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });
      config.headers.Authorization = `Bearer ${response.idToken}`;
    } catch {
      // If silent fails, trigger interactive login
      await msalInstance.acquireTokenRedirect(loginRequest);
    }
  }
  return config;
});

export default api;