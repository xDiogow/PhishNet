import { apiRequest } from '../config/api'

/**
 * Get all team members.
 */
export const getTeamMembers = async () => {
    try {
        const response = await apiRequest('/team')
        return response.team_members
    } catch (error) {
        console.error('Error getting team members:', error)
        throw error
    }
}

/**
 * Get all phishing targets.
 */
export const getTargets = async () => {
    try {
        const response = await apiRequest('/team/targets')
        return response.targets
    } catch (error) {
        console.error('Error getting phishing targets:', error)
        throw error
    }
}

/**
 * Add a new phishing target.
 */
export const addTarget = async (targetData) => {
    try {
        const response = await apiRequest('/team/targets', {
            method: 'POST',
            body: JSON.stringify(targetData)
        })
        return response
    } catch (error) {
        console.error('Error adding phishing target:', error)
        throw error
    }
}

/**
 * Delete a phishing target.
 */
export const deleteTarget = async (targetId) => {
    try {
        const response = await apiRequest(`/team/targets/${targetId}`, {
            method: 'DELETE'
        })
        return response
    } catch (error) {
        console.error('Error deleting phishing target:', error)
        throw error
    }
}

/**
 * GDPR Art. 17 erasure: anonymize campaign history then delete the target.
 */
export const gdprEraseTarget = async (targetId) => {
    try {
        const response = await apiRequest(`/team/targets/${targetId}/gdpr`, {
            method: 'DELETE'
        })
        return response
    } catch (error) {
        console.error('Error erasing target (GDPR):', error)
        throw error
    }
}
