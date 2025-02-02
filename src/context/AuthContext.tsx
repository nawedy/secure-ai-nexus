import React, { createContext, useContext, useState, ReactNode } from 'react'

interface AuthContextType {
  user: string | null
  role: string | null
  login: (user: string, role: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<string | null>(null)
  const [role, setRole] = useState<string | null>(null)

  const login = (user: string, role: string) => {
    setUser(user)
    setRole(role)
  }
  const logout = () => {
    setUser(null)
    setRole(null)
  }

  return (
    <AuthContext.Provider value={{ user, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
