import { createContext, useContext, useEffect, useMemo, useState } from 'react'

type AuthContextType = {
  accessToken: string | null
  refreshToken: string | null
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

  const login = (access: string, refresh: string) => {
    setAccess(access); setRefresh(refresh)
    localStorage.setItem('access', access); localStorage.setItem('refresh', refresh)
  }
  const logout = () => {
    setAccess(null); setRefresh(null)
    localStorage.removeItem('access'); localStorage.removeItem('refresh')
  }

  const value = useMemo(() => ({ accessToken, refreshToken, login, logout }), [accessToken, refreshToken])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


