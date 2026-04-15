
export default function UserMessage({ context, isUser }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start "}`}>
      <div className={`${isUser ? "bg-[#F4BA8D]" : "bg-transparent"} text-black p-2 rounded-xl my-1 max-w-2/3 whitespace-pre-wrap break-words`}>
        {context}
      </div>
    </div>
  )
}


