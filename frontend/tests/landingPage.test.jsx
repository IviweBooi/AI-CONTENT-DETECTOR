import { render, screen } from '@testing-library/react'
import LandingPage from '../src/pages/landingPage.jsx'
import { MemoryRouter } from 'react-router-dom'

it('renders the hero badge text', () => {
  render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>
  )
  expect(screen.getByText(/Academic Integrity/i)).toBeInTheDocument()
})
