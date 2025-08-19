import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuth()
  const loc = useLocation()
  if (!accessToken) return <Navigate to="/login" replace state={{ from: loc }} />
  return <>{children}</>
}


