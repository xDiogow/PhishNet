import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  TrendingUp,
  Mail,
  FileText,
  Building2,
  Users,
  Activity,
  ArrowRight,
  Plus,
  AlertCircle
} from 'lucide-react'
import { useUser } from '../../contexts/UserContext'
import { getCampaigns } from '../../services/campaignsService'
import { getTemplates } from '../../services/templatesService'
import { getTenants } from '../../services/tenantsService'
import { formatDate } from '../../utils/dateUtils'

export default function Dashboard() {
  const { user, isAdmin } = useUser()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    campaigns: 0,
    templates: 0,
    tenants: 0,
  })
  const [recentCampaigns, setRecentCampaigns] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setError(null)
      setLoading(true)

      // Fetch campaigns (all users)
      let campaignsData = []
      try {
        campaignsData = await getCampaigns()
        setStats(prev => ({ ...prev, campaigns: campaignsData.length }))
        setRecentCampaigns(campaignsData.slice(0, 5))
      } catch (err) {
        console.log('Campaigns not available:', err)
      }

      // Fetch templates (all users)
      try {
        const templatesData = await getTemplates()
        setStats(prev => ({ ...prev, templates: templatesData.length }))
      } catch (err) {
        console.log('Templates not available:', err)
      }

      // Fetch tenants (admin only)
      if (isAdmin()) {
        try {
          const tenantsData = await getTenants()
          setStats(prev => ({ ...prev, tenants: tenantsData.length }))
        } catch (err) {
          console.log('Tenants not available:', err)
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back{user?.first_name ? `, ${user.first_name}` : ''}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's an overview of your phishing security awareness training platform.
        </p>
      </div>

      {error && (
        <div role="alert" className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <AlertCircle aria-hidden="true" className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h2 className="text-sm font-medium text-red-800">Error</h2>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Campaigns Card */}
        <Link
          to="/campaigns"
          className="group relative overflow-hidden rounded-lg bg-white p-6 shadow hover:shadow-lg transition-shadow border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Campaigns</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.campaigns}</p>
            </div>
            <div className="rounded-full bg-blue-100 p-3">
              <Mail aria-hidden="true" className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-blue-600 group-hover:text-blue-700">
            <span>View all campaigns</span>
            <ArrowRight aria-hidden="true" className="ml-1 h-4 w-4" />
          </div>
        </Link>

        {/* Templates Card */}
        <Link
          to="/templates"
          className="group relative overflow-hidden rounded-lg bg-white p-6 shadow hover:shadow-lg transition-shadow border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Templates</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.templates}</p>
            </div>
            <div className="rounded-full bg-purple-100 p-3">
              <FileText aria-hidden="true" className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-purple-600 group-hover:text-purple-700">
            <span>Browse templates</span>
            <ArrowRight aria-hidden="true" className="ml-1 h-4 w-4" />
          </div>
        </Link>

        {/* Tenants Card (Admin Only) */}
        {isAdmin() && (
          <Link
            to="/tenants"
            className="group relative overflow-hidden rounded-lg bg-white p-6 shadow hover:shadow-lg transition-shadow border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tenants</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stats.tenants}</p>
              </div>
              <div className="rounded-full bg-orange-100 p-3">
                <Building2 aria-hidden="true" className="h-6 w-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-orange-600 group-hover:text-orange-700">
              <span>View tenants</span>
              <ArrowRight aria-hidden="true" className="ml-1 h-4 w-4" />
            </div>
          </Link>
        )}

        {/* Team Card (if not admin or to fill grid) */}
        {!isAdmin() && (
          <Link
            to="/team"
            className="group relative overflow-hidden rounded-lg bg-white p-6 shadow hover:shadow-lg transition-shadow border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Team</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">—</p>
              </div>
              <div className="rounded-full bg-indigo-100 p-3">
                <Users aria-hidden="true" className="h-6 w-6 text-indigo-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-indigo-600 group-hover:text-indigo-700">
              <span>View team</span>
              <ArrowRight aria-hidden="true" className="ml-1 h-4 w-4" />
            </div>
          </Link>
        )}
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 p-6 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="text-white">
            <h2 className="text-lg font-semibold">Ready to create a new campaign?</h2>
            <p className="mt-1 text-blue-100">
              Launch a phishing simulation to test your team's awareness
            </p>
          </div>
          <Link
            to="/campaigns"
            className="flex items-center justify-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-blue-600 hover:bg-blue-50 transition-colors sm:flex-shrink-0"
          >
            <Plus aria-hidden="true" className="h-4 w-4" />
            Create Campaign
          </Link>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Campaigns */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Activity aria-hidden="true" className="h-5 w-5 text-gray-400" />
              Recent Campaigns
            </h2>
            <Link
              to="/campaigns"
              className="text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              View all
            </Link>
          </div>

          {recentCampaigns.length === 0 ? (
            <div className="text-center py-8">
              <Mail aria-hidden="true" className="mx-auto h-12 w-12 text-gray-300" />
              <p className="mt-2 text-sm text-gray-500">No campaigns yet</p>
              <Link
                to="/campaigns"
                className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                Create your first campaign
                <ArrowRight aria-hidden="true" className="h-4 w-4" />
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentCampaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {campaign.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(campaign.created_at)}
                    </p>
                  </div>
                  <span
                    className={`ml-3 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${getStatusColor(
                      campaign.status
                    )}`}
                  >
                    {campaign.status || 'Draft'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div className="rounded-lg bg-white p-6 shadow border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp aria-hidden="true" className="h-5 w-5 text-gray-400" />
            Quick Links
          </h2>

          <div className="space-y-2">
            <Link
              to="/templates"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-purple-100 p-2">
                  <FileText aria-hidden="true" className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Browse Templates</p>
                  <p className="text-xs text-gray-500">
                    View {stats.templates} available templates
                  </p>
                </div>
              </div>
              <ArrowRight aria-hidden="true" className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
            </Link>

            <Link
              to="/team"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-indigo-100 p-2">
                  <Users aria-hidden="true" className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Team Management</p>
                  <p className="text-xs text-gray-500">Manage your team members</p>
                </div>
              </div>
              <ArrowRight aria-hidden="true" className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
            </Link>

            {isAdmin() && (
              <>
                <Link
                  to="/tenants"
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-orange-100 p-2">
                      <Building2 aria-hidden="true" className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Tenant Organizations</p>
                      <p className="text-xs text-gray-500">
                        {stats.tenants} tenants configured
                      </p>
                    </div>
                  </div>
                  <ArrowRight aria-hidden="true" className="h-5 w-5 text-gray-400 group-hover:text-gray-600" />
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Info Section */}
      <div className="rounded-lg bg-blue-50 p-6 border border-blue-200">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-blue-100 p-2">
            <Activity aria-hidden="true" className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-blue-900">
              Getting Started with PhishNet
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              PhishNet helps you run phishing simulations to train your team and improve security awareness.
              Start by creating templates, setting up campaigns, and tracking your team's progress.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
