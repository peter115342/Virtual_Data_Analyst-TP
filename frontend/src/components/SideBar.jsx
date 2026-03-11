// SideBar.jsx
import ButtonDatabase from "./ButtonDatabase.jsx";
import crossWhite from '../assets/cross-white.svg';
import filterWhite from "../assets/filter-white.svg";

export default function SideBar({ isOpenS, toggle, onOpenDatabase, isConnected }) {
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
        <div className="text-white mt-4 flex justify-center">
          <ButtonDatabase
            onClick={onOpenDatabase}
            label={isConnected ? "Disconnect Database" : "Connect Database"}
            isConnected={isConnected}
          />
        </div>
      )}
    </div>
  );
}
