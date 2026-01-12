import { useRef, useState } from "react"
import ButtonSend from "./ButtonSend"

export default function InputUser({ onSend }) {
  const textareaRef = useRef(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [text, setText] = useState("")

  const handleInput = () => {
    const el = textareaRef.current
    el.style.height = "auto"

    const maxHeight = 128
    const newHeight = Math.min(el.scrollHeight, maxHeight)

    el.style.height = newHeight + "px"

    setIsExpanded(newHeight > 40)
  }

  const handleKeyDown = (e) => { 
    if (e.key === "Enter") {
      if (e.metaKey || e.ctrlKey) {
        e.preventDefault()
        setText((prev) => {
          const newText = prev + "\n"
          setTimeout(() => handleInput(), 0)
          return newText
        })
      } else {
        e.preventDefault()
        handleSend()
      }
    }
  }

  const handleSend = () => {
    if (text.trim() === "") return;
    onSend(text);
    setText(""); 
    setTimeout(() => handleInput(), 0);
  }

  return (
    <div
      className={`
        bg-gray-500
        w-full
        flex
        items-end
        gap-2
        transition-all
        duration-150
        px-2
        py-2
        ${isExpanded ? "rounded-xl" : "rounded-full"}
        
      `}
    >
      <textarea
        ref={textareaRef}
        rows={1}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        placeholder="Type a question..."
        className="
          flex-grow
          resize-none
          bg-transparent
          px-4
          py-1
          focus:outline-none
          text-lg
          leading-relaxed
          min-h-8
          max-h-30
          overflow-y-auto
          text-white
        "
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <ButtonSend onClick={handleSend}/>
    </div>
  )
}

