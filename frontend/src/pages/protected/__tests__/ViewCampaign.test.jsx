import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ViewCampaign from '../ViewCampaign'
import * as campaignsService from '../../../services/campaignsService'

// Mock the services
vi.mock('../../../services/campaignsService')

// Mock the date utils
vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

// Mock useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: '1' })
  }
})

const mockCampaign = {
  id: 1,
  name: 'Security Awareness Campaign',
  status: 'running',
  template_id: 5,
  tenant_id: 10,
  created_at: '2024-01-15T10:00:00Z',
  launched_at: '2024-01-16T09:00:00Z',
  stopped_at: null
}

const mockSummary = {
  summary: {
    total: 100,
    sent: 98,
    opened: 75,
    clicked: 45,
    submitted_data: 12,
    email_reported: 8,
    error: 2
  },
  results: [
    {
      id: 'test123',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      status: 'Submitted Data',
      ip: '192.168.1.1'
    },
    {
      id: 'test456',
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane.smith@example.com',
      status: 'Error',
      ip: ''
    }
  ]
}

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      <Routes>
        <Route path="*" element={component} />
      </Routes>
    </BrowserRouter>
  )
}

describe('ViewCampaign Page — EF08 (campaign detail), EF13 (live stats per target)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(campaignsService, 'getCampaign').mockResolvedValue(mockCampaign)
    vi.spyOn(campaignsService, 'getCampaignSummary').mockResolvedValue(mockSummary)
  })

  it('should render campaign details', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Security Awareness Campaign')).toBeInTheDocument()
      expect(screen.getByText(/ID: 1/)).toBeInTheDocument()
    })
  })

  it('should display campaign status', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      // Use getAllByText since status appears in header badge
      const statusElements = screen.getAllByText('Running')
      expect(statusElements.length).toBeGreaterThan(0)
    })
  })

  it('should render statistics cards', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Total Recipients')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('Emails Opened')).toBeInTheDocument()
      expect(screen.getByText('75')).toBeInTheDocument()
      expect(screen.getByText('Links Clicked')).toBeInTheDocument()
      expect(screen.getByText('45')).toBeInTheDocument()
      // "Submitted Data" appears in both stats card and results table, so use getAllByText
      const submittedDataElements = screen.getAllByText('Submitted Data')
      expect(submittedDataElements.length).toBeGreaterThan(0)
      expect(screen.getByText('12')).toBeInTheDocument()
    })
  })

  it('should calculate and display percentages', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('75.0% open rate')).toBeInTheDocument()
      expect(screen.getByText('45.0% click rate')).toBeInTheDocument()
      expect(screen.getByText('12.0% submission rate')).toBeInTheDocument()
    })
  })

  it('should display campaign overview details', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Campaign Overview')).toBeInTheDocument()
      expect(screen.getByText('Template ID')).toBeInTheDocument()
      expect(screen.getByText('Tenant ID')).toBeInTheDocument()
    })
  })

  it('should display timeline information', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Timeline')).toBeInTheDocument()
      expect(screen.getByText('Created')).toBeInTheDocument()
      expect(screen.getByText('Launched')).toBeInTheDocument()
      expect(screen.getByText('Stopped')).toBeInTheDocument()
      expect(screen.getByText('Still active')).toBeInTheDocument()
    })
  })

  it('should display detailed statistics', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Detailed Statistics')).toBeInTheDocument()
      expect(screen.getByText('Emails Sent')).toBeInTheDocument()
      expect(screen.getByText('98')).toBeInTheDocument()
      expect(screen.getByText('Emails Reported')).toBeInTheDocument()
      expect(screen.getByText('8')).toBeInTheDocument()
      expect(screen.getByText('Errors')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  it('should show back to campaigns link', async () => {
    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Back to Campaigns')).toBeInTheDocument()
    })
  })

  it('should handle campaign not found', async () => {
    vi.spyOn(campaignsService, 'getCampaign').mockRejectedValue(
      new Error('Campaign not found')
    )

    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      expect(screen.getByText('Campaign not found')).toBeInTheDocument()
    })
  })

  it('should handle summary fetch failure gracefully', async () => {
    vi.spyOn(campaignsService, 'getCampaignSummary').mockRejectedValue(
      new Error('Failed to fetch summary')
    )

    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      // Should still display campaign name
      expect(screen.getByText('Security Awareness Campaign')).toBeInTheDocument()
      // Should show no statistics message
      expect(screen.getByText('No campaign statistics available yet')).toBeInTheDocument()
    })
  })

  it('should show loading state initially', () => {
    renderWithRouter(<ViewCampaign />)
    expect(screen.getByText('Loading campaign...')).toBeInTheDocument()
  })

  it('should display different status badges correctly', async () => {
    const completedCampaign = { ...mockCampaign, status: 'completed' }
    vi.spyOn(campaignsService, 'getCampaign').mockResolvedValue(completedCampaign)

    renderWithRouter(<ViewCampaign />)

    await waitFor(() => {
      // "Completed" appears in both header badge and overview section, so use getAllByText
      const completedElements = screen.getAllByText('Completed')
      expect(completedElements.length).toBeGreaterThan(0)
    })
  })
})
