import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import Signup from '../page'

describe('Signup Page', () => {
  it('renders the signup form', () => {
    render(<Signup />)
    expect(screen.getByLabelText(/Company name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Full name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument()
  })

  it('validates form inputs', async () => {
    render(<Signup />)
    fireEvent.click(screen.getByRole('button', { name: /Sign Up/i }))
    expect(await screen.findAllByRole('alert')).toHaveLength(4) // Assuming all fields are required
  })
})
