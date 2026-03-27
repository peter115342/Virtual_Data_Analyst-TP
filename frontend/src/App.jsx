import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from "@azure/msal-react"
import { loginRequest } from "./auth/msalConfig"
import HomePage from "./pages/HomePage.jsx"


export default function App() {
  const { instance, accounts } = useMsal()

  const handleLogin = () => {
    instance.loginRedirect(loginRequest)
  }

  const handleLogout = () => {
    instance.logoutRedirect()
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
        </div>
      </UnauthenticatedTemplate>

      <AuthenticatedTemplate>
        <HomePage onLogout={handleLogout} userName={accounts[0]?.name} />
      </AuthenticatedTemplate>
    </>
  )
}

