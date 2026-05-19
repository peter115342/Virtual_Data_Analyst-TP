import { useEffect, useState } from "react"
import crossOrange from "../assets/cross-orange.svg"
import filterOrange from "../assets/filter-orange.svg"
import HistoryBox from "./HistoryBox.jsx"
import logo from "../assets/VDA_logo.png"
import { listMongoSessions } from "../services/databaseService"

export default function SideBar({
  isOpenS,
  toggle,
  isConnected,
  onSelectSession,
  activeSessionId,
  onSessionsFetched,
}) {
  const [sessions, setSessions] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const data = await listMongoSessions()
        const fetchedSessions = data.sessions || []
        setSessions(fetchedSessions)
        onSessionsFetched?.(fetchedSessions)
        setError(null)
      } catch (err) {
        console.error("Failed to load sessions:", err)
        setError("Failed to load sessions")
      }
    }

    fetchSessions()
  }, [isConnected, activeSessionId, onSessionsFetched])

  const chats = sessions.map((session) => {
    const firstUserMessage = session.messages?.find((message) => message.role === "user")
    const shortPreview = firstUserMessage?.content
      ?.split(" ")
      .slice(0, 4)
      .join(" ")

    return {
      id: session.session_id,
      title: session.db_name || "Unknown DB",
      description: shortPreview ? `${shortPreview}...` : "No messages yet",
      date: session.connected_at
        ? new Date(session.connected_at).toLocaleString()
        : "No date",
      session,
    }
  })

  return (
    <div className="h-full min-h-0 p-1 flex flex-col bg-[#E8E8E8]">
      <div className="flex items-center justify-between">
        {isOpenS && (
          <img
            src={logo}
            alt="Logo"
            className="w-18"
          />
        )}

        <button
          onClick={toggle}
          className="w-10 h-10 flex items-center justify-center rounded-full hover:brightness-85"
        >
          <img
            src={isOpenS ? crossOrange : filterOrange}
            alt=""
            className={isOpenS ? "w-6" : "w-7"}
          />
        </button>
      </div>

      {isOpenS && (
        <div className="flex flex-col items-center gap-4 flex-1 min-h-0 bg-[#E8E8E8]">
          {error && (
            <div className="text-red-500 text-xs w-full px-2">
              {error}
            </div>
          )}

          <div className="flex-1 w-full overflow-y-auto mt-2 space-y-1 pr-1 custom-scrollbar min-h-0">
            {chats.length === 0 && !error && (
              <div className="text-gray-500 text-sm px-2">
                No sessions yet
              </div>
            )}

            {chats.map((chat) => (
              <HistoryBox
                key={chat.id}
                title={chat.title}
                description={chat.description}
                date={chat.date}
                onClick={() => {
                  onSelectSession(chat.session)
                }}
                isActive={chat.id === activeSessionId}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
