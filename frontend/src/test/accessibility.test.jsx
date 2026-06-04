// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { BrowserRouter } from 'react-router-dom'

expect.extend(toHaveNoViolations)

vi.mock('../contexts/UserContext')
vi.mock('../services/authService')
vi.mock('../services/campaignsService')
vi.mock('../services/templatesService')
vi.mock('../services/tenantsService')

import * as UserContext from '../contexts/UserContext'
import * as campaignsService from '../services/campaignsService'
import * as templatesService from '../services/templatesService'
import * as tenantsService from '../services/tenantsService'

import Login from '../pages/public/Login'
import Dashboard from '../pages/protected/Dashboard'

const wrap = (ui) => render(<BrowserRouter>{ui}</BrowserRouter>)

describe('Accessibilité — pages principales (RGAA / WCAG 2.1 AA)', () => {
  describe('Login', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({ setUser: vi.fn() })
    })

    it('ne doit pas avoir de violations axe', async () => {
      const { container } = wrap(<Login />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('Dashboard', () => {
    beforeEach(() => {
      vi.spyOn(UserContext, 'useUser').mockReturnValue({
        user: { first_name: 'Diogo', email: 'diogo@example.com' },
        isAdmin: () => false,
      })
      vi.spyOn(campaignsService, 'getCampaigns').mockResolvedValue([
        { id: 1, name: 'Campagne test', status: 'running', created_at: '2025-01-01T10:00:00Z' },
      ])
      vi.spyOn(templatesService, 'getTemplates').mockResolvedValue([
        { id: 1, name: 'Template test' },
      ])
      vi.spyOn(tenantsService, 'getTenants').mockResolvedValue([])
    })

    it('ne doit pas avoir de violations axe (état chargé)', async () => {
      const { container } = wrap(<Dashboard />)
      await waitFor(() => expect(container.textContent).toContain('Welcome back'))
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})
