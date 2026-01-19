import { useState } from "react";
import InputDatabase from "./InputDatabase";
import crossGray from "../assets/cross-gray.svg";
import useDatabase from "../hooks/useDatabase";

export default function DatabaseModal({ onClose, onConnected }) {
  const { connect, loading, error } = useDatabase();

  const [host, setHost] = useState("");
  const [port, setPort] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [dbName, setDbName] = useState("");

  const handleConnect = async () => {
    await connect({
      host,
      port: Number(port),
      username,
      password,
      db_name: dbName,
    });
    onConnected();
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-gray-800 p-6 rounded-xl w-full max-w-md relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-700"
        >
          <img src={crossGray} alt="Close" className="w-4" />
        </button>

        <h2 className="text-white text-xl font-semibold mb-4">
          Connect Database
        </h2>

        <div className="flex flex-col gap-4">
          <InputDatabase value={host} onChange={setHost} placeholder="Database Host" />
          <InputDatabase value={port} onChange={setPort} placeholder="Database Port" />
          <InputDatabase value={username} onChange={setUsername} placeholder="Username" />
          <InputDatabase value={password} onChange={setPassword} placeholder="Password" type="password" />
          <InputDatabase value={dbName} onChange={setDbName} placeholder="Database Name" />

          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}

          <button
            onClick={handleConnect}
            disabled={loading}
            className={`bg-orange-900 rounded-full py-3 text-white font-semibold hover:bg-orange-800 transition
              ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {loading ? "Connecting..." : "Connect"}
          </button>
        </div>
      </div>
    </div>
  );
}

