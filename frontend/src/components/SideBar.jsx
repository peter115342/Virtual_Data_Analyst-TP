// SideBar.jsx
import ButtonDatabase from "./ButtonDatabase.jsx";
import crossWhite from '../assets/cross-white.svg';
import filterWhite from "../assets/filter-white.svg";

export default function SideBar({ isOpenS, toggle, onOpenDatabase, isConnected, onLogout, userName }) {
  return (
    <div className="h-full p-2 flex flex-col justify-between">
      <div className={`flex ${isOpenS ? "justify-end" : "justify-center"}`}>
        <button
          onClick={toggle}
          className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-700 transition"
        >
          <img
            src={isOpenS ? crossWhite : filterWhite}
            alt=""
            className={isOpenS ? "w-3" : "w-5"}
          />
        </button>
      </div>

      {isOpenS && (
        <div className="flex flex-col items-center gap-4">
          <div className="text-white flex justify-center">
            <ButtonDatabase
              onClick={onOpenDatabase}
              label={isConnected ? "Disconnect Database" : "Connect Database"}
              isConnected={isConnected}
            />
          </div>

          <div className="text-gray-300 text-sm text-center">
            {userName && <p className="mb-2">Signed in as <span className="font-semibold text-white">{userName}</span></p>}
            <button
              onClick={onLogout}
              className="text-red-400 hover:text-red-300 underline text-sm transition"
            >
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
