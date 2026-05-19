import { useEffect, useRef, useState } from "react"
import InputQuestion from "./InputQuestion"
import UserMessage from "./UserMessage"
import { askQuestion, getSessionHistory } from "../services/databaseService"
import ChatHeader from "./ChatHeader"

export default function Chat({
  sessionId,
  onSessionIdChange,
  isConnected,
  onDatabaseClick,
  userName,
  onLogout,
}) {
  const [messages, setMessages] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(sessionId)
  const skipNextHistoryLoadRef = useRef(null)

  useEffect(() => {
    setCurrentSessionId(sessionId)
  }, [sessionId])

  const handleSend = async (text) => {
    setMessages((prev) => [
      ...prev,
      { text, fromUser: true },
      { text: "Thinking...", fromUser: false, loading: true },
    ])

    try {
      const result = await askQuestion(text, currentSessionId)

      if (result.session_id && result.session_id !== currentSessionId) {
        skipNextHistoryLoadRef.current = result.session_id
        setCurrentSessionId(result.session_id)
        onSessionIdChange?.(result.session_id)
      }

      setMessages((prev) => {
        const messagesWithoutThinking = prev.slice(0, -1)

        return [
          ...messagesWithoutThinking,
          {
            text: `${result.summary || "No response."}\n\nSQL Query: ${result.sql_query || "N/A"}`,
            fromUser: false,
            sql: result.sql_query,
            rowCount: result.row_count,
            chartImage: result.chart_image,
            chartTitle: result.chart_intent?.title,
          },
        ]
      })
    } catch (error) {
      console.error("Failed to send question", error)
      setMessages((prev) => {
        const messagesWithoutThinking = prev.slice(0, -1)

        return [
          ...messagesWithoutThinking,
          {
            text: "Failed to get response from server.",
            fromUser: false,
          },
        ]
      })
    }
  }

  useEffect(() => {
    const loadHistory = async () => {
      if (!sessionId) {
        setMessages([])
        return
      }

      if (skipNextHistoryLoadRef.current === sessionId) {
        skipNextHistoryLoadRef.current = null
        return
      }

      try {
        const data = await getSessionHistory(sessionId)
        const formatted = data.messages.map((msg) => ({
          text: msg.role === "assistant" && msg.sql_query
            ? `${msg.content}\n\nSQL Query: ${msg.sql_query}`
            : msg.content,
          fromUser: msg.role === "user",
          sql: msg.sql_query,
          rowCount: msg.row_count,
        }))

        setMessages(formatted)
      } catch (err) {
        console.log("Failed to load history", err)
      }
    }

    loadHistory()
  }, [sessionId])

  return (
    <div className="h-full flex flex-col relative">
      <ChatHeader
        isConnected={isConnected}
        onDatabaseClick={onDatabaseClick}
        userName={userName}
        onLogout={onLogout}
      />

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 pt-24 sm:pt-20 overflow-y-auto p-4 flex flex-col gap-2">
          {messages.map((msg, i) => (
            <UserMessage
              key={i}
              context={msg.text}
              isUser={msg.fromUser}
              chartImage={msg.chartImage}
              chartTitle={msg.chartTitle}
            />
          ))}
        </div>

        <div className="p-4 flex justify-center sticky bottom-0">
          <InputQuestion onSend={handleSend} />
        </div>
      </div>
    </div>
  )
}
