import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Calendar, Users, CheckSquare, Square } from 'lucide-react'
import FormLayout, { FormSection, FormField, FormActions } from '../../components/FormLayout'
import Input from '../../components/Input'
import Select from '../../components/Select'
import { createCampaign } from '../../services/campaignsService'
import { getTemplates } from '../../services/templatesService'
import { getTargets } from '../../services/teamService'

function defaultDatetime(offsetMinutes = 0) {
  const d = new Date(Date.now() + offsetMinutes * 60 * 1000)
  d.setSeconds(0, 0)
  return d.toISOString().slice(0, 16)
}

export default function CreateCampaign() {
  const navigate = useNavigate()

  const [name, setName]               = useState('')
  const [templateId, setTemplateId]   = useState('')
  const [templates, setTemplates]     = useState([])
  const [loadingTemplates, setLoadingTemplates] = useState(true)

  const [targets, setTargets]         = useState([])
  const [loadingTargets, setLoadingTargets] = useState(true)
  const [allTargets, setAllTargets]   = useState(true)      // "All" toggle
  const [selectedIds, setSelectedIds] = useState(new Set()) // individual selection

  const [scheduled, setScheduled]     = useState(false)
  const [scheduleStart, setScheduleStart] = useState(defaultDatetime(60))
  const [scheduleEnd,   setScheduleEnd]   = useState(defaultDatetime(60 * 24 * 7))

  const [error, setError]             = useState(null)
  const [submitting, setSubmitting]   = useState(false)

  useEffect(() => {
    Promise.all([
      getTemplates().then(setTemplates).finally(() => setLoadingTemplates(false)),
      getTargets().then(data => {
        setTargets(data || [])
        setSelectedIds(new Set((data || []).map(t => t.id)))
      }).finally(() => setLoadingTargets(false)),
    ]).catch(err => setError(err.message || 'Failed to load data'))
  }, [])

  const toggleAll = () => {
    if (allTargets) {
      setAllTargets(false)
      setSelectedIds(new Set())
    } else {
      setAllTargets(true)
      setSelectedIds(new Set(targets.map(t => t.id)))
    }
  }

  const toggleTarget = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      // sync "all" checkbox
      setAllTargets(next.size === targets.length)
      return next
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!templateId) { setError('Please select a template'); return }
    if (selectedIds.size === 0) { setError('Select at least one target'); return }

    if (scheduled) {
      if (!scheduleStart) { setError('Please set a start date'); return }
      if (!scheduleEnd)   { setError('Please set an end date');   return }
      if (new Date(scheduleEnd) <= new Date(scheduleStart)) {
        setError('End date must be after start date')
        return
      }
    }

    try {
      setSubmitting(true)
      const payload = {
        name,
        template_id: templateId,
        target_ids: allTargets ? null : [...selectedIds],
      }
      if (scheduled) {
        payload.scheduled_start_at = new Date(scheduleStart).toISOString()
        payload.scheduled_end_at   = new Date(scheduleEnd).toISOString()
      }
      await createCampaign(payload)
      navigate('/campaigns')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
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
              onCancel={() => navigate('/campaigns')}
              submitLabel={submitting ? 'Creating...' : 'Create Campaign'}
            />
          }
        >
          {/* ── Campaign Details ───────────────────────────────── */}
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
                value={name}
                onChange={e => setName(e.target.value)}
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
                  Loading templates…
                </div>
              ) : templates.length === 0 ? (
                <div className="mt-2 rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800 border border-yellow-200">
                  No templates available. Please create a template first.
                </div>
              ) : (
                <div className="mt-2">
                  <Select
                    options={templates.map(t => ({ value: t.id.toString(), label: t.name }))}
                    value={templateId}
                    onChange={setTemplateId}
                    placeholder="Select a template"
                  />
                </div>
              )}
            </FormField>
          </FormSection>

          {/* ── Targets ────────────────────────────────────────── */}
          <FormSection
            title="Targets"
            description="Choose who will receive the phishing simulation."
          >
            <div className="col-span-full">
              {loadingTargets ? (
                <div className="rounded-md bg-gray-50 px-3 py-2 text-sm text-gray-600 border border-gray-200">
                  Loading targets…
                </div>
              ) : targets.length === 0 ? (
                <div className="rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800 border border-yellow-200">
                  No targets found. Add targets in the Team page first.
                </div>
              ) : (
                <div className="rounded-lg border border-gray-200 overflow-hidden">
                  {/* All targets row */}
                  <button
                    type="button"
                    onClick={toggleAll}
                    className="w-full flex items-center gap-3 px-4 py-3 bg-gray-50 hover:bg-gray-100 border-b border-gray-200 transition-colors text-left"
                  >
                    {allTargets
                      ? <CheckSquare className="h-4 w-4 text-blue-600 flex-shrink-0" />
                      : <Square className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    }
                    <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                      <Users className="h-4 w-4 text-gray-400" aria-hidden="true" />
                      All targets
                    </span>
                    <span className="ml-auto text-xs text-gray-500">
                      {targets.length} recipient{targets.length !== 1 ? 's' : ''}
                    </span>
                  </button>

                  {/* Individual targets */}
                  <div className="divide-y divide-gray-100 max-h-56 overflow-y-auto">
                    {targets.map(target => (
                      <button
                        key={target.id}
                        type="button"
                        onClick={() => toggleTarget(target.id)}
                        className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 transition-colors text-left"
                      >
                        {selectedIds.has(target.id)
                          ? <CheckSquare className="h-4 w-4 text-blue-600 flex-shrink-0" />
                          : <Square className="h-4 w-4 text-gray-300 flex-shrink-0" />
                        }
                        <span className="text-sm text-gray-800">
                          {target.first_name} {target.last_name}
                        </span>
                        <span className="ml-auto text-xs text-gray-400">{target.email}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Selection summary */}
              {targets.length > 0 && (
                <p className="mt-2 text-xs text-gray-500">
                  {selectedIds.size} of {targets.length} target{targets.length !== 1 ? 's' : ''} selected
                </p>
              )}
            </div>
          </FormSection>

          {/* ── Scheduling ─────────────────────────────────────── */}
          <FormSection
            title="Campaign Schedule"
            description="Launch immediately or schedule a start and end date."
            borderBottom={false}
          >
            {/* Toggle */}
            <div className="col-span-full flex items-center gap-3">
              <button
                type="button"
                role="switch"
                aria-checked={scheduled}
                onClick={() => setScheduled(v => !v)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  scheduled ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  aria-hidden="true"
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    scheduled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
              <span className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Calendar className="h-4 w-4 text-gray-400" aria-hidden="true" />
                Schedule this campaign
              </span>
            </div>

            {/* Status badge */}
            <FormField
              label="Status"
              id="status"
              description={
                scheduled
                  ? 'Campaign will be queued and launched automatically at the scheduled start.'
                  : 'Campaign will start immediately and emails will be sent right away.'
              }
              colSpan="sm:col-span-3"
            >
              <div className="mt-2">
                {scheduled ? (
                  <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
                    Scheduled
                  </span>
                ) : (
                  <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                    Running (immediate)
                  </span>
                )}
              </div>
            </FormField>

            {/* Date inputs */}
            {scheduled && (
              <>
                <FormField
                  label="Start date"
                  id="schedule_start"
                  required
                  colSpan="sm:col-span-3"
                  description="Campaign emails will be sent at this time."
                >
                  <input
                    id="schedule_start"
                    type="datetime-local"
                    value={scheduleStart}
                    onChange={e => setScheduleStart(e.target.value)}
                    min={defaultDatetime(5)}
                    required
                    className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </FormField>

                <FormField
                  label="End date"
                  id="schedule_end"
                  required
                  colSpan="sm:col-span-3"
                  description="Campaign will be automatically stopped at this time."
                >
                  <input
                    id="schedule_end"
                    type="datetime-local"
                    value={scheduleEnd}
                    onChange={e => setScheduleEnd(e.target.value)}
                    min={scheduleStart || defaultDatetime(10)}
                    required
                    className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </FormField>
              </>
            )}
          </FormSection>
        </FormLayout>
      </div>
    </div>
  )
}
