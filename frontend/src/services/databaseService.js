
import api from "./api";

export const connectDatabase = async (data) => {
  const response = await api.post("/api/connect-database", data);
  return response.data;
};


export const disconnectDatabase = async (sessionId) => {
  const response = await api.post("/api/disconnect-database", {
    session_id: sessionId || null,
  });
  return response.data;
};

export const askQuestion = async (question, sessionId) => {
  const response = await api.post("/api/ask", {
    question,
    session_id: sessionId || null,
  });
  return response.data;
};

export const getSessionHistory = async (sessionId) => {
  const response = await api.get(`/api/history/${sessionId}`);
  return response.data;
};

export const listSessions = async () => {
  const response = await api.get("/api/sessions");
  return response.data;
};


export const listMongoSessions = async () => {
  const response = await api.get("/api/mongo/sessions");

  if (!response.data) {
    throw new Error("No data returned");
  }

  return response.data;
};