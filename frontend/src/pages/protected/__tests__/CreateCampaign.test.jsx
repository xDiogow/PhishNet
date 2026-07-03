import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import CreateCampaign from '../CreateCampaign'
import * as campaignsService from '../../../services/campaignsService'
import * as templatesService from '../../../services/templatesService'
import * as teamService from '../../../services/teamService'

vi.mock('../../../services/campaignsService')
vi.mock('../../../services/templatesService')
vi.mock('../../../services/teamService')

// Mock the headlessui Select to a native <select> — avoids transition/portal issues in happy-dom
vi.mock('../../../components/Select', () => ({
  default: ({ options, value, onChange, placeholder }) => (
    <select
      data-testid="template-select"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">{placeholder}</option>
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  )
}))

const mockNavigate = vi.hoisted(() => vi.fn())
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

const mockTemplates = [
  { id: 1, name: 'Phishing Template 1' },
  { id: 2, name: 'Phishing Template 2' },
]

const mockTargets = [
  { id: 1, first_name: 'Alice', last_name: 'Martin', email: 'alice@example.com' },
  { id: 2, first_name: 'Bob', last_name: 'Dupont', email: 'bob@example.com' },
]

const renderPage = () => render(<BrowserRouter><CreateCampaign /></BrowserRouter>)

describe('CreateCampaign — EF08 (lancement campagne)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(teamService, 'getTargets').mockResolvedValue(mockTargets)
  })

  describe('Chargement des templates', () => {
    it('affiche le loader pendant le chargement', () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      renderPage()
      expect(screen.getByText('Loading templates...')).toBeInTheDocument()
    })

    it('affiche les templates disponibles dans le sélecteur', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      renderPage()
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())
      expect(screen.getByTestId('template-select')).toBeInTheDocument()
      expect(screen.getByText('Phishing Template 1')).toBeInTheDocument()
      expect(screen.getByText('Phishing Template 2')).toBeInTheDocument()
    })

    it('affiche un avertissement si aucun template disponible', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue([])
      renderPage()
      await waitFor(() => expect(screen.getByText(/No templates available/i)).toBeInTheDocument())
      expect(screen.queryByTestId('template-select')).not.toBeInTheDocument()
    })

    it('affiche un avertissement si aucune cible disponible', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      vi.spyOn(teamService, 'getTargets').mockResolvedValue([])
      renderPage()
      await waitFor(() => expect(screen.getByText(/No targets found/i)).toBeInTheDocument())
    })

    it('affiche une alerte si le chargement échoue', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockRejectedValue(new Error('Network error'))
      renderPage()
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText('Network error')).toBeInTheDocument()
      })
    })
  })

  describe('Validation du formulaire', () => {
    it("affiche une erreur si aucun template n'est sélectionné", async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      renderPage()
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())

      fireEvent.change(screen.getByLabelText(/Campaign Name/i), {
        target: { name: 'name', value: 'Test Campaign' },
      })
      fireEvent.click(screen.getByRole('button', { name: /Create Campaign/i }))

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText('Please select a template')).toBeInTheDocument()
      })
      expect(campaignsService.createCampaign).not.toHaveBeenCalled()
    })
  })

  describe('Soumission du formulaire', () => {
    const fillAndSubmit = async () => {
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())
      await waitFor(() => expect(screen.queryByText('Loading targets...')).not.toBeInTheDocument())
      fireEvent.change(screen.getByLabelText(/Campaign Name/i), {
        target: { name: 'name', value: 'Test Campaign' },
      })
      fireEvent.change(screen.getByTestId('template-select'), {
        target: { value: '1' },
      })
      fireEvent.click(screen.getByRole('button', { name: /Create Campaign/i }))
    }

    it('appelle createCampaign avec le bon payload et redirige vers /campaigns', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      vi.spyOn(campaignsService, 'createCampaign').mockResolvedValue({ id: 1 })
      renderPage()
      await fillAndSubmit()
      await waitFor(() => {
        expect(campaignsService.createCampaign).toHaveBeenCalledWith(
          expect.objectContaining({ name: 'Test Campaign', template_id: '1' })
        )
        expect(mockNavigate).toHaveBeenCalledWith('/campaigns')
      })
    })

    it("affiche l'erreur retournée par l'API en cas d'échec", async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      vi.spyOn(campaignsService, 'createCampaign').mockRejectedValue(
        new Error('Server error')
      )
      renderPage()
      await fillAndSubmit()
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText('Server error')).toBeInTheDocument()
      })
      expect(mockNavigate).not.toHaveBeenCalled()
    })

    it('affiche "Creating..." pendant la soumission en cours', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      let resolveCreate
      vi.spyOn(campaignsService, 'createCampaign').mockReturnValue(
        new Promise(resolve => { resolveCreate = resolve })
      )
      renderPage()
      await fillAndSubmit()
      expect(screen.getByText('Creating...')).toBeInTheDocument()
      resolveCreate({ id: 1 })
    })
  })

  describe('Navigation', () => {
    beforeEach(() => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
    })

    it('revient à /campaigns via le bouton Cancel', async () => {
      renderPage()
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())
      fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
      expect(mockNavigate).toHaveBeenCalledWith('/campaigns')
    })

    it('revient à /campaigns via le bouton Back', () => {
      renderPage()
      fireEvent.click(screen.getByRole('button', { name: /Back to Campaigns/i }))
      expect(mockNavigate).toHaveBeenCalledWith('/campaigns')
    })
  })

  describe('Accessibilité', () => {
    it('le champ Campaign Name est marqué required', async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      renderPage()
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())
      expect(screen.getByLabelText(/Campaign Name/i)).toHaveAttribute('required')
    })

    it("l'alerte d'erreur utilise role='alert' pour les lecteurs d'écran", async () => {
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue(mockTemplates)
      renderPage()
      await waitFor(() => expect(screen.queryByText('Loading templates...')).not.toBeInTheDocument())
      // Fill name (required) but omit template — triggers JS validation path
      fireEvent.change(screen.getByLabelText(/Campaign Name/i), {
        target: { name: 'name', value: 'Test Campaign' },
      })
      fireEvent.click(screen.getByRole('button', { name: /Create Campaign/i }))
      await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
    })
  })
})
