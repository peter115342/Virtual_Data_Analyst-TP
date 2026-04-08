// HomePage.jsx
import { useState , useEffect} from "react";
import SideBar from "../components/SideBar.jsx";
import Chat from "../components/Chat.jsx";
import DatabaseModal from "../components/DatabaseModal.jsx";
import useDatabase from "../hooks/useDatabase";


export default function HomePage({ onLogout, userName }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDatabaseModalOpen, setIsDatabaseModalOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const { connect, disconnect, loading, error, sessionId } = useDatabase();

  const handleDatabaseButtonClick = async () => {
    if (isConnected) {
      try {
        await disconnect();
        setIsConnected(false);
      } catch (err) {
        console.error("Disconnect failed", err);
      }
    } else {
      setIsDatabaseModalOpen(true);
    }
  };

  // ✅ HOOK JE TU – SPRÁVNE
  useEffect(() => {
    if (isConnected) {
      setIsDatabaseModalOpen(false);
    }
  }, [isConnected]);
  return (
    <div className="h-screen flex bg-gray-100 relative">
      <div
        className={`bg-gray-800 transition-all duration-300
          ${isSidebarOpen ? "w-72" : "w-14"}
        `}
      >
        <SideBar
          isOpenS={isSidebarOpen}
          toggle={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenDatabase={() => handleDatabaseButtonClick()}
          isConnected={isConnected}
          onLogout={onLogout}
          userName={userName}
        />
      </div>

      <div className="flex-1">
        <Chat sessionId={sessionId} />
      </div>

      {isDatabaseModalOpen && (
        <DatabaseModal
          onClose={() => setIsDatabaseModalOpen(false)}
          onConnected={() => {
            setIsConnected(true);
            setIsDatabaseModalOpen(false);
          }}
          connect={connect}
          loading={loading}
          error={error}
        />
      )}
    </div>
  );
}
