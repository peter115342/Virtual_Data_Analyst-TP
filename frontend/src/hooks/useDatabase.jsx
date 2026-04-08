import { useState } from "react";
import { connectDatabase, disconnectDatabase } from "../services/databaseService";

export default function useDatabase() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const connect = async (data) => {
    try {
      setLoading(true);
      setError(null);
      const result = await connectDatabase(data);
      setSessionId(result.session_id || null);
      return result;
    } catch (err) {
      setError(err.response?.data?.message || "Connection failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const disconnect = async () => {
    const result = await disconnectDatabase(sessionId);
    setSessionId(null);
    return result;
  };

  return {
    connect,
    disconnect,
    loading,
    error,
    sessionId,
  };
}
