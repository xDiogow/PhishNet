import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, FileText, Globe } from 'lucide-react'
import Button from '../../components/Button'
import Modal from '../../components/Modal'
import ConfirmDialog from '../../components/ConfirmDialog'
import Input from '../../components/Input'
import Textarea from '../../components/Textarea'
import { useUser } from '../../contexts/UserContext'
import {
  getTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate
} from '../../services/templatesService'
import { formatDate } from '../../utils/dateUtils'

export default function Templates() {
  const { isAdmin, hasPermission } = useUser()

  const canCreate = () => isAdmin() || hasPermission('manage_templates')
  const canManage = (template) => {
    if (template.is_global) return isAdmin()
    return hasPermission('manage_templates')
  }

  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)

  // Form fields — one state variable per field
  const [templateName, setTemplateName] = useState('')
  const [emailSubject, setEmailSubject] = useState('')
  const [emailHtml, setEmailHtml] = useState('')
  const [landingHtml, setLandingHtml] = useState('')

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      setError(null)
      setLoading(true)
      const data = await getTemplates()
      setTemplates(data)
    } catch (err) {
      setError(err.message || 'Failed to load templates')
      console.error('Error fetching templates:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingTemplate(null)
    setTemplateName('')
    setEmailSubject('')
    setEmailHtml('')
    setLandingHtml('')
    setIsModalOpen(true)
  }

  const handleOpenEditModal = async (template) => {
    try {
      const fullTemplate = await getTemplate(template.id)
      setEditingTemplate(template)
      setTemplateName(fullTemplate.name || '')
      setEmailSubject(fullTemplate.email_template ? fullTemplate.email_template.subject : '')
      setEmailHtml(fullTemplate.email_template ? fullTemplate.email_template.html : '')
      setLandingHtml(fullTemplate.landing_page ? fullTemplate.landing_page.html : '')
      setIsModalOpen(true)
    } catch (err) {
      setError(err.message || 'Failed to load template details')
      console.error('Error loading template:', err)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTemplate(null)
  }

  const handleNameChange = (value) => {
    setTemplateName(value)
  }

  const handleEmailSubjectChange = (value) => {
    setEmailSubject(value)
  }

  const handleEmailHtmlChange = (value) => {
    setEmailHtml(value)
  }

  const handleLandingHtmlChange = (value) => {
    setLandingHtml(value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      const payload = {
        name: templateName,
        email_template_data: { subject: emailSubject, html: emailHtml },
        landing_page_data: { html: landingHtml },
      }
      if (editingTemplate) {
        await updateTemplate(editingTemplate.id, payload)
      } else {
        await createTemplate(payload)
      }
      handleCloseModal()
      await fetchTemplates()
    } catch (err) {
      setError(err.message || 'Failed to save template')
      console.error('Error saving template:', err)
    }
  }

  const handleDeleteClick = (template) => {
    setEditingTemplate(template)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteCancel = () => {
    setIsDeleteDialogOpen(false)
    setEditingTemplate(null)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteTemplate(editingTemplate.id)
      setIsDeleteDialogOpen(false)
      setEditingTemplate(null)
      await fetchTemplates()
    } catch (err) {
      setError(err.message || 'Failed to delete template')
      console.error('Error deleting template:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading templates...</div>
      </div>
    )
  }

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
          <p className="mt-1 text-sm text-gray-500">
            {canCreate()
              ? 'Manage email templates and landing pages for your campaigns'
              : 'Browse available templates for your campaigns'}
          </p>
        </div>
        {canCreate() && (
          <Button onClick={handleOpenCreateModal} fullWidth={false}>
            <Plus className="w-5 h-5 mr-2" />
            Create Template
          </Button>
        )}
      </div>

      {error && (
        <div role="alert" className="mb-4 rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {templates.length === 0 ? (
        <div className="text-center py-12">
          <FileText aria-hidden="true" className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No templates</h3>
          <p className="mt-1 text-sm text-gray-500">
            {canCreate() ? 'Get started by creating a new template.' : 'No templates available yet.'}
          </p>
          {canCreate() && (
            <div className="mt-6">
              <Button onClick={handleOpenCreateModal} fullWidth={false}>
                <Plus className="w-5 h-5 mr-2" />
                Create Template
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <div
              key={template.id}
              className="relative flex flex-col rounded-lg border border-gray-300 bg-white p-6 shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {template.name}
                      </h3>
                      {template.is_global && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                          <Globe aria-hidden="true" className="h-3 w-3" />
                          Platform
                        </span>
                      )}
                    </div>
                    {template.created_at && (
                      <p className="text-sm text-gray-500">
                        Created {formatDate(template.created_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {canManage(template) && (
                <div className="mt-4 flex gap-2 justify-end">
                  <button
                    onClick={() => handleOpenEditModal(template)}
                    aria-label={`Edit template ${template.name}`}
                    className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <Pencil aria-hidden="true" className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteClick(template)}
                    aria-label={`Delete template ${template.name}`}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <Trash2 aria-hidden="true" className="h-5 w-5" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        title={editingTemplate ? 'Edit Template' : 'Create New Template'}
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
              form="template-form"
              fullWidth={false}
            >
              {editingTemplate ? 'Update' : 'Create'}
            </Button>
          </div>
        }
        size="lg"
      >
        <form id="template-form" onSubmit={handleSubmit} className="space-y-6">
          {/* Template Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Template Name
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              value={templateName}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder="e.g., Security Awareness Template"
            />
          </div>

          {/* Email Template Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Email Template</h3>

            <div className="space-y-4">
              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                  Email Subject
                </label>
                <Input
                  id="subject"
                  name="subject"
                  type="text"
                  required
                  value={emailSubject}
                  onChange={(e) => handleEmailSubjectChange(e.target.value)}
                  placeholder="e.g., Action Required: Verify Your Account"
                />
              </div>

              <div>
                <label htmlFor="email_html" className="block text-sm font-medium text-gray-700">
                  Email HTML Content
                </label>
                <Textarea
                  id="email_html"
                  name="email_html"
                  rows={6}
                  required
                  value={emailHtml}
                  onChange={(e) => handleEmailHtmlChange(e.target.value)}
                  placeholder="<html><body>Your email content here...</body></html>"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Use HTML to format your email. Include {'{{.TrackingUrl}}'} for tracking.
                </p>
              </div>
            </div>
          </div>

          {/* Landing Page Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Landing Page</h3>

            <div className="space-y-4">
              <div>
                <label htmlFor="landing_html" className="block text-sm font-medium text-gray-700">
                  Landing Page HTML
                </label>
                <Textarea
                  id="landing_html"
                  name="landing_html"
                  rows={6}
                  required
                  value={landingHtml}
                  onChange={(e) => handleLandingHtmlChange(e.target.value)}
                  placeholder="<html><body>Your landing page content here...</body></html>"
                />
              </div>

              <p className="mt-1 text-xs text-gray-500">
                After submitting the form, users are automatically redirected to the caught page.
              </p>
            </div>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        title="Delete Template"
        message={
          editingTemplate
            ? `Are you sure you want to delete "${editingTemplate.name}"? This action cannot be undone.`
            : 'Are you sure you want to delete this template?'
        }
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  )
}
