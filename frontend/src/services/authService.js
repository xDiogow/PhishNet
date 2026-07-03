import { apiRequest } from '../config/api'

export const login = async (credentials) => {
    return apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
    })
}

export const register = async (userData) => {
    return apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
    })
}

export const logout = async () => {
    await apiRequest('/auth/logout', { method: 'POST' })
}
