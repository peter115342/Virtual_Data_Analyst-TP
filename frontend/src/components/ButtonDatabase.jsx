export default function ButtonDatabase({ onClick, label }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-6 py-3 font-semibold text-white transition shadow-lg hover:shadow-xl ${
        label.includes("Disconnect") ? "bg-[#F9730B] hover:bg-[#E66400]" : "bg-[#F9730B] hover:bg-[#E66400]"
      }`}
    >
      {label}
    </button>
  );
}
