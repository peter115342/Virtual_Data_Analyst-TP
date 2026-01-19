// ButtonDatabase.jsx
export default function ButtonDatabase({ onClick, label }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-6 py-3 font-semibold text-white transition ${
        label.includes("Disconnect") ? "bg-red-700 hover:bg-red-600" : "bg-orange-900 hover:bg-orange-800"
      }`}
    >
      {label}
    </button>
  );
}
