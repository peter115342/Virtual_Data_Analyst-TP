/**
 * TODO: Implement API calls to FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * TODO: Implement POST to /api/generate-dashboard
 */
export const generateDashboard = async (description, sketchUrl, comments) => {
  // TODO: Implement
  throw new Error('Not implemented');
};

/**
 * TODO: Implement POST to /api/generate-callback
 */
export const generateCallback = async (elementId, functionality) => {
  // TODO: Implement
  throw new Error('Not implemented');
};

/**
 * TODO: Implement POST to /api/ask
 */
export const askQuestion = async (question) => {
  // TODO: Implement
  throw new Error('Not implemented');
};

export default apiClient;
