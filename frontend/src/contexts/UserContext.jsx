import { createContext, useContext, useState } from 'react'
import { getAuthToken } from '../config/api'

const UserContext = createContext(null)

export const useUser = () => {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) : null
    } catch {
      localStorage.removeItem('user')
      return null
    }
  })

  const setUserData = (userData) => {
    setUser(userData)
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  const isAdmin = () => {
    return user?.is_admin === true
  }

  const isAuthenticated = () => {
    return !!getAuthToken() && !!user
  }

  return (
    <UserContext.Provider value={{ user, setUser: setUserData, isAdmin, isAuthenticated, loading: false }}>
      {children}
    </UserContext.Provider>
  )
}
