import { Link, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function AppLayout() {
  const { logout } = useAuth()
  return (
    <div className="min-h-screen grid grid-rows-[auto,1fr]">
      <header className="border-b p-3 flex gap-4 items-center">
        <div className="font-semibold">MauEyeCare</div>
        <nav className="flex gap-3 text-sm">
          <Link to="/">Dashboard</Link>
          <Link to="/patients">Patients</Link>
          <Link to="/visits/new">New Visit</Link>
          <Link to="/prescriptions">Prescriptions</Link>
          <Link to="/marketing">Marketing</Link>
          <Link to="/operations">Operations</Link>
          <Link to="/insights">Insights</Link>
          <Link to="/settings">Settings</Link>
        </nav>
        <div className="ml-auto">
          <button className="text-sm" onClick={logout}>Logout</button>
        </div>
      </header>
      <main className="p-4"><Outlet /></main>
    </div>
  )
}

