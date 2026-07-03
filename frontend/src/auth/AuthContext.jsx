import { createContext } from "react"

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  return children
}
