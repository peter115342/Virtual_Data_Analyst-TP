import { useState, useEffect } from "react"
import InputQuestion from "./InputQuestion"
import UserMessage from "./UserMessage"


export default function Chat() {
    const [messages, setMessages] = useState([])

    const handleSend = (text) => {
        console.log("HANDLE SEND", text)

        setMessages(prev => [
        ...prev,
        { text, fromUser: true },
        { text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", fromUser: false }
        ])
    }

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