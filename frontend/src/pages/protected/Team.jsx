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
  Mail,
  Clock,
  Settings,
  Target as TargetIcon,
} from 'lucide-react'
import { getTeamMembers, getTargets, addTarget, deleteTarget, gdprEraseTarget, setMemberPermissions } from '../../services/teamService'
import { createInvitation, getInvitationsByTenant } from '../../services/invitationsService'
import { useUser } from '../../contexts/UserContext'
import { formatDateShort } from '../../utils/dateUtils'
import { generateAvatarUrl } from '../../utils/avatarUtils'

const ALL_PERMISSIONS = ['manage_campaigns', 'manage_templates', 'manage_targets', 'manage_team']

const PERMISSION_LABELS = {
  manage_campaigns: 'Campaigns',
  manage_templates: 'Templates',
  manage_targets: 'Targets',
  manage_team: 'Team',
}

function PermissionBadge({ permission }) {
  return (
    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-indigo-50 text-indigo-700">
      {PERMISSION_LABELS[permission] || permission}
    </span>
  )
}

export default function Team() {
  const { user, hasPermission } = useUser()
  const [teamMembers, setTeamMembers] = useState([])
  const [pendingInvitations, setPendingInvitations] = useState([])
  const [targets, setTargets] = useState([])
  const [loading, setLoading] = useState(true)
  const [memberSearch, setMemberSearch] = useState('')
  const [targetSearch, setTargetSearch] = useState('')

  // Invite modal
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)
  const [inviteTab, setInviteTab] = useState('quick')
  const [invitationCode, setInvitationCode] = useState(null)
  const [quickLoading, setQuickLoading] = useState(false)
  const [quickError, setQuickError] = useState(null)
  const [copiedCode, setCopiedCode] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [emailLoading, setEmailLoading] = useState(false)
  const [emailError, setEmailError] = useState(null)
  const [emailSent, setEmailSent] = useState(false)

  // Permissions modal
  const [permMember, setPermMember] = useState(null)
  const [permSelection, setPermSelection] = useState([])
  const [permSaving, setPermSaving] = useState(false)
  const [permError, setPermError] = useState(null)

  // Target modal
  const [isTargetModalOpen, setIsTargetModalOpen] = useState(false)
  const [targetFormData, setTargetFormData] = useState({ email: '', first_name: '', last_name: '', position: '' })
  const [targetActionLoading, setTargetActionLoading] = useState(false)

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const members = await getTeamMembers()
      setTeamMembers(members || [])
    } catch (err) {
      console.error(err)
    }
    try {
      const targets = await getTargets()
      setTargets(targets || [])
    } catch (err) {
      console.error(err)
    }
    if (user && user.tenant_id) {
      try {
        const invs = await getInvitationsByTenant(user.tenant_id, false)
        const pending = (invs || []).filter(i => i.email && i.is_valid)
        setPendingInvitations(pending)
      } catch (err) {
        // ignore errors for pending invitations
      }
    }
    setLoading(false)
  }

  // ── Invite modal ──────────────────────────────────────────────────────────

  const openInviteModal = () => {
    setInviteTab('quick')
    setInvitationCode(null)
    setQuickError(null)
    setCopiedCode(false)
    setInviteEmail('')
    setEmailError(null)
    setEmailSent(false)
    setIsInviteModalOpen(true)
  }

  const handleCloseInviteModal = async () => {
    setIsInviteModalOpen(false)
    if (user && user.tenant_id) {
      try {
        const invs = await getInvitationsByTenant(user.tenant_id, false)
        const pending = (invs || []).filter(i => i.email && i.is_valid)
        setPendingInvitations(pending)
      } catch (err) {
        // ignore errors
      }
    }
  }

  const handleGenerateCode = async () => {
    try {
      setQuickError(null)
      setQuickLoading(true)
      const res = await createInvitation(user.tenant_id)
      setInvitationCode(res.invitation.invitation_code)
    } catch (err) {
      setQuickError(err.message || 'Failed to generate code')
    } finally {
      setQuickLoading(false)
    }
  }

  const handleSendEmailInvite = async (e) => {
    e.preventDefault()
    try {
      setEmailError(null)
      setEmailLoading(true)
      await createInvitation(user.tenant_id, null, inviteEmail)
      setEmailSent(true)
    } catch (err) {
      setEmailError(err.message || 'Failed to send invitation')
    } finally {
      setEmailLoading(false)
    }
  }

  const handleGenerateAnother = () => {
    setInvitationCode(null)
    setQuickError(null)
  }

  const handleInviteAnother = () => {
    setEmailSent(false)
    setInviteEmail('')
    setEmailError(null)
  }

  const handleCopyCode = () => {
    navigator.clipboard.writeText(invitationCode)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  // ── Permissions modal ─────────────────────────────────────────────────────

  const openPermModal = (member) => {
    setPermMember(member)
    setPermSelection(member.permissions || [])
    setPermError(null)
  }

  const togglePerm = (perm) => {
    if (permSelection.includes(perm)) {
      setPermSelection(permSelection.filter(p => p !== perm))
    } else {
      setPermSelection([...permSelection, perm])
    }
  }

  const handleSavePermissions = async () => {
    try {
      setPermSaving(true)
      setPermError(null)
      await setMemberPermissions(permMember.id, permSelection)
      await fetchData()
      setPermMember(null)
    } catch (err) {
      setPermError(err.message || 'Failed to save permissions')
    } finally {
      setPermSaving(false)
    }
  }

  // ── Targets ───────────────────────────────────────────────────────────────

  const handleTargetFirstNameChange = (e) => {
    setTargetFormData({ email: targetFormData.email, first_name: e.target.value, last_name: targetFormData.last_name, position: targetFormData.position })
  }

  const handleTargetLastNameChange = (e) => {
    setTargetFormData({ email: targetFormData.email, first_name: targetFormData.first_name, last_name: e.target.value, position: targetFormData.position })
  }

  const handleTargetEmailChange = (e) => {
    setTargetFormData({ email: e.target.value, first_name: targetFormData.first_name, last_name: targetFormData.last_name, position: targetFormData.position })
  }

  const handleTargetPositionChange = (e) => {
    setTargetFormData({ email: targetFormData.email, first_name: targetFormData.first_name, last_name: targetFormData.last_name, position: e.target.value })
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
      alert(error.message || 'Failed to add target')
    } finally {
      setTargetActionLoading(false)
    }
  }

  const handleDeleteTarget = async (targetId) => {
    if (!window.confirm('Remove this target? This action cannot be undone.')) return
    try {
      setTargetActionLoading(true)
      await deleteTarget(targetId)
      await fetchData()
    } finally {
      setTargetActionLoading(false)
    }
  }

  const handleGdprErase = async (targetId, targetName) => {
    if (!window.confirm(
      `GDPR Erasure — ${targetName}\n\n` +
      `This will permanently anonymize all campaign history for this target, then delete the record.\n\nContinue?`
    )) return
    try {
      setTargetActionLoading(true)
      await gdprEraseTarget(targetId)
      await fetchData()
    } finally {
      setTargetActionLoading(false)
    }
  }

  // ── Derived state ─────────────────────────────────────────────────────────

  const canManageTeam = hasPermission('manage_team')
  const canManageTargets = hasPermission('manage_targets')

  const filteredMembers = teamMembers.filter(m => {
    const q = memberSearch.toLowerCase()
    return `${m.first_name} ${m.last_name}`.toLowerCase().includes(q) || m.email.toLowerCase().includes(q)
  })

  const filteredPending = pendingInvitations.filter(inv =>
    inv.email.toLowerCase().includes(memberSearch.toLowerCase())
  )

  const filteredTargets = targets.filter(t => {
    const q = targetSearch.toLowerCase()
    return `${t.first_name} ${t.last_name}`.toLowerCase().includes(q) || t.email.toLowerCase().includes(q)
  })

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-600">Loading team data...</div>
  }

  const fullAccessCount = teamMembers.filter(m => m.permissions && m.permissions.length === ALL_PERMISSIONS.length).length

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
            <div><p className="text-sm text-gray-600 mb-1">Team Members</p><p className="text-3xl font-bold text-gray-900">{teamMembers.length}</p></div>
            <div className="p-3 bg-blue-100 rounded-lg"><Users className="w-8 h-8 text-blue-600" /></div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-gray-600 mb-1">Phishing Targets</p><p className="text-3xl font-bold text-gray-900">{targets.length}</p></div>
            <div className="p-3 bg-purple-100 rounded-lg"><TargetIcon className="w-8 h-8 text-purple-600" /></div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-indigo-500">
          <div className="flex items-center justify-between">
            <div><p className="text-sm text-gray-600 mb-1">With Full Access</p><p className="text-3xl font-bold text-gray-900">{fullAccessCount}</p></div>
            <div className="p-3 bg-indigo-100 rounded-lg"><Shield className="w-8 h-8 text-indigo-600" /></div>
          </div>
        </div>
      </div>

      {/* Team Members */}
      <section className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-500" /> Team Members
          </h2>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative">
              <Search aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <label htmlFor="member-search" className="sr-only">Search team members</label>
              <input
                id="member-search" type="text" placeholder="Search members..."
                value={memberSearch} onChange={e => setMemberSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {canManageTeam && (
              <button onClick={openInviteModal} className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors">
                <UserPlus aria-hidden="true" className="w-4 h-4" /> Invite Member
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permissions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase text-right">Joined</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMembers.length === 0 && filteredPending.length === 0 ? (
                <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-500">No members found.</td></tr>
              ) : (
                <>
                  {filteredMembers.map(member => (
                    <tr key={member.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <img src={generateAvatarUrl(member.first_name, member.last_name, member.email)} alt="" className="w-8 h-8 rounded-full" />
                          <span className="font-medium text-gray-900">{member.first_name} {member.last_name}</span>
                          {member.is_admin && (
                            <span className="px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">Admin</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{member.email}</td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1 items-center">
                          {member.is_admin ? (
                            <span className="text-xs text-gray-500 italic">All (admin)</span>
                          ) : member.permissions?.length > 0 ? (
                            member.permissions.map(p => <PermissionBadge key={p} permission={p} />)
                          ) : (
                            <span className="text-xs text-gray-400">No permissions</span>
                          )}
                          {canManageTeam && !member.is_admin && member.id !== user?.id && (
                            <button
                              onClick={() => openPermModal(member)}
                              title="Edit permissions"
                              className="ml-1 text-gray-400 hover:text-indigo-600 transition-colors"
                            >
                              <Settings className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${member.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {member.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-500 text-sm">
                        {formatDateShort(member.created_at)}
                      </td>
                    </tr>
                  ))}
                  {filteredPending.map(inv => (
                    <tr key={`pending-${inv.id}`} className="hover:bg-gray-50 bg-amber-50/40">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">
                            <Clock className="w-4 h-4 text-amber-500" />
                          </div>
                          <span className="font-medium text-gray-500 italic">Invited user</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{inv.email}</td>
                      <td className="px-6 py-4 text-xs text-gray-400">—</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Pending</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-gray-400 text-sm">
                        Invited {formatDateShort(inv.created_at)}
                      </td>
                    </tr>
                  ))}
                </>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Phishing Targets */}
      <section className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <TargetIcon className="w-5 h-5 text-purple-500" /> Phishing Targets
          </h2>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative">
              <Search aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <label htmlFor="target-search" className="sr-only">Search phishing targets</label>
              <input
                id="target-search" type="text" placeholder="Search targets..."
                value={targetSearch} onChange={e => setTargetSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>
            {canManageTargets && (
              <button onClick={() => setIsTargetModalOpen(true)} className="flex items-center justify-center gap-2 bg-purple-500 hover:bg-purple-600 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors">
                <Plus aria-hidden="true" className="w-4 h-4" /> Add Target
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Position</th>
                {canManageTargets && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTargets.length === 0 ? (
                <tr><td colSpan={canManageTargets ? 4 : 3} className="px-6 py-8 text-center text-gray-500">No phishing targets found.</td></tr>
              ) : (
                filteredTargets.map(target => (
                  <tr key={target.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900 text-sm">{target.first_name} {target.last_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{target.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600 text-sm">{target.position || '-'}</td>
                    {canManageTargets && (
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-3">
                          <button onClick={() => handleGdprErase(target.id, `${target.first_name} ${target.last_name}`)} disabled={targetActionLoading} aria-label="GDPR erase" title="GDPR erasure" className="text-amber-500 hover:text-amber-700 transition-colors disabled:opacity-50">
                            <ShieldOff aria-hidden="true" className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDeleteTarget(target.id)} disabled={targetActionLoading} aria-label="Delete target" className="text-red-500 hover:text-red-700 transition-colors disabled:opacity-50">
                            <Trash2 aria-hidden="true" className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    )}
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
          <div role="dialog" aria-modal="true" aria-labelledby="add-target-title" className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 id="add-target-title" className="text-xl font-bold mb-4">Add Phishing Target</h2>
            <form onSubmit={handleAddTarget} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="target-first-name" className="block text-sm font-medium text-gray-700">First Name</label>
                  <input id="target-first-name" type="text" required value={targetFormData.first_name} onChange={handleTargetFirstNameChange} className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
                </div>
                <div>
                  <label htmlFor="target-last-name" className="block text-sm font-medium text-gray-700">Last Name</label>
                  <input id="target-last-name" type="text" required value={targetFormData.last_name} onChange={handleTargetLastNameChange} className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
                </div>
              </div>
              <div>
                <label htmlFor="target-email" className="block text-sm font-medium text-gray-700">Email Address</label>
                <input id="target-email" type="email" required value={targetFormData.email} onChange={handleTargetEmailChange} className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
              </div>
              <div>
                <label htmlFor="target-position" className="block text-sm font-medium text-gray-700">Position / Title (Optional)</label>
                <input id="target-position" type="text" value={targetFormData.position} onChange={handleTargetPositionChange} className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setIsTargetModalOpen(false)} className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">Cancel</button>
                <button type="submit" disabled={targetActionLoading} className="px-4 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50">
                  {targetActionLoading ? 'Saving...' : 'Add Target'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Permissions Modal */}
      {permMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div role="dialog" aria-modal="true" aria-labelledby="perm-modal-title" className="bg-white rounded-lg shadow-xl max-w-sm w-full p-6">
            <h2 id="perm-modal-title" className="text-lg font-bold text-gray-900 mb-1">Edit Permissions</h2>
            <p className="text-sm text-gray-500 mb-4">{permMember.first_name} {permMember.last_name}</p>

            {permError && (
              <div role="alert" className="mb-3 p-3 bg-red-50 text-red-700 rounded border border-red-200 text-sm">{permError}</div>
            )}

            <div className="space-y-3">
              {ALL_PERMISSIONS.map(perm => (
                <label key={perm} className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={permSelection.includes(perm)}
                    onChange={() => togglePerm(perm)}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-800">{PERMISSION_LABELS[perm]}</span>
                    <span className="ml-2 text-xs text-gray-400">{perm}</span>
                  </div>
                </label>
              ))}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setPermMember(null)} className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">Cancel</button>
              <button onClick={handleSavePermissions} disabled={permSaving} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50">
                {permSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite Member Modal */}
      {isInviteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div role="dialog" aria-modal="true" aria-labelledby="invite-modal-title" className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 id="invite-modal-title" className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-blue-500" /> Invite Team Member
              </h2>
              <button onClick={handleCloseInviteModal} aria-label="Close modal" className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
            </div>

            <div className="flex border-b border-gray-100">
              <button
                onClick={() => setInviteTab('quick')}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${inviteTab === 'quick' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Quick Code
              </button>
              <button
                onClick={() => setInviteTab('email')}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${inviteTab === 'email' ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Send via Email
              </button>
            </div>

            <div className="p-6">
              {inviteTab === 'quick' && (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">Generate a one-time code and share it with the person you want to invite.</p>
                  {quickError && <div role="alert" className="p-3 bg-red-50 text-red-700 rounded border border-red-200 text-sm">{quickError}</div>}
                  {!invitationCode ? (
                    <button onClick={handleGenerateCode} disabled={quickLoading} className="w-full py-2.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
                      {quickLoading ? 'Generating...' : 'Generate Code'}
                    </button>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-50 border rounded px-4 py-3 font-mono text-lg font-bold text-gray-900 tracking-widest">{invitationCode}</div>
                        <button onClick={handleCopyCode} aria-label={copiedCode ? 'Copied' : 'Copy code'} className="p-3 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                          {copiedCode ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                        </button>
                      </div>
                      <p className="text-xs text-gray-500">This code can be used once. Share it securely.</p>
                      <button onClick={handleGenerateAnother} className="text-xs text-blue-600 hover:underline">Generate another</button>
                    </div>
                  )}
                </div>
              )}

              {inviteTab === 'email' && (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">Send an invitation email. The recipient appears as <strong>Pending</strong> until they register.</p>
                  {emailError && <div role="alert" className="p-3 bg-red-50 text-red-700 rounded border border-red-200 text-sm">{emailError}</div>}
                  {emailSent ? (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-medium text-green-800">Invitation sent!</p>
                          <p className="text-xs text-green-700 mt-0.5">Email sent to <strong>{inviteEmail}</strong>.</p>
                        </div>
                      </div>
                      <button onClick={handleInviteAnother} className="text-xs text-blue-600 hover:underline">Invite another</button>
                    </div>
                  ) : (
                    <form onSubmit={handleSendEmailInvite} className="space-y-4">
                      <div>
                        <label htmlFor="invite-email" className="block text-sm font-medium text-gray-700 mb-1">Email address</label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                          <input id="invite-email" type="email" required value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="colleague@company.com" className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500" />
                        </div>
                      </div>
                      <button type="submit" disabled={emailLoading} className="w-full py-2.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2">
                        <Mail className="w-4 h-4" />
                        {emailLoading ? 'Sending...' : 'Send Invitation'}
                      </button>
                    </form>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
