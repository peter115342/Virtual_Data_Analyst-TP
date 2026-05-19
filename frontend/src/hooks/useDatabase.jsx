import { useState } from "react"
import { connectDatabase, disconnectDatabase } from "../services/databaseService"

export default function useDatabase() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("active_session_id")
  })

  const saveSessionId = (newSessionId) => {
    setSessionId(newSessionId)
    if (newSessionId) {
      localStorage.setItem("active_session_id", newSessionId)
    } else {
      localStorage.removeItem("active_session_id")
    }
  }

  const connect = async (data) => {
    try {
      setLoading(true)
      setError(null)
      const result = await connectDatabase(data)
      saveSessionId(result.session_id || null)
      return result
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || "Connection failed")
      throw err
    } finally {
      setLoading(false)
    }
  }

  const disconnect = async () => {
    await disconnectDatabase(sessionId)
    saveSessionId(null)
  }

  return {
    connect,
    disconnect,
    saveSessionId,
    loading,
    error,
    sessionId,
  }
}
