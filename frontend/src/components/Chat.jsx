import { useState } from "react"
import InputQuestion from "./InputQuestion"
import UserMessage from "./UserMessage"
import { askQuestion } from "../services/databaseService";
import ChatHeader from "./ChatHeader";
import { getSessionHistory } from "../services/databaseService";
import { useEffect } from "react";

export default function Chat({ sessionId, isConnected, onDatabaseClick, userName, onLogout }) {
    const [messages, setMessages] = useState([])

    const handleSend = async (text) => {
        setMessages((prev) => [
            ...prev,
            { text, fromUser: true },
            { text: "Thinking...", fromUser: false, loading: true },
        ]);

        try {
            const result = await askQuestion(text, sessionId);

            setMessages((prev) => {
                const messagesWithoutThinking = prev.slice(0, -1);

                return [
                    ...messagesWithoutThinking,
                    {
                        text: `${result.summary || "No response."}\n\nSQL Query: ${result.sql_query || "N/A"}`,
                        fromUser: false,
                        sql: result.sql_query,
                        rowCount: result.row_count,
                    },
                ];
            });
        } catch (error) {
            setMessages((prev) => {
                const messagesWithoutThinking = prev.slice(0, -1);

                return [
                    ...messagesWithoutThinking,
                    {
                        text: "Failed to get response from server.",
                        fromUser: false,
                    },
                ];
            });
        }
    };

    useEffect(() => {
        const loadHistory = async () => {
            if (!sessionId) return;

            try {
            const data = await getSessionHistory(sessionId);
            const formatted = data.messages.map((msg) => ({
                text: msg.content,
                fromUser: msg.role === "user",
            }));

            setMessages(formatted);
            } catch (err) {
            console.log("Failed to load history", err);
            }
        };

        loadHistory();
        }, [sessionId]);




return (
  <div className="h-full flex flex-col relative">

    <ChatHeader
      isConnected={isConnected}
      onDatabaseClick={onDatabaseClick}
      userName={userName}
      onLogout={onLogout}
    />

    <div className="flex-1 flex flex-col min-h-0">

      <div className="flex-1 pt-25 overflow-y-auto p-4 flex flex-col gap-2">
        {messages.map((msg, i) => (
          <UserMessage key={i} context={msg.text} isUser={msg.fromUser} />
        ))}
      </div>

      <div className="p-4 flex justify-center sticky bottom-0">
        <InputQuestion onSend={handleSend} />
      </div>

    </div>
  </div>
);
}