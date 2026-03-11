export default function DatabaseLoader() {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-xl flex flex-col items-center gap-4">
        <div className="loader border-4 border-t-orange-500 border-gray-300 rounded-full w-12 h-12 animate-spin"></div>
        <p className="text-white text-lg font-medium">Connecting to database...</p>
      </div>
    </div>
  )
}
