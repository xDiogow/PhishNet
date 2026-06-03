import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, FileText } from 'lucide-react'
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
  const { isAdmin } = useUser()
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isViewModalOpen, setIsViewModalOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)
  const [viewingTemplate, setViewingTemplate] = useState(null)
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    email_template_data: {
      subject: '',
      html: '',
    },
    landing_page_data: {
      html: '',
      redirect_url: '',
    },
  })

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
    setFormData({
      name: '',
      email_template_data: {
        subject: '',
        html: '',
      },
      landing_page_data: {
        html: '',
        redirect_url: '',
      },
    })
    setIsModalOpen(true)
  }

  const handleOpenEditModal = async (template) => {
    try {
      // Fetch full template details for editing
      const fullTemplate = await getTemplate(template.id)

      setEditingTemplate(template)
      setFormData({
        name: fullTemplate.name || '',
        email_template_data: {
          subject: fullTemplate.email_template?.subject || '',
          html: fullTemplate.email_template?.html || '',
        },
        landing_page_data: {
          html: fullTemplate.landing_page?.html || '',
          redirect_url: fullTemplate.landing_page?.redirect_url || '',
        },
      })
      setIsModalOpen(true)
    } catch (err) {
      setError(err.message || 'Failed to load template details')
      console.error('Error loading template:', err)
    }
  }

  const handleOpenViewModal = async (template) => {
    try {
      const fullTemplate = await getTemplate(template.id)
      setViewingTemplate(fullTemplate)
      setIsViewModalOpen(true)
    } catch (err) {
      setError(err.message || 'Failed to load template details')
      console.error('Error loading template:', err)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTemplate(null)
  }

  const handleCloseViewModal = () => {
    setIsViewModalOpen(false)
    setViewingTemplate(null)
  }

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value,
        },
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value,
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setError(null)
      
      if (editingTemplate) {
        await updateTemplate(editingTemplate.id, formData)
      } else {
        await createTemplate(formData)
      }

      handleCloseModal()
      await fetchTemplates()
    } catch (err) {
      const errorMessage = err.message || 'Failed to save template'
      setError(errorMessage)
      console.error('Error saving template:', err)
    }
  }

  const handleDeleteClick = (template) => {
    setEditingTemplate(template)
    setIsDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      setError(null)
      await deleteTemplate(editingTemplate.id)
      setIsDeleteDialogOpen(false)
      setEditingTemplate(null)
      await fetchTemplates()
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete template'
      setError(errorMessage)
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
            {isAdmin() 
              ? 'Manage email templates and landing pages for your campaigns' 
              : 'Browse available templates for your campaigns'}
          </p>
        </div>
        {isAdmin() && (
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
            {isAdmin() ? 'Get started by creating a new template.' : 'No templates available yet.'}
          </p>
          {isAdmin() && (
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
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {template.name}
                    </h3>
                    {template.created_at && (
                      <p className="text-sm text-gray-500">
                        Created {formatDate(template.created_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleOpenViewModal(template)}
                  className="flex-1 text-sm font-medium text-blue-600 hover:text-blue-500 py-2 px-4 rounded-md hover:bg-blue-50 transition-colors"
                >
                  View Details
                </button>
                
                {isAdmin() && (
                  <div className="flex gap-2">
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
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
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
                  value={formData.email_template_data.subject}
                  onChange={(e) => handleInputChange('email_template_data.subject', e.target.value)}
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
                  value={formData.email_template_data.html}
                  onChange={(e) => handleInputChange('email_template_data.html', e.target.value)}
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
                  value={formData.landing_page_data.html}
                  onChange={(e) => handleInputChange('landing_page_data.html', e.target.value)}
                  placeholder="<html><body>Your landing page content here...</body></html>"
                />
              </div>

              <div>
                <label htmlFor="redirect_url" className="block text-sm font-medium text-gray-700">
                  Redirect URL
                </label>
                <Input
                  id="redirect_url"
                  name="redirect_url"
                  type="url"
                  value={formData.landing_page_data.redirect_url}
                  onChange={(e) => handleInputChange('landing_page_data.redirect_url', e.target.value)}
                  placeholder="https://example.com"
                />
                <p className="mt-1 text-xs text-gray-500">
                  URL to redirect users after they submit the form.
                </p>
              </div>
            </div>
          </div>
        </form>
      </Modal>

      {/* View Template Modal */}
      <Modal
        open={isViewModalOpen}
        onClose={handleCloseViewModal}
        title="Template Details"
        footer={
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleCloseViewModal}
              className="inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        }
        size="lg"
      >
        {viewingTemplate && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {viewingTemplate.name}
              </h3>
              {viewingTemplate.created_at && (
                <p className="text-sm text-gray-500">
                  Created {formatDate(viewingTemplate.created_at)}
                </p>
              )}
            </div>

            {/* Email Template Info */}
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-900 mb-3">Email Template</h4>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Subject</dt>
                  <dd className="text-sm text-gray-900">{viewingTemplate.email_template?.subject}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500 mb-1">HTML Preview</dt>
                  <dd className="text-sm">
                    <div className="border rounded-md p-4 bg-gray-50 max-h-64 overflow-auto">
                      <pre className="text-xs whitespace-pre-wrap font-mono">
                        {viewingTemplate.email_template?.html}
                      </pre>
                    </div>
                  </dd>
                </div>
              </dl>
            </div>

            {/* Landing Page Info */}
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-900 mb-3">Landing Page</h4>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Redirect URL</dt>
                  <dd className="text-sm text-gray-900">
                    {viewingTemplate.landing_page?.redirect_url || 'Not set'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500 mb-1">HTML Preview</dt>
                  <dd className="text-sm">
                    <div className="border rounded-md p-4 bg-gray-50 max-h-64 overflow-auto">
                      <pre className="text-xs whitespace-pre-wrap font-mono">
                        {viewingTemplate.landing_page?.html}
                      </pre>
                    </div>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setEditingTemplate(null)
        }}
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
