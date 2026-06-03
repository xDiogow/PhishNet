import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Calendar,
  Mail,
  Users,
  MousePointerClick,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Activity,
  TrendingUp,
  Eye,
  Send
} from 'lucide-react'
import Button from '../../components/Button'
import { getCampaign, getCampaignSummary } from '../../services/campaignsService'
import { formatDate } from '../../utils/dateUtils'

export default function ViewCampaign() {
  const { id } = useParams()
  const [campaign, setCampaign] = useState(null)
  const [summary, setSummary] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        setLoading(true)
        const data = await getCampaign(id)
        setCampaign(data)
      } catch (err) {
        setError(err.message || 'Failed to load campaign')
        console.error('Error fetching campaign:', err)
      } finally {
        setLoading(false)
      }
    }

    const fetchSummary = async () => {
      try {
        setLoadingSummary(true)
        const data = await getCampaignSummary(id)
        setSummary(data.summary || null)
        setResults(data.results || [])
      } catch (err) {
        console.error('Error fetching campaign summary:', err)
        // Don't set error state for summary failures, just log it
      } finally {
        setLoadingSummary(false)
      }
    }

    if (id) {
      fetchCampaign()
      fetchSummary()
    }
  }, [id])

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'running':
      case 'in progress':
        return 'bg-green-50 text-green-700 ring-green-600/20'
      case 'completed':
        return 'bg-blue-50 text-blue-700 ring-blue-600/20'
      case 'draft':
        return 'bg-gray-50 text-gray-600 ring-gray-500/10'
      case 'stopped':
      case 'archived':
        return 'bg-yellow-50 text-yellow-700 ring-yellow-600/20'
      default:
        return 'bg-gray-50 text-gray-600 ring-gray-500/10'
    }
  }

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'running':
      case 'in progress':
        return <Activity aria-hidden="true" className="h-4 w-4" />
      case 'completed':
        return <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
      case 'stopped':
      case 'archived':
        return <AlertTriangle aria-hidden="true" className="h-4 w-4" />
      default:
        return <FileText aria-hidden="true" className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-500">Loading campaign...</div>
      </div>
    )
  }

  if (error || !campaign) {
    return (
      <div className="space-y-4">
        <Link
          to="/campaigns"
          className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Back to Campaigns
        </Link>
        <div role="alert" className="rounded-lg bg-red-50 p-6 border border-red-200">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
          <p className="text-red-700">{error || 'Campaign not found'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/campaigns"
          className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Back to Campaigns
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{campaign.name}</h1>
            <div className="flex items-center gap-2 mt-2">
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ring-1 ring-inset ${getStatusColor(
                  campaign.status
                )}`}
              >
                {getStatusIcon(campaign.status)}
                {campaign.status?.charAt(0).toUpperCase() + campaign.status?.slice(1)}
              </span>
              <span className="text-sm text-gray-500">
                ID: {campaign.id}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Stats Grid */}
      {!loadingSummary && summary && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Total Recipients */}
          {typeof summary.total !== 'undefined' && (
            <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Recipients</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{summary.total}</p>
                </div>
                <div className="rounded-full bg-blue-100 p-3">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>
          )}

          {/* Emails Opened */}
          {typeof summary.opened !== 'undefined' && (
            <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Emails Opened</p>
                  <p className="mt-2 text-3xl font-bold text-green-600">{summary.opened}</p>
                  {summary.total > 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      {((summary.opened / summary.total) * 100).toFixed(1)}% open rate
                    </p>
                  )}
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <Eye className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>
          )}

          {/* Links Clicked */}
          {typeof summary.clicked !== 'undefined' && (
            <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Links Clicked</p>
                  <p className="mt-2 text-3xl font-bold text-yellow-600">{summary.clicked}</p>
                  {summary.total > 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      {((summary.clicked / summary.total) * 100).toFixed(1)}% click rate
                    </p>
                  )}
                </div>
                <div className="rounded-full bg-yellow-100 p-3">
                  <MousePointerClick className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
            </div>
          )}

          {/* Data Submitted */}
          {typeof summary.submitted_data !== 'undefined' && (
            <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Submitted Data</p>
                  <p className="mt-2 text-3xl font-bold text-red-600">{summary.submitted_data}</p>
                  {summary.total > 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      {((summary.submitted_data / summary.total) * 100).toFixed(1)}% submission rate
                    </p>
                  )}
                </div>
                <div className="rounded-full bg-red-100 p-3">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {loadingSummary && (
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="text-center text-gray-500">Loading campaign statistics...</div>
        </div>
      )}

      {/* Campaign Details */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Overview Card */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FileText aria-hidden="true" className="h-5 w-5 text-gray-400" />
            Campaign Overview
          </h2>
          <dl className="space-y-4">
            <div className="flex justify-between items-start">
              <dt className="text-sm font-medium text-gray-500">Campaign ID</dt>
              <dd className="text-sm text-gray-900 font-mono">{campaign.id}</dd>
            </div>
            {campaign.template_id && (
              <div className="flex justify-between items-start">
                <dt className="text-sm font-medium text-gray-500">Template ID</dt>
                <dd className="text-sm text-gray-900 font-mono">{campaign.template_id}</dd>
              </div>
            )}
            {campaign.tenant_id && (
              <div className="flex justify-between items-start">
                <dt className="text-sm font-medium text-gray-500">Tenant ID</dt>
                <dd className="text-sm text-gray-900 font-mono">{campaign.tenant_id}</dd>
              </div>
            )}
            <div className="flex justify-between items-start">
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd>
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${getStatusColor(
                    campaign.status
                  )}`}
                >
                  {getStatusIcon(campaign.status)}
                  {campaign.status?.charAt(0).toUpperCase() + campaign.status?.slice(1)}
                </span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Timeline Card */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Calendar aria-hidden="true" className="h-5 w-5 text-gray-400" />
            Timeline
          </h2>
          <dl className="space-y-4">
            <div className="flex justify-between items-start">
              <dt className="text-sm font-medium text-gray-500 flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                Created
              </dt>
              <dd className="text-sm text-gray-900">
                {campaign.created_at ? formatDate(campaign.created_at) : 'N/A'}
              </dd>
            </div>
            <div className="flex justify-between items-start">
              <dt className="text-sm font-medium text-gray-500 flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${campaign.launched_at ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                Launched
              </dt>
              <dd className="text-sm text-gray-900">
                {campaign.launched_at ? formatDate(campaign.launched_at) : 'Not launched'}
              </dd>
            </div>
            <div className="flex justify-between items-start">
              <dt className="text-sm font-medium text-gray-500 flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${campaign.stopped_at ? 'bg-red-500' : 'bg-gray-300'}`}></div>
                Stopped
              </dt>
              <dd className="text-sm text-gray-900">
                {campaign.stopped_at ? formatDate(campaign.stopped_at) : 'Still active'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Additional Statistics */}
      {!loadingSummary && summary && (
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp aria-hidden="true" className="h-5 w-5 text-gray-400" />
            Detailed Statistics
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {typeof summary.sent !== 'undefined' && (
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="flex items-center gap-2 mb-1">
                  <Send aria-hidden="true" className="h-4 w-4 text-blue-500" />
                  <dt className="text-sm font-medium text-gray-600">Emails Sent</dt>
                </div>
                <dd className="text-2xl font-bold text-gray-900">{summary.sent}</dd>
                {summary.total > 0 && (
                  <dd className="text-xs text-gray-500 mt-1">
                    {((summary.sent / summary.total) * 100).toFixed(1)}% delivery rate
                  </dd>
                )}
              </div>
            )}
            {typeof summary.email_reported !== 'undefined' && (
              <div className="border-l-4 border-orange-500 pl-4">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle aria-hidden="true" className="h-4 w-4 text-orange-500" />
                  <dt className="text-sm font-medium text-gray-600">Emails Reported</dt>
                </div>
                <dd className="text-2xl font-bold text-gray-900">{summary.email_reported}</dd>
                {summary.total > 0 && (
                  <dd className="text-xs text-gray-500 mt-1">
                    {((summary.email_reported / summary.total) * 100).toFixed(1)}% reported
                  </dd>
                )}
              </div>
            )}
            {typeof summary.error !== 'undefined' && (
              <div className="border-l-4 border-red-500 pl-4">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle aria-hidden="true" className="h-4 w-4 text-red-500" />
                  <dt className="text-sm font-medium text-gray-600">Errors</dt>
                </div>
                <dd className="text-2xl font-bold text-gray-900">{summary.error}</dd>
              </div>
            )}
          </div>
        </div>
      )}

      {!loadingSummary && !summary && (
        <div className="rounded-lg bg-gray-50 p-6 border border-gray-200">
          <div className="text-center text-gray-500">
            <Activity aria-hidden="true" className="mx-auto h-12 w-12 text-gray-300 mb-2" />
            <p>No campaign statistics available yet</p>
            <p className="text-sm mt-1">Statistics will appear once the campaign starts collecting data</p>
          </div>
        </div>
      )}

      {/* Results Table */}
      {!loadingSummary && results.length > 0 && (
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Users aria-hidden="true" className="h-5 w-5 text-gray-400" />
            Campaign Results ({results.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((result) => (
                  <tr key={result.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {result.first_name} {result.last_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {result.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          result.status === 'Submitted Data'
                            ? 'bg-red-100 text-red-800'
                            : result.status === 'Error'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {result.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
