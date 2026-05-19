import { useCallback, useEffect, useState } from "react"
import SideBar from "../components/SideBar.jsx"
import Chat from "../components/Chat.jsx"
import DatabaseModal from "../components/DatabaseModal.jsx"
import DisconnectPromptModal from "../components/DisconnectPromptModal.jsx"
import useDatabase from "../hooks/useDatabase"
import { getDatabaseStatus } from "../services/databaseService.js"

export default function HomePage({ onLogout, userName }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isDatabaseModalOpen, setIsDatabaseModalOpen] = useState(false)
  const [isDisconnectPromptOpen, setIsDisconnectPromptOpen] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [sessionsList, setSessionsList] = useState([])
  const [pendingSession, setPendingSession] = useState(null)

  const { connect, disconnect, saveSessionId, loading, error, sessionId } = useDatabase()

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await getDatabaseStatus()
        setIsConnected(res.connected)
      } catch (err) {
        console.error("Database status check failed", err)
        setIsConnected(false)
      }
    }

    checkConnection()
  }, [])

  useEffect(() => {
    if (sessionId && !activeSessionId) {
      setActiveSessionId(sessionId)
    }
  }, [sessionId, activeSessionId])

  const handleSessionsFetched = useCallback((sessions) => {
    setSessionsList(sessions)
  }, [])

  const handleSessionIdChange = (id) => {
    saveSessionId(id)
    setActiveSessionId(id)
  }

  const handleSelectSession = (clickedSession) => {
    const selectedSession = typeof clickedSession === "string"
      ? sessionsList.find((session) => session.session_id === clickedSession) || {
        session_id: clickedSession,
      }
      : clickedSession

    if (!selectedSession?.session_id) {
      return
    }

    if (!isConnected) {
      setPendingSession(selectedSession)
      setIsDatabaseModalOpen(true)
      return
    }

    const currentSession = sessionsList.find((session) => session.session_id === sessionId)
    const sameDatabase =
      !currentSession?.db_name ||
      !selectedSession.db_name ||
      selectedSession.db_name === currentSession.db_name

    if (sameDatabase) {
      setPendingSession(null)
      saveSessionId(selectedSession.session_id)
      setActiveSessionId(selectedSession.session_id)
      return
    }

    setPendingSession(selectedSession)
    setIsDisconnectPromptOpen(true)
  }

  const handleConfirmDisconnectAndSwitch = async () => {
    try {
      setIsDisconnectPromptOpen(false)
      await disconnect()
      setIsConnected(false)
      setIsDatabaseModalOpen(true)
    } catch (err) {
      console.error("Disconnect failed during session switch", err)
    }
  }

  const handleDatabaseButtonClick = async () => {
    if (isConnected) {
      try {
        await disconnect()
        setIsConnected(false)
        setActiveSessionId(null)
        setPendingSession(null)
      } catch (err) {
        console.error("Disconnect failed", err)
      }
      return
    }

    setPendingSession(null)
    setIsDatabaseModalOpen(true)
  }

  const handleDatabaseConnected = (result) => {
    setIsConnected(true)
    if (pendingSession?.session_id) {
      setActiveSessionId(pendingSession.session_id)
    } else if (result?.session_id) {
      setActiveSessionId(result.session_id)
    }
    setPendingSession(null)
  }

  return (
    <div className="h-screen flex bg-[#eeeeee] relative">
      <div className={`${isSidebarOpen ? "w-72" : "w-14"} transition-all duration-300 ease-in-out`}>
        <SideBar
          onSelectSession={handleSelectSession}
          onSessionsFetched={handleSessionsFetched}
          isOpenS={isSidebarOpen}
          toggle={() => setIsSidebarOpen(!isSidebarOpen)}
          isConnected={isConnected}
          activeSessionId={activeSessionId}
        />
      </div>

      <div className="flex-1">
        <Chat
          sessionId={activeSessionId || sessionId}
          onSessionIdChange={handleSessionIdChange}
          isConnected={isConnected}
          onDatabaseClick={handleDatabaseButtonClick}
          userName={userName}
          onLogout={onLogout}
        />
      </div>

      <DisconnectPromptModal
        isOpen={isDisconnectPromptOpen}
        onClose={() => setIsDisconnectPromptOpen(false)}
        onConfirm={handleConfirmDisconnectAndSwitch}
        dbName={pendingSession?.db_name}
      />

      {isDatabaseModalOpen && (
        <DatabaseModal
          onClose={() => setIsDatabaseModalOpen(false)}
          onConnected={handleDatabaseConnected}
          connect={connect}
          loading={loading}
          error={error}
          prefillData={pendingSession}
        />
      )}
    </div>
  )
}
