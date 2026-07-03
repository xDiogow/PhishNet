import { apiRequest } from '../config/api'

/**
 * Create a new invitation for a tenant.
 * If email is provided, the backend will also send an invitation email to that address.
 */
export const createInvitation = async (tenantId, expiresDays = null, email = null) => {
    try {
        const body = { tenant_id: tenantId, expires_days: expiresDays }
        if (email) body.email = email
        const response = await apiRequest('/tenant-invitations', {
            method: 'POST',
            body: JSON.stringify(body),
        })
        return response
    } catch (error) {
        console.error('Error creating invitation:', error)
        throw error
    }
}

/**
 * Get all invitations for a tenant.
 */
export const getInvitationsByTenant = async (tenantId, isUsed = null) => {
    try {
        const params = new URLSearchParams()
        if (isUsed !== null) {
            params.append('is_used', isUsed.toString())
        }
        const queryString = params.toString()
        let url = '/tenant-invitations/tenant/' + tenantId
        if (queryString) {
            url = url + '?' + queryString
        }
        const response = await apiRequest(url)
        return response.invitations
    } catch (error) {
        console.error('Error getting invitations:', error)
        throw error
    }
}
