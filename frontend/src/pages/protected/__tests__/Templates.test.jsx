import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Templates from '../Templates'
import * as templatesService from '../../../services/templatesService'
import * as UserContext from '../../../contexts/UserContext'

vi.mock('../../../services/templatesService')
vi.mock('../../../contexts/UserContext')

vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

const mockTemplates = [
  {
    id: 1,
    name: 'Security Awareness Template',
    is_global: true,
    tenant_id: null,
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Phishing Test Template',
    is_global: false,
    tenant_id: 1,
    created_at: '2024-01-20T14:30:00Z'
  }
]

const mockTemplateDetails = {
  id: 1,
  name: 'Security Awareness Template',
  created_at: '2024-01-15T10:00:00Z',
  email_template: {
    id: 1,
    name: 'Test Email',
    subject: 'Security Alert',
    html: '<p>Test content</p>'
  },
  landing_page: {
    id: 1,
    name: 'Test Landing',
    html: '<p>Landing page</p>',
    redirect_url: 'https://example.com'
  }
}

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Templates Page — EF07 (template management, admin-only writes)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
    vi.spyOn(templatesService, 'getTemplate').mockResolvedValue(mockTemplateDetails)
  })

  describe('User View', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => false,
        hasPermission: () => false,
      })
    })

    it('should render templates grid for regular users', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.getByText('Security Awareness Template')).toBeInTheDocument()
        expect(screen.getByText('Phishing Test Template')).toBeInTheDocument()
      })
    })

    it('should not show admin buttons for regular users', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.queryByText('Create Template')).not.toBeInTheDocument()
        expect(screen.queryByRole('button', { name: /edit template/i })).not.toBeInTheDocument()
      })
    })

    it('should display empty state when no templates', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue([])
      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.getByText('No templates')).toBeInTheDocument()
        expect(screen.getByText('No templates available yet.')).toBeInTheDocument()
      })
    })
  })

  describe('Admin View', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => true,
        hasPermission: () => false,
      })
      // Both templates global so admin can manage them
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(
        mockTemplates.map(t => ({ ...t, is_global: true, tenant_id: null }))
      )
    })

    it('should show create template button for admins', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.getByText('Create Template')).toBeInTheDocument()
      })
    })

    it('should show edit and delete buttons for global templates', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const editButtons = screen.getAllByRole('button', { name: /edit template/i })
        const deleteButtons = screen.getAllByRole('button', { name: /delete template/i })
        expect(editButtons).toHaveLength(2)
        expect(deleteButtons).toHaveLength(2)
      })
    })

    it('should open create modal when create button is clicked', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const createButton = screen.getByText('Create Template')
        fireEvent.click(createButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Create New Template')).toBeInTheDocument()
      })
    })

    it('should open edit modal with pre-filled data', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const editButton = screen.getAllByRole('button', { name: /edit template/i })[0]
        fireEvent.click(editButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Edit Template')).toBeInTheDocument()
        expect(templatesService.getTemplate).toHaveBeenCalledWith(1)
      })
    })
  })

  describe('Error Handling', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => false,
        hasPermission: () => false,
      })
    })

    it('should display error message when fetch fails', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockRejectedValue(
        new Error('Failed to fetch templates')
      )

      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.getByText('Failed to fetch templates')).toBeInTheDocument()
      })
    })
  })
})
