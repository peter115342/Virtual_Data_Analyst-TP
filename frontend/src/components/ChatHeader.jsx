import ButtonDatabase from "./ButtonDatabase.jsx";

export default function ChatHeader({ isConnected, onDatabaseClick, userName, onLogout }) {
  return (
    <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-6 py-3 backdrop-blur-md bg-[#eeeeee]/30 border-b border-white/20">
      
      <div className="text-lg  text-[#F9730B] ">
        Virtual Data Analyst
      </div>

      <div className="flex-1 flex justify-center">
        <ButtonDatabase
          onClick={onDatabaseClick}
          label={isConnected ? "Disconnect Database" : "Connect Database"}
        />
      </div>

      <div className="flex items-center gap-4">

        <div className="text-gray-400 text-sm text-center">
            {userName && (
              <p className="mb-2">
                Signed in as{" "}
                <span className="font-semibold text-black">{userName}</span>
              </p>
            )}
            <button
              onClick={onLogout}
              className="text-red-400 hover:text-red-300 underline text-sm transition"
            >
              Sign out
            </button>

        </div>

        <button className="p-2 rounded-full hover:bg-gray-200 transition">
          <svg
            className="w-5 h-5 text-gray-700"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <circle cx="12" cy="5" r="2" />
            <circle cx="12" cy="12" r="2" />
            <circle cx="12" cy="19" r="2" />
          </svg>
        </button>

      </div>
    </div>
  );
}