import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Building2, Key, Copy, CheckCircle2, Users } from 'lucide-react'
import Button from '../../components/Button'
import Modal from '../../components/Modal'
import ConfirmDialog from '../../components/ConfirmDialog'
import Input from '../../components/Input'
import {
  getTenants,
  createTenant,
  updateTenant,
  deleteTenant
} from '../../services/tenantsService'
import { createInvitation, getInvitationsByTenant } from '../../services/invitationsService'
import { formatDate } from '../../utils/dateUtils'

export default function Tenants() {
  const [tenants, setTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isInvitationsModalOpen, setIsInvitationsModalOpen] = useState(false)
  const [editingTenant, setEditingTenant] = useState(null)
  const [viewingInvitationsTenant, setViewingInvitationsTenant] = useState(null)
  
  // Invitations data
  const [invitations, setInvitations] = useState([])
  const [loadingInvitations, setLoadingInvitations] = useState(false)
  const [copiedCode, setCopiedCode] = useState(null)
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    invitation_expires_days: '',
  })

  useEffect(() => {
    fetchTenants()
  }, [])

  const fetchTenants = async () => {
    try {
      setError(null)
      setLoading(true)
      const data = await getTenants()
      setTenants(data)
    } catch (err) {
      setError(err.message || 'Failed to load tenants')
      console.error('Error fetching tenants:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchInvitations = async (tenantId) => {
    try {
      setLoadingInvitations(true)
      const data = await getInvitationsByTenant(tenantId)
      setInvitations(data)
    } catch (err) {
      setError(err.message || 'Failed to load invitations')
      console.error('Error fetching invitations:', err)
    } finally {
      setLoadingInvitations(false)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingTenant(null)
    setFormData({
      name: '',
      invitation_expires_days: '',
    })
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (tenant) => {
    setEditingTenant(tenant)
    setFormData({
      name: tenant.name,
      invitation_expires_days: '',
    })
    setIsModalOpen(true)
  }

  const handleOpenInvitationsModal = async (tenant) => {
    setViewingInvitationsTenant(tenant)
    setIsInvitationsModalOpen(true)
    await fetchInvitations(tenant.id)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTenant(null)
    setSuccessMessage(null)
  }

  const handleCloseInvitationsModal = () => {
    setIsInvitationsModalOpen(false)
    setViewingInvitationsTenant(null)
    setInvitations([])
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      setSuccessMessage(null)
      
      if (editingTenant) {
        // Update tenant (name only)
        await updateTenant(editingTenant.id, {
          name: formData.name.trim()
        })
        setSuccessMessage('Tenant updated successfully')
      } else {
        // Create tenant with invitation
        const submitData = {
          name: formData.name.trim()
        }
        
        if (formData.invitation_expires_days) {
          const days = parseInt(formData.invitation_expires_days)
          if (days > 0) {
            submitData.invitation_expires_days = days
          }
        }

        const response = await createTenant(submitData)
        
        // Show success message with invitation code
        if (response.invitation) {
          setSuccessMessage(
            `Tenant created successfully! Invitation code: ${response.invitation.invitation_code}`
          )
        } else {
          setSuccessMessage('Tenant created successfully!')
        }
      }

      await fetchTenants()
      
      // Don't close modal immediately so user can see success message
      setTimeout(() => {
        handleCloseModal()
      }, 3000)
    } catch (err) {
      const errorMessage = err.message || 'Failed to save tenant'
      setError(errorMessage)
      console.error('Error saving tenant:', err)
    }
  }

  const handleDeleteClick = (tenant) => {
    setEditingTenant(tenant)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteTenant(editingTenant.id)
      setIsDeleteDialogOpen(false)
      setEditingTenant(null)
      await fetchTenants()
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete tenant'
      setError(errorMessage)
      console.error('Error deleting tenant:', err)
      setIsDeleteDialogOpen(false)
      setEditingTenant(null)
    }
  }

  const handleCreateInvitation = async () => {
    if (!viewingInvitationsTenant) return
    
    try {
      setError(null)
      await createInvitation(viewingInvitationsTenant.id)
      await fetchInvitations(viewingInvitationsTenant.id)
    } catch (err) {
      const errorMessage = err.message || 'Failed to create invitation'
      setError(errorMessage)
      console.error('Error creating invitation:', err)
    }
  }

  const handleCopyInvitationCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code)
      setCopiedCode(code)
      setTimeout(() => setCopiedCode(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading tenants...</div>
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tenants</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage tenant organizations and their invitations
          </p>
        </div>
        <Button onClick={handleOpenCreateModal} fullWidth={false}>
          <Plus className="w-5 h-5 mr-2" />
          Create Tenant
        </Button>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {tenants.length === 0 ? (
        <div className="text-center py-12">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No tenants</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first tenant.
          </p>
          <div className="mt-6">
            <Button onClick={handleOpenCreateModal} fullWidth={false}>
              <Plus className="w-5 h-5 mr-2" />
              Create Tenant
            </Button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg overflow-hidden shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                    Name
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Created
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {tenants.map((tenant) => (
                  <tr key={tenant.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                      {tenant.name}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {formatDate(tenant.created_at)}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenInvitationsModal(tenant)}
                          className="p-2 text-gray-600 hover:text-purple-600 hover:bg-gray-100 rounded-md transition-colors"
                          title="Manage Invitations"
                        >
                          <Key className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleOpenEditModal(tenant)}
                          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-md transition-colors"
                          title="Edit"
                        >
                          <Pencil className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(tenant)}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded-md transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        title={editingTenant ? 'Edit Tenant' : 'Create New Tenant'}
        footer={
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleCloseModal}
              className="inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Cancel
            </button>
            <Button
              type="submit"
              form="tenant-form"
              fullWidth={false}
            >
              {editingTenant ? 'Update' : 'Create'}
            </Button>
          </div>
        }
        size="md"
      >
        {successMessage && (
          <div className="mb-4 rounded-md bg-green-50 p-4 border border-green-200">
            <div className="flex">
              <CheckCircle2 className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">{successMessage}</p>
              </div>
            </div>
          </div>
        )}
        
        <form id="tenant-form" onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Tenant Name
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Acme Corporation"
            />
          </div>

          {!editingTenant && (
            <div>
              <label htmlFor="invitation_expires_days" className="block text-sm font-medium text-gray-700">
                Invitation Expiry (days) <span className="text-gray-500">(optional)</span>
              </label>
              <Input
                id="invitation_expires_days"
                name="invitation_expires_days"
                type="number"
                min="1"
                value={formData.invitation_expires_days}
                onChange={handleInputChange}
                placeholder="Leave empty for no expiration"
              />
              <p className="mt-1 text-xs text-gray-500">
                Number of days until the initial invitation expires
              </p>
            </div>
          )}
        </form>
      </Modal>

      {/* Invitations Modal */}
      <Modal
        open={isInvitationsModalOpen}
        onClose={handleCloseInvitationsModal}
        title={`Invitations - ${viewingInvitationsTenant?.name || ''}`}
        footer={
          <div className="flex justify-between items-center w-full">
            <Button
              onClick={handleCreateInvitation}
              fullWidth={false}
              className="bg-purple-500 hover:bg-purple-600"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Invitation
            </Button>
            <button
              type="button"
              onClick={handleCloseInvitationsModal}
              className="inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        }
        size="lg"
      >
        {loadingInvitations ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-gray-500">Loading invitations...</div>
          </div>
        ) : invitations.length === 0 ? (
          <div className="text-center py-8">
            <Key className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No invitations</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create an invitation to allow users to join this tenant.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {invitations.map((invitation) => (
              <div
                key={invitation.id}
                className={`border rounded-lg p-4 ${
                  invitation.is_used
                    ? 'bg-gray-50 border-gray-200'
                    : invitation.is_valid
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <code className="text-sm font-mono bg-white px-2 py-1 rounded border">
                        {invitation.invitation_code}
                      </code>
                      <button
                        onClick={() => handleCopyInvitationCode(invitation.invitation_code)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Copy code"
                      >
                        {copiedCode === invitation.invitation_code ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    
                    <div className="text-xs text-gray-600 space-y-1">
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(invitation.created_at)}
                      </div>
                      {invitation.expires_at && (
                        <div>
                          <span className="font-medium">Expires:</span> {formatDate(invitation.expires_at)}
                        </div>
                      )}
                      {invitation.is_used && invitation.used_at && (
                        <div>
                          <span className="font-medium">Used:</span> {formatDate(invitation.used_at)}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <span
                      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                        invitation.is_used
                          ? 'bg-gray-100 text-gray-700 ring-gray-600/20'
                          : invitation.is_valid
                          ? 'bg-green-100 text-green-700 ring-green-600/20'
                          : 'bg-red-100 text-red-700 ring-red-600/20'
                      }`}
                    >
                      {invitation.is_used ? (
                        <>
                          <Users className="w-3 h-3 mr-1" />
                          Used
                        </>
                      ) : invitation.is_valid ? (
                        'Valid'
                      ) : (
                        'Expired'
                      )}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setEditingTenant(null)
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Tenant"
        message={
          editingTenant
            ? `Are you sure you want to delete "${editingTenant.name}"? This action cannot be undone and will fail if there are users in this tenant.`
            : 'Are you sure you want to delete this tenant?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
