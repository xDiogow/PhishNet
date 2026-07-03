// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { axe, toHaveNoViolations } from 'jest-axe'
import CaughtPage from '../CaughtPage'

expect.extend(toHaveNoViolations)

const renderCaught = (search = '') =>
  render(
    <MemoryRouter initialEntries={[`/caught${search}`]}>
      <CaughtPage />
    </MemoryRouter>
  )

describe('CaughtPage — vue "phished" (sans ?reported)', () => {
  it('affiche le titre d\'échec', () => {
    renderCaught()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'You fell for a phishing attack'
    )
  })

  it('affiche le badge rouge de simulation', () => {
    renderCaught()
    expect(screen.getByText(/Phishing Simulation — You submitted your credentials/i)).toBeInTheDocument()
  })

  it('affiche la section "What just happened"', () => {
    renderCaught()
    expect(screen.getByRole('heading', { name: /what just happened/i })).toBeInTheDocument()
  })

  it('affiche la section "Red flags"', () => {
    renderCaught()
    expect(screen.getByRole('heading', { name: /red flags you may have missed/i })).toBeInTheDocument()
  })

  it('affiche la section "How to spot it next time"', () => {
    renderCaught()
    expect(screen.getByRole('heading', { name: /how to spot it next time/i })).toBeInTheDocument()
  })

  it('affiche le lien ANSSI', () => {
    renderCaught()
    expect(screen.getByRole('link', { name: /anssi phishing guide/i })).toBeInTheDocument()
  })

  it('affiche le lien phishing.fr', () => {
    renderCaught()
    expect(screen.getByRole('link', { name: /phishing\.fr/i })).toBeInTheDocument()
  })

  it('mentionne qu\'aucun credential n\'a été stocké', () => {
    renderCaught()
    expect(screen.getAllByText(/no credentials were stored/i).length).toBeGreaterThan(0)
  })

  it('n\'affiche pas la page verte "Good job"', () => {
    renderCaught()
    expect(screen.queryByText(/great job — you spotted it/i)).not.toBeInTheDocument()
  })

  it('ne doit pas avoir de violations axe (WCAG 2.1 AA)', async () => {
    const { container } = renderCaught()
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})

describe('CaughtPage — vue "reported" (?reported=true)', () => {
  it('affiche le titre de félicitations', () => {
    renderCaught('?reported=true')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Great job — you spotted it!'
    )
  })

  it('affiche le badge vert de signalement', () => {
    renderCaught('?reported=true')
    expect(screen.getByText(/Phishing Simulation — You reported this email/i)).toBeInTheDocument()
  })

  it('affiche la section "Why this matters"', () => {
    renderCaught('?reported=true')
    expect(screen.getByRole('heading', { name: /why this matters/i })).toBeInTheDocument()
  })

  it('affiche le lien ANSSI', () => {
    renderCaught('?reported=true')
    expect(screen.getByRole('link', { name: /anssi phishing guide/i })).toBeInTheDocument()
  })

  it('mentionne qu\'aucun credential n\'a été stocké', () => {
    renderCaught('?reported=true')
    expect(screen.getAllByText(/no credentials were stored/i).length).toBeGreaterThan(0)
  })

  it('n\'affiche pas la page rouge d\'échec', () => {
    renderCaught('?reported=true')
    expect(screen.queryByText(/you fell for a phishing attack/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/what just happened/i)).not.toBeInTheDocument()
  })

  it('ne doit pas avoir de violations axe (WCAG 2.1 AA)', async () => {
    const { container } = renderCaught('?reported=true')
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
