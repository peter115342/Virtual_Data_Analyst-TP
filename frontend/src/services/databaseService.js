
import api from "./api";

export const connectDatabase = async (data) => {
  const response = await api.post("/api/connect-database", data);
  return response.data;
};


export const disconnectDatabase = async () => {
  const response = await api.post("/api/disconnect-database");
  return response.data;
};

export const askQuestion = async (question) => {
  const response = await api.post("/api/ask", {
    question,
  });
  return response.data;
};