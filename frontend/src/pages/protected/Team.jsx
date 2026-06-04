import { useEffect, useState } from 'react'
import {
  Users,
  Shield,
  UserPlus,
  Search,
  Plus,
  Trash2,
  ShieldOff,
  Copy,
  Check,
  Target as TargetIcon
} from 'lucide-react'
import { getTeamMembers, getTargets, addTarget, deleteTarget, gdprEraseTarget } from '../../services/teamService'
import { createInvitation } from '../../services/invitationsService'
import { useUser } from '../../contexts/UserContext'
import { formatDateShort } from '../../utils/dateUtils'
import { generateAvatarUrl } from '../../utils/avatarUtils'

function getRoleColor(role) {
  switch (role) {
    case 'Operator':
      return 'bg-purple-100 text-purple-800'
    case 'Admin':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getStatusColor(isActive) {
  return isActive
    ? 'bg-green-100 text-green-800'
    : 'bg-gray-100 text-gray-800'
}

export default function Team() {
  const { user } = useUser()
  const [teamMembers, setTeamMembers] = useState([])
  const [targets, setTargets] = useState([])
  const [loading, setLoading] = useState(true)
  const [memberSearch, setMemberSearch] = useState('')
  const [targetSearch, setTargetSearch] = useState('')

  // Invitation Modal State
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const [invitationCode, setInvitationCode] = useState(null)
  const [inviteLoading, setInviteLoading] = useState(false)
  const [inviteError, setInviteError] = useState(null)
  const [copiedCode, setCopiedCode] = useState(false)

  // Target Modal State
  const [isTargetModalOpen, setIsTargetModalOpen] = useState(false)
  const [targetFormData, setTargetFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    position: ''
  })
  const [targetActionLoading, setTargetActionLoading] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)

      // Fetch members and targets independently to ensure one failure doesn't block the other
      const fetchMembers = getTeamMembers().then(m => setTeamMembers(m || [])).catch(err => console.error('Error fetching members:', err));
      const fetchTargets = getTargets().then(t => setTargets(t || [])).catch(err => console.error('Error fetching targets:', err));

      await Promise.allSettled([fetchMembers, fetchTargets]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false)
    }
  }

  const handleInviteMember = async () => {
    if (!user?.tenant_id) {
      setInviteError('Unable to determine tenant. Please try again.')
      return
    }

    try {
      setInviteError(null)
      setInviteLoading(true)
      const response = await createInvitation(user.tenant_id)
      setInvitationCode(response.invitation.invitation_code)
      setIsInviteModalOpen(true)
    } catch (err) {
      const errorMessage = err.message || 'Failed to create invitation'
      setInviteError(errorMessage)
      setIsInviteModalOpen(true)
      console.error('Error creating invitation:', err)
    } finally {
      setInviteLoading(false)
    }
  }

  const handleAddTarget = async (e) => {
    e.preventDefault()
    try {
      setTargetActionLoading(true)
      await addTarget(targetFormData)
      await fetchData()
      setIsTargetModalOpen(false)
      setTargetFormData({ email: '', first_name: '', last_name: '', position: '' })
    } catch (error) {
      console.error('Error adding target:', error)
      alert(error.message || 'Failed to add target')
    } finally {
      setTargetActionLoading(false)
    }
  }

  const handleDeleteTarget = async (targetId) => {
    if (!window.confirm('Are you sure you want to remove this target? This action cannot be undone.')) {
      return
    }
    try {
      setTargetActionLoading(true)
      await deleteTarget(targetId)
      await fetchData()
    } catch (error) {
      console.error('Error deleting target:', error)
    } finally {
      setTargetActionLoading(false)
    }
  }

  const handleGdprErase = async (targetId, targetName) => {
    if (!window.confirm(
      `GDPR Erasure — ${targetName}\n\n` +
      `This will permanently anonymize all campaign history for this target (email, name, position replaced with placeholders), then delete the target record.\n\n` +
      `This action cannot be undone. Continue?`
    )) {
      return
    }
    try {
      setTargetActionLoading(true)
      await gdprEraseTarget(targetId)
      await fetchData()
    } catch (error) {
      console.error('Error erasing target (GDPR):', error)
    } finally {
      setTargetActionLoading(false)
    }
  }

  const handleCopyCode = () => {
    if (invitationCode) {
      navigator.clipboard.writeText(invitationCode)
      setCopiedCode(true)
      setTimeout(() => setCopiedCode(false), 2000)
    }
  }

  const handleCloseModal = () => {
    setIsInviteModalOpen(false)
    setInvitationCode(null)
    setInviteError(null)
    setCopiedCode(false)
  }

  // Check if current user is operator
  const isOperator = teamMembers.find(m => m.id === user?.id)?.is_operator || false

  // Statistics
  const totalMembers = teamMembers.length
  const totalTargets = targets.length
  const operators = teamMembers.filter(m => m.is_operator).length

  // Filtering
  const filteredMembers = teamMembers.filter(member => {
    const query = memberSearch.toLowerCase()
    const fullName = `${member.first_name} ${member.last_name}`.toLowerCase()
    return fullName.includes(query) || member.email.toLowerCase().includes(query)
  })

  const filteredTargets = targets.filter(target => {
    const query = targetSearch.toLowerCase()
    const fullName = `${target.first_name} ${target.last_name}`.toLowerCase()
    return fullName.includes(query) || target.email.toLowerCase().includes(query)
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading team data...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Team & Targets</h1>
        <p className="text-gray-600">Manage your platform operators and phishing targets in one place.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Team Members</p>
              <p className="text-3xl font-bold text-gray-900">{totalMembers}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Phishing Targets</p>
              <p className="text-3xl font-bold text-gray-900">{totalTargets}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <TargetIcon className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-indigo-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Operators</p>
              <p className="text-3xl font-bold text-gray-900">{operators}</p>
            </div>
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Shield className="w-8 h-8 text-indigo-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Section: Team Members */}
      <section className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-500" />
            Team Members
          </h2>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative">
              <Search aria-hidden="true" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <label htmlFor="member-search" className="sr-only">Search team members</label>
              <input
                id="member-search"
                type="text"
                placeholder="Search members..."
                value={memberSearch}
                onChange={(e) => setMemberSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {isOperator && (
              <button
                onClick={handleInviteMember}
                disabled={inviteLoading}
                className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                <UserPlus aria-hidden="true" className="w-4 h-4" />
                Invite Member
              </button>
            )}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase text-right">Joined</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMembers.length === 0 ? (
                <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-500">No members found.</td></tr>
              ) : (
                filteredMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <img
                          src={generateAvatarUrl(member.first_name, member.last_name, member.email)}
                          alt="" className="w-8 h-8 rounded-full mr-3"
                        />
                        <span className="font-medium text-gray-900">{member.first_name} {member.last_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{member.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRoleColor(member.role)}`}>
                        {member.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(member.is_active)}`}>
                        {member.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-gray-500 text-sm">
                      {formatDateShort(member.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section: Phishing Targets */}
      <section className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <TargetIcon className="w-5 h-5 text-purple-500" />
            Phishing Targets
          </h2>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative">
              <Search aria-hidden="true" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <label htmlFor="target-search" className="sr-only">Search phishing targets</label>
              <input
                id="target-search"
                type="text"
                placeholder="Search targets..."
                value={targetSearch}
                onChange={(e) => setTargetSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <button
              onClick={() => setIsTargetModalOpen(true)}
              className="flex items-center justify-center gap-2 bg-purple-500 hover:bg-purple-600 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            >
              <Plus aria-hidden="true" className="w-4 h-4" />
              Add Target
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Position</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTargets.length === 0 ? (
                <tr><td colSpan="4" className="px-6 py-8 text-center text-gray-500">No phishing targets found.</td></tr>
              ) : (
                filteredTargets.map((target) => (
                  <tr key={target.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900 text-sm">
                      {target.first_name} {target.last_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{target.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{target.position || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => handleGdprErase(target.id, `${target.first_name} ${target.last_name}`)}
                          disabled={targetActionLoading}
                          aria-label={`GDPR erase target ${target.first_name} ${target.last_name}`}
                          title="GDPR erasure — anonymize history and delete"
                          className="text-amber-500 hover:text-amber-700 transition-colors disabled:opacity-50"
                        >
                          <ShieldOff aria-hidden="true" className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteTarget(target.id)}
                          disabled={targetActionLoading}
                          aria-label={`Remove target ${target.first_name} ${target.last_name}`}
                          title="Delete target (campaign history preserved)"
                          className="text-red-500 hover:text-red-700 transition-colors disabled:opacity-50"
                        >
                          <Trash2 aria-hidden="true" className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Target Modal */}
      {isTargetModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-target-title"
            className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
          >
            <h2 id="add-target-title" className="text-xl font-bold mb-4">Add Phishing Target</h2>
            <form onSubmit={handleAddTarget} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="target-first-name" className="block text-sm font-medium text-gray-700">First Name</label>
                  <input
                    id="target-first-name"
                    type="text"
                    required
                    aria-required="true"
                    value={targetFormData.first_name}
                    onChange={(e) => setTargetFormData({...targetFormData, first_name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="target-last-name" className="block text-sm font-medium text-gray-700">Last Name</label>
                  <input
                    id="target-last-name"
                    type="text"
                    required
                    aria-required="true"
                    value={targetFormData.last_name}
                    onChange={(e) => setTargetFormData({...targetFormData, last_name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="target-email" className="block text-sm font-medium text-gray-700">Email Address</label>
                <input
                  id="target-email"
                  type="email"
                  required
                  aria-required="true"
                  value={targetFormData.email}
                  onChange={(e) => setTargetFormData({...targetFormData, email: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label htmlFor="target-position" className="block text-sm font-medium text-gray-700">Position / Title (Optional)</label>
                <input
                  id="target-position"
                  type="text"
                  value={targetFormData.position}
                  onChange={(e) => setTargetFormData({...targetFormData, position: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsTargetModalOpen(false)}
                  className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={targetActionLoading}
                  className="px-4 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                  {targetActionLoading ? 'Saving...' : 'Add Target'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Invitation Modal */}
      {isInviteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="invitation-modal-title"
            className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 id="invitation-modal-title" className="text-xl font-bold">Invitation Code</h2>
              <button
                onClick={handleCloseModal}
                aria-label="Close invitation modal"
                className="text-gray-400 hover:text-gray-600"
              >
                &times;
              </button>
            </div>
            {inviteError ? (
              <div role="alert" className="p-3 bg-red-50 text-red-700 rounded border border-red-200 text-sm">{inviteError}</div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">Share this code with your new operator.</p>
                <div className="flex items-center gap-2">
                  <div
                    className="flex-1 bg-gray-50 border rounded px-4 py-3 font-mono text-lg font-bold"
                    aria-label={`Invitation code: ${invitationCode}`}
                  >
                    {invitationCode}
                  </div>
                  <button
                    onClick={handleCopyCode}
                    aria-label={copiedCode ? 'Code copied' : 'Copy invitation code'}
                    className="p-3 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    {copiedCode
                      ? <Check aria-hidden="true" className="w-5 h-5" />
                      : <Copy aria-hidden="true" className="w-5 h-5" />
                    }
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
