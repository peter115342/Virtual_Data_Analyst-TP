import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from "@azure/msal-react"
import { loginRequest } from "./auth/msalConfig"
import { useState } from "react"
import "./App.css";
import HomePage from "./pages/HomePage.jsx"


export default function App() {
  const { instance, accounts } = useMsal()
  const [devMode, setDevMode] = useState(false)

  const handleLogin = () => {
    instance.loginRedirect(loginRequest)
  }

  const handleLogout = () => {
    if (devMode) {
      setDevMode(false)
      return
    }
    instance.logoutRedirect()
  }

  // Dev bypass — skip Entra ID entirely
  if (devMode) {
    return <HomePage onLogout={handleLogout} userName="Dev User" />
  }

  return (
    <>
      <UnauthenticatedTemplate>
        <div className="h-screen flex flex-col items-center justify-center bg-gray-800 text-white gap-6">
          <h1 className="text-3xl font-bold">Virtual Data Analyst</h1>
          <p className="text-gray-400">Sign in with your Microsoft account to continue</p>
          <button
            onClick={handleLogin}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition"
          >
            Sign in with Microsoft
          </button>
          <button
            onClick={() => setDevMode(true)}
            className="text-gray-500 hover:text-gray-300 text-sm underline transition"
          >
            Skip auth (dev mode)
          </button>
        </div>
      </UnauthenticatedTemplate>

      <AuthenticatedTemplate>
        <HomePage onLogout={handleLogout} userName={accounts[0]?.name} />
      </AuthenticatedTemplate>
    </>
  )
}

