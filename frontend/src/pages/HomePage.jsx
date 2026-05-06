import { useState, useEffect } from "react";
import SideBar from "../components/SideBar.jsx";
import Chat from "../components/Chat.jsx";
import DatabaseModal from "../components/DatabaseModal.jsx";
import useDatabase from "../hooks/useDatabase";
import { getDatabaseStatus } from "../services/databaseService.js";

export default function HomePage({ onLogout, userName }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDatabaseModalOpen, setIsDatabaseModalOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState(null);

  const { connect, disconnect, loading, error, sessionId } = useDatabase();

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await getDatabaseStatus();
        setIsConnected(res.connected);
        console.log("Database status:", res);
      } catch (err) {
        console.log("Status check failed", err);
        setIsConnected(false);
      }
    };

    checkConnection();
  }, []);

  const handleSelectSession = (id) => {
    setActiveSessionId(id);
    console.log("ACTIVE SESSION:", activeSessionId);
  };

  const handleDatabaseButtonClick = async () => {
    if (isConnected) {
      try {
        await disconnect();
        const res = await getDatabaseStatus();
        setIsConnected(res.connected);
      } catch (err) {
        console.error("Disconnect failed", err);
      }
    } else {
      setIsDatabaseModalOpen(true);
    }
  };

  useEffect(() => {
    if (isConnected) {
      setIsDatabaseModalOpen(false);
    }
  }, [isConnected]);

  return (
    <div className="h-screen flex bg-[#eeeeee] relative">
      <div
        className={`
          ${isSidebarOpen ? "w-72" : "w-14"}
          transition-all duration-300 ease-in-out
        `}
      >
        <SideBar
          onSelectSession={handleSelectSession}
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

      {isDatabaseModalOpen && (
        <DatabaseModal
          onClose={() => setIsDatabaseModalOpen(false)}
          onConnected={() => {
            setIsConnected(true);
          }}
          connect={connect}
          loading={loading}
          error={error}
        />
      )}
    </div>
  );
}