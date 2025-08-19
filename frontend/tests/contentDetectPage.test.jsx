import { render, screen, fireEvent } from '@testing-library/react'
import ContentDetectPage from '../src/pages/contentDetectPage.jsx'

function setTextarea(val) {
  const ta = screen.getByPlaceholderText(/Paste or type your content/i)
  fireEvent.change(ta, { target: { value: val } })
}

beforeEach(() => {
  // Reset localStorage counter for deterministic tests
  const today = new Date().toISOString().slice(0, 10)
  localStorage.setItem('aicd_daily_counter', JSON.stringify({ date: today, used: 0 }))
})

it('disables Analyze button until minimum characters are entered', () => {
  render(<ContentDetectPage />)
  const btn = screen.getByRole('button', { name: /Analyze/i })
  expect(btn).toBeDisabled()

  setTextarea('a'.repeat(51))
  expect(btn).not.toBeDisabled()
})

it('shows remaining daily submissions message when analyzing under limit', async () => {
  render(<ContentDetectPage />)
  setTextarea('a'.repeat(60))
  const btn = screen.getByRole('button', { name: /Analyze/i })
  fireEvent.click(btn)
  // Accept either the immediate or post-submit variant
  expect(await screen.findByText(/submissions remaining/i)).toBeInTheDocument()
})
