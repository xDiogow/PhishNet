import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Templates from '../Templates'
import * as templatesService from '../../../services/templatesService'
import * as UserContext from '../../../contexts/UserContext'

// Mock the services
vi.mock('../../../services/templatesService')
vi.mock('../../../contexts/UserContext')

// Mock the date utils
vi.mock('../../../utils/dateUtils', () => ({
  formatDate: (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
}))

const mockTemplates = [
  {
    id: 1,
    name: 'Security Awareness Template',
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    name: 'Phishing Test Template',
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

describe('Templates Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
    vi.spyOn(templatesService, 'getTemplate').mockResolvedValue(mockTemplateDetails)
  })

  describe('User View', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => false
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
      })
    })

    it('should show view details button', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const viewButtons = screen.getAllByText('View Details')
        expect(viewButtons).toHaveLength(2)
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
        isAdmin: () => true
      })
    })

    it('should show create template button for admins', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        expect(screen.getByText('Create Template')).toBeInTheDocument()
      })
    })

    it('should show edit and delete buttons for admins', async () => {
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
  })

  describe('View Template Modal', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => false
      })
    })

    it('should open view modal when view details is clicked', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const viewButton = screen.getAllByText('View Details')[0]
        fireEvent.click(viewButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Template Details')).toBeInTheDocument()
        expect(templatesService.getTemplate).toHaveBeenCalledWith(1)
      })
    })

    it('should display template details in modal', async () => {
      renderWithRouter(<Templates />)

      await waitFor(() => {
        const viewButton = screen.getAllByText('View Details')[0]
        fireEvent.click(viewButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Email Template')).toBeInTheDocument()
        expect(screen.getByText('Landing Page')).toBeInTheDocument()
        expect(screen.getByText('Security Alert')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        isAdmin: () => false
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
