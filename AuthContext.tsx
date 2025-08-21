import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { apiGet } from './api'

type UserProfile = {
  id: number
  email: string
  full_name?: string | null
  role: 'admin' | 'doctor' | 'staff' | string
}

type AuthContextType = {
  accessToken: string | null
  refreshToken: string | null
  user: UserProfile | null
  login: (access: string, refresh: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccess] = useState<string | null>(localStorage.getItem('access'))
  const [refreshToken, setRefresh] = useState<string | null>(localStorage.getItem('refresh'))
  const [user, setUser] = useState<UserProfile | null>(null)

  // Fetch current user when token changes
  useEffect(() => {
    let cancelled = false
    async function fetchMe() {
      if (!accessToken) { setUser(null); return }
      try {
        const me = await apiGet<UserProfile>('/api/auth/me', accessToken)
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) setUser(null)
      }
    }
    fetchMe()
    return () => { cancelled = true }
  }, [accessToken])

  const login = (access: string, refresh: string) => {
    setAccess(access); setRefresh(refresh)
    localStorage.setItem('access', access); localStorage.setItem('refresh', refresh)
  }
  const logout = () => {
    setAccess(null); setRefresh(null); setUser(null)
    localStorage.removeItem('access'); localStorage.removeItem('refresh')
  }

  const value = useMemo(() => ({ accessToken, refreshToken, user, login, logout }), [accessToken, refreshToken, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


