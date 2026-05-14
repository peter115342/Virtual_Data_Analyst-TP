export default function UserMessage({ context, isUser, chartImage, chartTitle }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start "}`}>
      <div
        className={`${isUser ? "bg-green-400 max-w-xs" : "bg-blue-400 max-w-3xl"} text-white p-2 rounded-xl my-1 whitespace-pre-wrap break-words`}
      >
        {context}
        {chartImage && (
          <img
            src={chartImage}
            alt={chartTitle || "Generated chart"}
            className="mt-3 w-full rounded-md bg-white"
          />
        )}
      </div>
    </div>
  )
}
