import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import FormLayout, { FormSection, FormField, FormActions } from '../../components/FormLayout'
import Input from '../../components/Input'
import Select from '../../components/Select'
import { createCampaign } from '../../services/campaignsService'
import { getTemplates } from '../../services/templatesService'

export default function CreateCampaign() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
  })
  const [templates, setTemplates] = useState([])
  const [loadingTemplates, setLoadingTemplates] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      setLoadingTemplates(true)
      const data = await getTemplates()
      setTemplates(data)
    } catch (err) {
      setError(err.message || 'Failed to load templates')
      console.error('Error fetching templates:', err)
    } finally {
      setLoadingTemplates(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleTemplateChange = (templateId) => {
    setFormData(prev => ({
      ...prev,
      template_id: templateId
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!formData.template_id) {
      setError('Please select a template')
      return
    }

    try {
      setSubmitting(true)
      await createCampaign({
        name: formData.name,
        template_id: formData.template_id,
      })
      navigate('/campaigns')
    } catch (error) {
      setError(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate('/campaigns')
  }

  return (
    <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/campaigns')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="text-sm font-medium">Back to Campaigns</span>
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Create Campaign</h1>
          <p className="mt-2 text-sm text-gray-600">
            Set up a new phishing awareness campaign to train your team.
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow p-6">
          {error && (
            <div role="alert" className="mb-6 rounded-md bg-red-50 border border-red-200 p-4">
              <div className="flex items-start gap-3">
                <AlertCircle aria-hidden="true" className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}

          <FormLayout 
            onSubmit={handleSubmit} 
            actions={
              <FormActions 
                onCancel={handleCancel} 
                submitLabel={submitting ? "Creating..." : "Create Campaign"}
              />
            }
          >
            <FormSection
              title="Campaign Details"
              description="Enter the basic information for your phishing awareness campaign."
            >
              <FormField label="Campaign Name" id="name" required colSpan="col-span-full">
                <Input
                  id="name"
                  name="name"
                  type="text"
                  required
                  placeholder="e.g., Q4 Security Awareness Training"
                  value={formData.name}
                  onChange={handleChange}
                />
              </FormField>

              <FormField 
                label="Template" 
                id="template_id" 
                required 
                colSpan="col-span-full"
                description="Select a template to use for this campaign."
              >
                {loadingTemplates ? (
                  <div className="mt-2 rounded-md bg-gray-50 px-3 py-2 text-sm text-gray-600 border border-gray-200">
                    Loading templates...
                  </div>
                ) : templates.length === 0 ? (
                  <div className="mt-2 rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800 border border-yellow-200">
                    No templates available. Please create a template first.
                  </div>
                ) : (
                  <div className="mt-2">
                    <Select
                      options={templates.map(template => ({
                        value: template.id.toString(),
                        label: template.name
                      }))}
                      value={formData.template_id}
                      onChange={handleTemplateChange}
                      placeholder="Select a template"
                    />
                  </div>
                )}
              </FormField>
            </FormSection>

            <FormSection
              title="Campaign Configuration"
              description="Configure the settings for your campaign. You can edit these later."
              borderBottom={false}
            >
              <FormField
                label="Status"
                id="status"
                description="New campaigns are created as running and will be launched immediately."
                colSpan="sm:col-span-3"
              >
                <div className="mt-2">
                  <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                    Running
                  </span>
                </div>
              </FormField>
            </FormSection>
          </FormLayout>
        </div>
    </div>
  )
}
