import { useEffect, useState } from 'react'
import {
  Search,
  User,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Info,
  ShieldAlert,
  Download
} from 'lucide-react'
import { auditLogAPI } from '../../services/auditLogService'

export default function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalLogs, setTotalLogs] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  const [exporting, setExporting] = useState(false)

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const data = await auditLogAPI.getLogs({
        page,
        per_page: 20,
        action: actionFilter || undefined
      })

      setLogs(data.logs || [])
      setTotalPages(data.total_pages || 1)
      setTotalLogs(data.total || 0)
    } catch (error) {
      console.error('Error fetching audit logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      setExporting(true)
      await auditLogAPI.exportLogs({
        action: actionFilter || undefined
      })
    } catch (error) {
      console.error('Error exporting audit logs:', error)
      alert('Failed to export audit logs. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [page, actionFilter])

  const getActionColor = (action) => {
    switch (action) {
      case 'LOGIN':
        return 'bg-blue-100 text-blue-800'
      case 'CREATE_CAMPAIGN':
        return 'bg-green-100 text-green-800'
      case 'DELETE_CAMPAIGN':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading && logs.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading audit logs...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Audit Logs</h1>
        <p className="text-gray-600">Track and monitor all user and system actions within your tenant</p>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex flex-col sm:flex-row flex-1 items-stretch sm:items-center gap-3">
          <div className="relative flex-1 sm:max-w-md">
            <Search aria-hidden="true" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <label htmlFor="audit-search" className="sr-only">Search audit logs</label>
            <input
              id="audit-search"
              type="text"
              placeholder="Search in logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <label htmlFor="audit-action-filter" className="sr-only">Filter by action</label>
          <select
            id="audit-action-filter"
            value={actionFilter}
            onChange={(e) => {
              setActionFilter(e.target.value)
              setPage(1)
            }}
            className="border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Actions</option>
            <option value="LOGIN">Login</option>
            <option value="CREATE_CAMPAIGN">Create Campaign</option>
          </select>
          <button
            onClick={handleExport}
            disabled={exporting || logs.length === 0}
            className="flex items-center justify-center gap-2 bg-white border border-gray-300 rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download aria-hidden="true" className={`w-4 h-4 ${exporting ? 'animate-bounce' : ''}`} />
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
        </div>
        <div className="text-sm text-gray-500">
          Showing <span className="font-medium text-gray-900">{logs.length}</span> of <span className="font-medium text-gray-900">{totalLogs}</span> logs
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    No audit logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center gap-2">
                        <Calendar aria-hidden="true" className="w-4 h-4 text-gray-400" />
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                          <User className="w-4 h-4 text-gray-500" />
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">{log.user_name}</div>
                          <div className="text-xs text-gray-500">{log.user_email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                        {log.action.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.resource_type ? (
                        <div className="flex items-center gap-1">
                          <ShieldAlert aria-hidden="true" className="w-4 h-4 text-gray-400" />
                          <span>{log.resource_type} #{log.resource_id}</span>
                        </div>
                      ) : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs">
                      <div className="flex items-center gap-1">
                        <Info aria-hidden="true" className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <span>{log.details}</span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing page <span className="font-medium">{page}</span> of <span className="font-medium">{totalPages}</span>
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    <span className="sr-only">Previous</span>
                    <ChevronLeft className="h-5 w-5" aria-hidden="true" />
                  </button>
                  {[...Array(totalPages).keys()].map(i => (
                    <button
                      key={i + 1}
                      onClick={() => setPage(i + 1)}
                      aria-current={page === i + 1 ? 'page' : undefined}
                      aria-label={`Page ${i + 1}`}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === i + 1
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    <span className="sr-only">Next</span>
                    <ChevronRight className="h-5 w-5" aria-hidden="true" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
