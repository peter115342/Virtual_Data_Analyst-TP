// useDatabase.jsx
import { useState, useEffect } from "react";
import { connectDatabase, disconnectDatabase } from "../services/databaseService";

export default function useDatabase() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Načítame pôvodné sessionId z localStorage pri štarte
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("active_session_id");
  });

  const connect = async (data) => {
    try {
      setLoading(true);
      setError(null);
      const result = await connectDatabase(data);
      const newSessionId = result.session_id || null;
      
      setSessionId(newSessionId);
      if (newSessionId) {
        localStorage.setItem("active_session_id", newSessionId);
      }
      return result;
    } catch (err) {
      setError(err.response?.data?.message || "Connection failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const disconnect = async () => {
    await disconnectDatabase(sessionId);
    setSessionId(null);
    localStorage.removeItem("active_session_id"); // Vymažeme pri odpojení
  };

  return {
    connect,
    disconnect,
    loading,
    error,
    sessionId,
  };
}