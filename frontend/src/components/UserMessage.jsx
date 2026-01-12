
export default function UserMessage({ context, isUser }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start "}`}>
      <div className={`${isUser ? "bg-green-400" : "bg-blue-400"} text-white p-2 rounded-xl my-1 max-w-xs whitespace-pre-wrap break-words`}>
        {context}
      </div>
    </div>
  )
}


