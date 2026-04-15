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
          isOpenS={isSidebarOpen}
          toggle={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenDatabase={() => handleDatabaseButtonClick()}
          isConnected={isConnected}
          onLogout={onLogout}
          userName={userName}
        />
      </div>

      <div className="flex-1">
        <Chat
          sessionId={sessionId}
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
