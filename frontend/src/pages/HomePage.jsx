import { useState } from "react"
import SideBar from "../components/SideBar.jsx"
import Chat from "../components/Chat.jsx"


function HomePage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex bg-gray-100">
      <div
        className={`bg-gray-800 transition-all duration-300
          ${isSidebarOpen ? "w-72" : "w-14"}
        `}
      >
        <SideBar
          isOpen={isSidebarOpen}
          toggle={() => setIsSidebarOpen(!isSidebarOpen)}
        />
      </div>

      <div className="flex-1">
        <Chat />
      </div>
    </div>
  );
}

export default HomePage;

