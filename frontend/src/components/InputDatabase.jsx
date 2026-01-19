


export default function InputDatabase({ value, onChange, placeholder, type = "text" }) {
  return (
    <input
      type={type} 
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="bg-gray-700 text-white p-2 rounded w-full"
    />
  );
}


