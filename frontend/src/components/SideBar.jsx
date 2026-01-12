import { useState } from "react";
import ButtonDatabase from "./ButtonDatabase.jsx"
import crossWhite from '../assets/cross-white.svg'
import crossGray from '../assets/cross-gray.svg'
import filterWhite from "../assets/filter-white.svg";
import filterGray from "../assets/filter-gray.svg";

export default function SideBar({ isOpen, toggle }) {
  return (
    <div className="h-full p-2 flex flex-col justify-between">
      <div
        className={`flex ${
          isOpen ? "justify-end" : "justify-center"
        }`}
      >
        <button
            onClick={toggle}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-700 transition"
            >
            <img
                src={isOpen ? crossWhite : filterWhite}
                alt=""
                className={isOpen ? "w-3" : "w-5"}
            />
        </button>

      </div>
      {isOpen && (
        <div className="text-white mt-4 flex justify-center">
          <ButtonDatabase />
        </div>
      )}
    </div>
  );
}
