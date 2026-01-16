import { useState } from "react"
import InputQuestion from "./InputQuestion"
import UserMessage from "./UserMessage"
import { askQuestion } from "../services/databaseService";

export default function Chat() {
    const [messages, setMessages] = useState([])

    const handleSend = async (text) => {
        setMessages((prev) => [
            ...prev,
            { text, fromUser: true },
            { text: "Thinking...", fromUser: false, loading: true },
        ]);

        try {
            const result = await askQuestion(text);

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
                        text: "❌ Failed to get response from server.",
                        fromUser: false,
                    },
                ];
            });
        }
    };




    return (
        <div className="h-screen flex flex-col justify-end bg-gray-700 p-4 gap-2" >
            <div className="flex flex-col gap-2 overflow-y-auto" >
                {messages.map((msg, i) => (
                <UserMessage
                    key={i}
                    context={msg.text}
                    isUser={msg.fromUser}
                />
                ))}
            </div>
            <InputQuestion onSend={handleSend} />
        </div>
    )
}