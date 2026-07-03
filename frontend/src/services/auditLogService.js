import { apiRequest } from '../config/api'

export const getAuditLogs = async (params = {}) => {
    const query = new URLSearchParams()
    if (params.page !== undefined) query.append('page', params.page)
    if (params.per_page !== undefined) query.append('per_page', params.per_page)
    if (params.action !== undefined) query.append('action', params.action)
    const queryString = query.toString()

    let url = '/audit-logs'
    if (queryString) {
        url = `/audit-logs?${queryString}`
    }
    return apiRequest(url)
}

export const exportAuditLogs = async (params = {}) => {
    const API_URL = import.meta.env.VITE_API_URL || '/api'
    const query = new URLSearchParams()
    if (params.action !== undefined) query.append('action', params.action)
    const queryString = query.toString()

    let url = `${API_URL}/audit-logs/export`
    if (queryString) {
        url = `${API_URL}/audit-logs/export?${queryString}`
    }

    const response = await fetch(url, { credentials: 'include' })
    if (!response.ok) throw new Error('Export failed')

    // ISO format is "YYYY-MM-DDTHH:MM:SS.mmmZ" — split('T')[0] gives just the date part
    const todayIso = new Date().toISOString()
    const todayDate = todayIso.split('T')[0]

    // Trigger a file download in the browser without navigating away from the page
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.setAttribute('download', `audit_logs_${todayDate}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(link.href)
}

export const auditLogAPI = {
    getLogs: getAuditLogs,
    exportLogs: exportAuditLogs,
}

export default auditLogAPI
