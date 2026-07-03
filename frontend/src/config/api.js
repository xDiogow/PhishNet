const API_URL = import.meta.env.VITE_API_URL || "/api"

export const apiRequest = async (endpoint, options = {}) => {
    const config = {
        ...options,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config)

        if (response.status === 401) {
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
            throw new Error('Unauthorized. Please login again.')
        }

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.message || 'An error occurred')
        }

        return await response.json()
    } catch (error) {
        throw new Error(error.message || 'An error occurred')
    }
}

export default { API_URL, apiRequest }
