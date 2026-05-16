import { useState, useRef } from "react";

export default function HistoryBox({
  title,
  description,
  date,
  onClick,
  isActive,
}) {
  const [expanded, setExpanded] = useState(false);
  const [position, setPosition] = useState(null);

  const timeoutRef = useRef(null);
  const itemRef = useRef(null);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      const rect = itemRef.current.getBoundingClientRect();

      setPosition({
        top: rect.top,
        left: rect.left,
        width: rect.width,
      });

      setExpanded(true);
    }, 800);
  };

  const handleMouseLeave = () => {
    clearTimeout(timeoutRef.current);
    setExpanded(false);
  };

  return (
    <>
      <div
        ref={itemRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick && onClick();
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className={`w-full px-3 py-2 rounded-xl cursor-pointer transition-all duration-200
          ${
            isActive
              ? "bg-[#F9730B] text-white shadow-md"
              : "text-black hover:bg-[#F4BA8D]"
          }`}
      >
        <div className="flex flex-col">

          {/* TITLE */}
          <h2 className="text-sm font-medium truncate">
            {title}
          </h2>

          {/* DESCRIPTION */}
          <p
            className={`text-xs italic mt-0.5 truncate
              ${
                isActive
                  ? "text-orange-100"
                  : "text-gray-600"
              }`}
          >
            {description}
          </p>

          {/* DATE */}
          <p
            className={`text-[10px] mt-1 truncate
              ${
                isActive
                  ? "text-orange-200"
                  : "text-gray-400"
              }`}
          >
            {date}
          </p>

        </div>
      </div>

      {/* OPTIONAL TOOLTIP */}
      {/* 
      {expanded && position && (
        <div
          className="fixed z-[9999] bg-[#F4BA8D] text-white rounded-lg shadow-xl p-2 w-72"
          style={{
            top: position.top,
            left: position.left,
          }}
        >
          <h2 className="text-sm font-normal text-black">
            {title}
          </h2>

          <p className="text-xs text-gray-700 mt-1 break-words whitespace-normal">
            {description}
          </p>
        </div>
      )}
      */}
    </>
  );
}