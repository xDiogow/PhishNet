import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Mail, 
  Play, 
  Search, 
  Plus, 
  Eye, 
  Pause, 
  Calendar
} from 'lucide-react'
import { getCampaigns, getCampaignSummary } from '../../services/campaignsService'
import { getTemplates } from '../../services/templatesService'
import { formatDateShort } from '../../utils/dateUtils'

function getStatusColor(status) {
  switch (status) {
    case 'running':
      return 'bg-green-100 text-green-800'
    case 'completed':
    case 'archived':
      return 'bg-purple-100 text-purple-800'
    case 'scheduled':
    case 'draft':
      return 'bg-blue-100 text-blue-800'
    case 'paused':
    case 'stopped':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function toPercent(count, total) {
  if (total === 0) return 0
  return ((count / total) * 100).toFixed(0)
}

function getStatusLabel(status) {
  switch (status) {
    case 'running':
      return 'active'
    case 'completed':
    case 'archived':
      return 'completed'
    case 'scheduled':
    case 'draft':
      return 'scheduled'
    case 'paused':
    case 'stopped':
      return 'paused'
    default:
      return status
  }
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [campaignStats, setCampaignStats] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const campaignsData = await getCampaigns()
        const templatesData = await getTemplates()
        
        setCampaigns(campaignsData || [])
        setTemplates(templatesData || [])

        const stats = []
        for (const campaign of (campaignsData || [])) {
          try {
            const data = await getCampaignSummary(campaign.id)
            const summary = data.summary || data
            summary.campaign_id = campaign.id
            stats.push(summary)
          } catch (err) {
            // ignore campaigns whose summary failed to load
          }
        }
        setCampaignStats(stats)
      } catch (error) {
        console.error('Error fetching campaigns:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Calculate statistics
  const totalCampaigns = campaigns.length
  const activeCampaigns = campaigns.filter(c => c.status === 'running').length

  // Get template name by ID
  const getTemplateName = (templateId) => {
    if (!templateId) return 'N/A'
    const template = templates.find(t => t.id === templateId)
    if (!template) return 'Unknown'
    return template.name
  }

  // Get campaign stats
  const getCampaignStats = (campaignId) => {
    return campaignStats.find(stat => stat.campaign_id === campaignId) || {}
  }

  // Filter campaigns by search query
  const filteredCampaigns = campaigns.filter(campaign => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return campaign.name.toLowerCase().includes(query) ||
           getTemplateName(campaign.template_id).toLowerCase().includes(query)
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading campaigns...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Campaigns</h1>
        <p className="text-gray-600">Manage and monitor your phishing simulation campaigns</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Campaigns</p>
              <p className="text-3xl font-bold text-gray-900">{totalCampaigns}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Now</p>
              <p className="text-3xl font-bold text-gray-900">{activeCampaigns}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Play className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and New Campaign Button */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div className="relative flex-1 sm:max-w-md">
          <Search aria-hidden="true" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <label htmlFor="campaign-search" className="sr-only">Search campaigns</label>
          <input
            id="campaign-search"
            type="text"
            placeholder="Search campaigns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <Link
          to="/campaigns/create"
          className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md font-medium transition-colors sm:flex-shrink-0"
        >
          <Plus className="w-5 h-5" />
          New Campaign
        </Link>
      </div>

      {/* Campaigns Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Campaign Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="hidden sm:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Template
                </th>
                <th className="hidden md:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Recipients
                </th>
                <th className="hidden md:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Opened
                </th>
                <th className="hidden lg:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Clicked
                </th>
                <th className="hidden lg:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Submitted Data
                </th>
                <th className="hidden sm:table-cell px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Start Date
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCampaigns.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-6 py-12 text-center text-gray-500">
                    {searchQuery ? 'No campaigns found matching your search.' : 'No campaigns yet. Create your first campaign to get started.'}
                  </td>
                </tr>
              ) : (
                filteredCampaigns.map((campaign) => {
                  const stats = getCampaignStats(campaign.id)
                  const recipients = stats.total || 0
                  const opened = stats.opened || 0
                  const clicked = stats.clicked || 0
                  const submitted = stats.submitted_data || 0

                  const openedPercent = toPercent(opened, recipients)
                  const clickedPercent = toPercent(clicked, recipients)
                  const submittedPercent = toPercent(submitted, recipients)

                  let startDate
                  if (campaign.status === 'scheduled') {
                    startDate = campaign.scheduled_start_at
                  } else if (campaign.launched_at) {
                    startDate = campaign.launched_at
                  } else {
                    startDate = campaign.created_at
                  }

                  return (
                    <tr key={campaign.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {campaign.name}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                          {getStatusLabel(campaign.status)}
                        </span>
                      </td>
                      <td className="hidden sm:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {getTemplateName(campaign.template_id)}
                        </div>
                      </td>
                      <td className="hidden md:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{recipients}</div>
                      </td>
                      <td className="hidden md:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div>{opened}</div>
                          <div className="text-xs text-gray-500">{openedPercent}%</div>
                        </div>
                      </td>
                      <td className="hidden lg:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div>{clicked}</div>
                          <div className="text-xs text-gray-500">{clickedPercent}%</div>
                        </div>
                      </td>
                      <td className="hidden lg:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div>{submitted}</div>
                          <div className="text-xs text-gray-500">{submittedPercent}%</div>
                        </div>
                      </td>
                      <td className="hidden sm:table-cell px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-1 text-sm text-gray-900">
                          <Calendar aria-hidden="true" className="w-4 h-4 text-gray-400" />
                          {formatDateShort(startDate)}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/campaigns/${campaign.id}`}
                            aria-label={`View details for ${campaign.name}`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Eye aria-hidden="true" className="w-5 h-5" />
                          </Link>
                          {campaign.status === 'running' ? (
                            <button
                              aria-label={`Pause campaign ${campaign.name}`}
                              className="text-yellow-600 hover:text-yellow-900"
                            >
                              <Pause aria-hidden="true" className="w-5 h-5" />
                            </button>
                          ) : (
                            <button
                              aria-label={`Resume campaign ${campaign.name}`}
                              className="text-green-600 hover:text-green-900"
                            >
                              <Play aria-hidden="true" className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
