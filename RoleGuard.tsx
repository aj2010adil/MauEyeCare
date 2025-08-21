import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function RoleGuard({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const { accessToken, user } = useAuth()
  const loc = useLocation()

  if (!accessToken) return <Navigate to="/login" replace state={{ from: loc }} />
  if (!user) return null // Optionally a spinner while /me loads
  if (roles.length && !roles.includes(user.role)) return <Navigate to="/" replace />

  return <>{children}</>
}
