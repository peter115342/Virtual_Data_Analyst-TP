import { useState } from "react"
import InputDatabase from "./InputDatabase"
import crossOrange from "../assets/cross-orange.svg"
import arrowOrange from "../assets/triangle-down-orange.svg"

export default function DatabaseModal({
  onClose,
  onConnected,
  connect,
  loading,
  error,
  prefillData,
}) {
  const [host, setHost] = useState(prefillData?.db_host || "")
  const [port, setPort] = useState(prefillData?.db_port || "")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [dbName, setDbName] = useState(prefillData?.db_name || "")
  const [dbType, setDbType] = useState(prefillData?.db_type || "postgres")
  
  const [validationError, setValidationError] = useState("")
  
  const [hasSubmitted, setHasSubmitted] = useState(false) 

  const handleConnect = async () => {
    setHasSubmitted(true) // Zaznamenáme pokus o pripojenie
    setValidationError("") 

    // 1. empty fields
    if (!host || !port || !username || !password || !dbName) {
      setValidationError("All fields are required.")
      return
    }

    // 2. validation of port number
    if (!/^\d+$/.test(port)) {
      setValidationError("Port must contain only digits (0-9).")
      return
    }

    const portNum = Number(port)
    if (portNum < 1 || portNum > 65535) {
      setValidationError("Port must be between 1 and 65535.")
      return
    }

    // 3. validation of max length
    if (host.length > 253) {
      setValidationError("Host can have a maximum of 253 characters.")
      return
    }
    if (username.length > 128) {
      setValidationError("Username can have a maximum of 128 characters.")
      return
    }
    if (password.length > 256) {
      setValidationError("Password can have a maximum of 256 characters.")
      return
    }
    if (dbName.length > 128) {
      setValidationError("Database name can have a maximum of 128 characters.")
      return
    }

    // 4. validation of allowed characters 
    const hostRegex = /^[a-zA-Z0-9.\-_[\]:]+$/;
    const userRegex = /^[a-zA-Z0-9.\-_@]+$/;     
    const dbNameRegex = /^[a-zA-Z0-9.\-_]+$/;

    if (!hostRegex.test(host)) {
      setValidationError("Host contains invalid characters.");
      return;
    }
    if (!userRegex.test(username)) {
      setValidationError("Username contains invalid characters.");
      return;
    }
    if (!dbNameRegex.test(dbName)) {
      setValidationError("Database name contains invalid characters.");
      return;
    }

    try {
      const result = await connect({
        db_type: dbType,
        host,
        port: Number(port),
        username,
        password,
        db_name: dbName,
      })

      onConnected(result)
      onClose()
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleConnect()
        }}
        className="bg-[#eeeeee] p-6 rounded-xl w-full max-w-md relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full hover:brightness-85"
        >
          <img src={crossOrange} alt="Close" className="w-6" />
        </button>

        <h2 className="text-[#F9730B] text-xl mb-2">
          Connect Database
        </h2>

        <div className="flex flex-col gap-4">
          <div className="relative w-full mt-5">
            <select
              value={dbType}
              onChange={(e) => setDbType(e.target.value)}
              className="
                w-full
                bg-[#eeeeee]
                text-gray-700
                border border-gray-300
                rounded-lg
                pl-5 pr-4 py-2
                focus:outline-none focus:border-[#F9730B]
                appearance-none
              "
            >
              <option value="postgres">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="oracle">OracleDB</option>
              <option value="sqlserver">SQL Server</option>
            </select>

            <img
              src={arrowOrange}
              alt=""
              className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-3 pointer-events-none"
            />
          </div>

          <InputDatabase value={host} onChange={setHost} placeholder="Database Host" />
          <InputDatabase value={port} onChange={setPort} placeholder="Database Port" />
          <InputDatabase value={username} onChange={setUsername} placeholder="Username" />
          <InputDatabase value={password} onChange={setPassword} placeholder="Password" type="password" />
          <InputDatabase value={dbName} onChange={setDbName} placeholder="Database Name" />

          {(validationError || (hasSubmitted && error)) && (
            <p className="text-red-400 text-sm text-center">
              {validationError || error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`bg-[#F9730B] rounded-full py-3 text-white font-semibold hover:bg-[#E66400] transition
              ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {loading ? "Connecting..." : "Connect"}
          </button>
        </div>
      </form>
    </div>
  )
}