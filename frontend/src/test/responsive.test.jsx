// @vitest-environment jsdom
/**
 * EF18 — Responsive design (WCAG mobile, viewport cible 375 px)
 *
 * Les tests vérifient que les composants principaux appliquent
 * des classes utilitaires Tailwind responsives (sm:, lg:, flex-col, etc.)
 * garantissant l'adaptation de la mise en page sur mobile.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

vi.mock('../contexts/UserContext')
vi.mock('../services/campaignsService')
vi.mock('../services/templatesService')
vi.mock('../services/tenantsService')

import * as UserContext from '../contexts/UserContext'
import * as campaignsService from '../services/campaignsService'
import * as templatesService from '../services/templatesService'
import * as tenantsService from '../services/tenantsService'

import Dashboard from '../pages/protected/Dashboard'

const wrap = (ui) => render(<BrowserRouter>{ui}</BrowserRouter>)

describe('EF18 — Responsive design (classes Tailwind sm:/lg:)', () => {
  beforeEach(() => {
    vi.spyOn(UserContext, 'useUser').mockReturnValue({
      user: { first_name: 'Diogo', email: 'diogo@example.com' },
      isAdmin: () => false,
    })
    vi.spyOn(campaignsService, 'getCampaigns').mockResolvedValue([
      { id: 1, name: 'Campagne test', status: 'running', created_at: '2025-01-01T10:00:00Z' },
    ])
    vi.spyOn(templatesService, 'getTemplates').mockResolvedValue([{ id: 1, name: 'Template' }])
    vi.spyOn(tenantsService, 'getTenants').mockResolvedValue([])
  })

  it('la grille de stats utilise des breakpoints responsifs (sm: lg:)', async () => {
    const { container } = wrap(<Dashboard />)
    await waitFor(() => expect(container.textContent).toContain('Welcome back'))

    expect(container.innerHTML).toContain('sm:grid-cols-2')
    expect(container.innerHTML).toContain('lg:grid-cols-4')
  })

  it('le bloc CTA passe de colonne à ligne sur desktop (sm:flex-row)', async () => {
    const { container } = wrap(<Dashboard />)
    await waitFor(() => expect(container.textContent).toContain('Ready to create'))

    expect(container.innerHTML).toContain('sm:flex-row')
  })

  it('la section contenu utilise une grille responsive à 2 colonnes (lg:grid-cols-2)', async () => {
    const { container } = wrap(<Dashboard />)
    await waitFor(() => expect(container.textContent).toContain('Recent Campaigns'))

    expect(container.innerHTML).toContain('lg:grid-cols-2')
  })
})
