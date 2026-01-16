import { useState } from "react";
import { connectDatabase, disconnectDatabase } from "../services/databaseService";

export default function useDatabase() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const connect = async (data) => {
    try {
      setLoading(true);
      setError(null);
      return await connectDatabase(data);
    } catch (err) {
      setError(err.response?.data?.message || "Connection failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const disconnect = async () => {
    return await disconnectDatabase();
  };

  return {
    connect,
    disconnect,
    loading,
    error,
  };
}
