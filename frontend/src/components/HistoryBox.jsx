import { useState, useRef } from "react";

export default function HistoryBox({ title, description }) {
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
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                className="w-full h-9 px-2 py-1 text-black rounded-lg cursor-pointer hover:bg-[#F4BA8D] transition"
            >
                <h2 className="text-sm font-normal truncate">{title}</h2>
            </div>

            {expanded && position && (
                <div
                    className="fixed z-[9999] bg-[#F4BA8D] text-white rounded-lg shadow-xl p-2 w-72"
                    style={{
                        top: position.top,
                        left: position.left,
                    }}
                    
                >
                    <h2 className="text-sm font-normal text-black">{title}</h2>
                    <p className="text-xs text-gray-700 mt-1 break-words whitespace-normal">
                        {description}
                    </p>
                </div>
            )}
        </>
    );
}