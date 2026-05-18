import { useState, useEffect } from "react";
import SideBar from "../components/SideBar.jsx";
import Chat from "../components/Chat.jsx";
import DatabaseModal from "../components/DatabaseModal.jsx";
import DisconnectPromptModal from "../components/DisconnectPromptModal.jsx";
import useDatabase from "../hooks/useDatabase";
import { getDatabaseStatus } from "../services/databaseService.js";

export default function HomePage({ onLogout, userName }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDatabaseModalOpen, setIsDatabaseModalOpen] = useState(false);
  const [isDisconnectPromptOpen, setIsDisconnectPromptOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  const { connect, disconnect, loading, error, sessionId } = useDatabase();
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  const [sessionsList, setSessionsList] = useState([]); 
  const [pendingSession, setPendingSession] = useState(null); // Tu bude uložený celý objekt chatu

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await getDatabaseStatus();
        setIsConnected(res.connected);
      } catch (err) {
        setIsConnected(false);
      }
    };
    checkConnection();
  }, []);

  const handleSessionsFetched = (sessions) => {
    setSessionsList(sessions);
  };

  const handleSelectSession = (clickedSession) => {
    // clickedSession je teraz celá schránka dát z MongoDB (objekt)
    if (!isConnected) {
      // Ak nie sme pripojení, rovno otvoríme prihlasovací modal a predvyplníme ho
      setPendingSession(clickedSession);
      setIsDatabaseModalOpen(true);
    } else {
      // Sme pripojení, zistíme detaily o aktuálnej session z hooku
      const currentSession = sessionsList.find((s) => s.session_id === sessionId);
      
      if (currentSession && clickedSession.db_name === currentSession.db_name) {
        // Klikli sme na rovnakú databázu, iba prepneme chat
        setActiveSessionId(clickedSession.session_id);
      } else {
        // Klikli sme na inú databázu -> otvoríme varovný prompt modal
        setPendingSession(clickedSession);
        setIsDisconnectPromptOpen(true);
      }
    }
  };

  const handleConfirmDisconnectAndSwitch = async () => {
    try {
      setIsDisconnectPromptOpen(false);
      await disconnect(); // Odpojíme sa
      setIsConnected(false);
      setIsDatabaseModalOpen(true); // Otvoríme formulár s dátami z pendingSession
    } catch (err) {
      console.error("Disconnect failed during session switch", err);
    }
  };

  const handleDatabaseButtonClick = async () => {
    if (isConnected) {
      try {
        await disconnect();
        setIsConnected(false);
      } catch (err) {
        console.error("Disconnect failed", err);
      }
    } else {
      setPendingSession(null); // Čisté kliknutie (prázdny formulár)
      setIsDatabaseModalOpen(true);
    }
  };

  useEffect(() => {
    if (sessionId) {
      setActiveSessionId(sessionId);
    }
  }, [sessionId]);

  return (
    <div className="h-screen flex bg-[#eeeeee] relative">
      <div className={` ${isSidebarOpen ? "w-72" : "w-14"} transition-all duration-300 ease-in-out `}>
        <SideBar
          onSelectSession={handleSelectSession}
          onSessionsFetched={handleSessionsFetched}
          isOpenS={isSidebarOpen}
          toggle={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenDatabase={handleDatabaseButtonClick}
          isConnected={isConnected}
          onLogout={onLogout}
          userName={userName}
          activeSessionId={activeSessionId}
        />
      </div>

      <div className="flex-1">
        <Chat
          sessionId={activeSessionId || sessionId}
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
          onConnected={() => setIsConnected(true)}
          connect={connect}
          loading={loading}
          error={error}
          prefillData={pendingSession} 
        />
      )}
    </div>
  );
}