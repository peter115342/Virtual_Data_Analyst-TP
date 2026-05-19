export default function UserMessage({ context, isUser, chartImage, chartTitle }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`${isUser ? "bg-[#F4BA8D] max-w-[66.666%]" : "bg-transparent max-w-3xl"} text-black p-2 rounded-xl my-1 whitespace-pre-wrap break-words`}
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
