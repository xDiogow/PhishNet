import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Tenants from '../Tenants'
import * as tenantsService from '../../../services/tenantsService'
import * as invitationsService from '../../../services/invitationsService'

// Mock the services
vi.mock('../../../services/tenantsService')
vi.mock('../../../services/invitationsService')

// Mock the date utils
vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

const mockTenants = [
  {
    id: 1,
    name: 'Acme Corporation',
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'TechCorp Inc',
    created_at: '2024-01-20T14:30:00Z'
  }
]

const mockInvitations = [
  {
    id: 1,
    invitation_code: 'ABC123XYZ',
    tenant_id: 1,
    is_used: false,
    is_valid: true,
    created_at: '2024-01-15T10:00:00Z',
    expires_at: '2024-02-15T10:00:00Z'
  },
  {
    id: 2,
    invitation_code: 'DEF456UVW',
    tenant_id: 1,
    is_used: true,
    is_valid: false,
    created_at: '2024-01-10T10:00:00Z',
    used_at: '2024-01-12T10:00:00Z'
  }
]

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Tenants Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(tenantsService, 'getTenants').mockResolvedValue(mockTenants)
    vi.spyOn(invitationsService, 'getInvitationsByTenant').mockResolvedValue(mockInvitations)
  })

  it('should render tenants table', async () => {
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      expect(screen.getByText('Acme Corporation')).toBeInTheDocument()
      expect(screen.getByText('TechCorp Inc')).toBeInTheDocument()
    })
  })

  it('should display tenant names correctly', async () => {
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      expect(screen.getByText('Acme Corporation')).toBeInTheDocument()
      expect(screen.getByText('TechCorp Inc')).toBeInTheDocument()
    })
  })

  it('should show create tenant button', async () => {
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      expect(screen.getByText('Create Tenant')).toBeInTheDocument()
    })
  })

  it('should display empty state when no tenants', async () => {
    vi.spyOn(tenantsService, 'getTenants').mockResolvedValue([])
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      expect(screen.getByText('No tenants')).toBeInTheDocument()
      expect(screen.getByText('Get started by creating your first tenant.')).toBeInTheDocument()
    })
  })

  it('should open create modal when create button is clicked', async () => {
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      const createButton = screen.getByText('Create Tenant')
      fireEvent.click(createButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Create New Tenant')).toBeInTheDocument()
    })
  })

  it('should have action buttons for each tenant', async () => {
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      const invitationButtons = screen.getAllByRole('button', { name: /manage invitations for/i })
      const editButtons = screen.getAllByRole('button', { name: /edit tenant/i })
      const deleteButtons = screen.getAllByRole('button', { name: /delete tenant/i })
      expect(invitationButtons).toHaveLength(2)
      expect(editButtons).toHaveLength(2)
      expect(deleteButtons).toHaveLength(2)
    })
  })

  describe('Invitations Modal', () => {
    it('should open invitations modal when key icon is clicked', async () => {
      renderWithRouter(<Tenants />)

      await waitFor(() => {
        const invitationButtons = screen.getAllByRole('button', { name: /manage invitations for/i })
        fireEvent.click(invitationButtons[0])
      })

      await waitFor(() => {
        expect(screen.getByText(/Invitations - Acme Corporation/)).toBeInTheDocument()
        expect(invitationsService.getInvitationsByTenant).toHaveBeenCalledWith(1)
      })
    })

    it('should display invitations list', async () => {
      renderWithRouter(<Tenants />)

      await waitFor(() => {
        const invitationButtons = screen.getAllByRole('button', { name: /manage invitations for/i })
        fireEvent.click(invitationButtons[0])
      })

      await waitFor(() => {
        expect(screen.getByText('ABC123XYZ')).toBeInTheDocument()
        expect(screen.getByText('DEF456UVW')).toBeInTheDocument()
        expect(screen.getByText('Valid')).toBeInTheDocument()
        expect(screen.getByText('Used')).toBeInTheDocument()
      })
    })

    it('should show create invitation button in modal', async () => {
      renderWithRouter(<Tenants />)

      await waitFor(() => {
        const invitationButtons = screen.getAllByRole('button', { name: /manage invitations for/i })
        fireEvent.click(invitationButtons[0])
      })

      await waitFor(() => {
        expect(screen.getByText('Create Invitation')).toBeInTheDocument()
      })
    })
  })

  it('should display error message when fetch fails', async () => {
    vi.spyOn(tenantsService, 'getTenants').mockRejectedValue(
      new Error('Failed to load tenants')
    )
    
    renderWithRouter(<Tenants />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load tenants')).toBeInTheDocument()
    })
  })

  it('should show loading state initially', () => {
    renderWithRouter(<Tenants />)
    expect(screen.getByText('Loading tenants...')).toBeInTheDocument()
  })
})
