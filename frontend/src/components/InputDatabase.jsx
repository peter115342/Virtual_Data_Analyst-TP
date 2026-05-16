


export default function InputDatabase({ value, onChange, placeholder, type = "text" }) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="
        w-full
        bg-[#eeeeee]
        text-gray-700
        border border-gray-300
        rounded-lg
        pl-5 pr-4 py-2
        focus:outline-none focus:border-orange-500
        appearance-none
        "
    />
  );
}


