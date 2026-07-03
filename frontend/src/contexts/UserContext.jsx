import { createContext, useContext, useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || "/api"

const UserContext = createContext(null)

export const useUser = () => {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await fetch(`${API_URL}/auth/me`, { credentials: 'include' })
        if (response.ok) {
          const data = await response.json()
          setUser(data.user || null)
        } else {
          setUser(null)
        }
      } catch (error) {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    fetchCurrentUser()
  }, [])

  const setUserData = (userData) => {
    setUser(userData)
  }

  const isAdmin = () => {
    if (!user) return false
    return user.is_admin === true
  }

  const hasPermission = (permission) => {
    if (!user) return false
    if (user.is_admin) return true
    return Array.isArray(user.permissions) && user.permissions.includes(permission)
  }

  const isAuthenticated = () => {
    return user !== null
  }

  return (
    <UserContext.Provider value={{ user, setUser: setUserData, isAdmin, hasPermission, isAuthenticated, loading }}>
      {children}
    </UserContext.Provider>
  )
}
