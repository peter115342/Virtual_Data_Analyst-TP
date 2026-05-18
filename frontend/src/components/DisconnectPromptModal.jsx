import React from "react";

export default function DisconnectPromptModal({ isOpen, onClose, onConfirm, dbName }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#eeeeee] p-6 rounded-xl w-full max-w-md relative shadow-2xl border border-white/20">
        <h2 className="text-[#F9730B] text-xl font-semibold mb-3">
          Zmena databázového pripojenia
        </h2>
        <p className="text-gray-700 text-sm mb-6 leading-relaxed">
          Tento chat prislúcha k databáze <span className="font-bold text-black">{dbName || "Neznáma DB"}</span>. 
          Ak chcete otvoriť tento chat, musíte sa pripojiť k tejto databáze.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-200 transition text-sm font-medium"
          >
            Zrušiť
          </button>
          <button
            onClick={onConfirm}
            className="px-5 py-2 rounded-full bg-[#F9730B] text-white font-semibold hover:bg-[#E66400] transition text-sm shadow-sm"
          >
            Pripojiť sa k databáze
          </button>
        </div>
      </div>
    </div>
  );
}