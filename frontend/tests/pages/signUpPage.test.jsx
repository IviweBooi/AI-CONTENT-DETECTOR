import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import SignUpPage from '../../src/pages/signUpPage';
import { AuthContext } from '../../src/contexts/AuthContext';

// Mock the detect icon
jest.mock('../../src/assets/icons/detect.svg', () => 'detect-icon.svg');

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Create a wrapper component with AuthContext and Router
const createWrapper = (authContextValue) => {
  return ({ children }) => (
    <BrowserRouter>
      <AuthContext.Provider value={authContextValue}>
        {children}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('SignUpPage Component', () => {
  const mockSignUp = jest.fn();
  const mockSignInWithGoogle = jest.fn();
  const mockSignInWithGitHub = jest.fn();
  const mockClearError = jest.fn();

  const defaultAuthContext = {
    signUp: mockSignUp,
    signInWithGoogle: mockSignInWithGoogle,
    signInWithGitHub: mockSignInWithGitHub,
    clearError: mockClearError,
    error: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
    // Clear localStorage to prevent test interference
    localStorage.clear();
  });

  test('renders the sign up form with all elements', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    // Check for main elements
    expect(screen.getByText('Create your account')).toBeInTheDocument();
    expect(screen.getByText('Join thousands of users detecting AI content')).toBeInTheDocument();
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    expect(screen.getByText('Create account')).toBeInTheDocument();
    expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    expect(screen.getByText('Continue with GitHub')).toBeInTheDocument();
    expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    expect(screen.getByText('Sign in')).toBeInTheDocument();
  });

  test('handles full name input validation', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const nameInput = screen.getByLabelText('Full Name');
    
    // Test empty name
    fireEvent.change(nameInput, { target: { value: '' } });
    fireEvent.blur(nameInput);

    await waitFor(() => {
      expect(screen.getByText('Please enter your full name')).toBeInTheDocument();
    });

    // Test valid name
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.blur(nameInput);

    await waitFor(() => {
      expect(screen.queryByText('Please enter your full name')).not.toBeInTheDocument();
    });
  });

  test('handles email input validation', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const emailInput = screen.getByLabelText('Email');
    
    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });

    // Test valid email
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.blur(emailInput);

    await waitFor(() => {
      expect(screen.queryByText('Please enter a valid email address')).not.toBeInTheDocument();
    });
  });

  test('handles password input validation', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    
    // Test short password
    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
    });

    // Test valid password
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.queryByText('Password must be at least 8 characters long')).not.toBeInTheDocument();
    });
  });

  test('handles password confirmation validation', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    
    // Set password first
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    
    // Test mismatched confirmation
    fireEvent.change(confirmPasswordInput, { target: { value: 'different' } });
    fireEvent.blur(confirmPasswordInput);

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });

    // Test matching confirmation
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.blur(confirmPasswordInput);

    await waitFor(() => {
      expect(screen.queryByText('Passwords do not match')).not.toBeInTheDocument();
    });
  });

  test('toggles password visibility', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const toggleButtons = screen.getAllByLabelText('Show password');

    // Initially passwords should be hidden
    expect(passwordInput.type).toBe('password');
    expect(confirmPasswordInput.type).toBe('password');

    // Click to show password
    fireEvent.click(toggleButtons[0]);
    expect(passwordInput.type).toBe('text');

    // Click to show confirm password
    fireEvent.click(toggleButtons[1]);
    expect(confirmPasswordInput.type).toBe('text');

    // Click to hide passwords again
    fireEvent.click(toggleButtons[0]);
    fireEvent.click(toggleButtons[1]);
    expect(passwordInput.type).toBe('password');
    expect(confirmPasswordInput.type).toBe('password');
  });

  test('disables submit button when form is invalid', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const submitButton = screen.getByText('Create account').closest('button');
    
    // Initially disabled (empty form)
    expect(submitButton).toBeDisabled();

    // Fill all fields with valid data
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const termsCheckbox = screen.getByLabelText(/I agree to the Terms of Service/);

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.click(termsCheckbox);

    expect(screen.getByText('Create account').closest('button')).not.toBeDisabled();
  });

  test('submits form with valid data', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const termsCheckbox = screen.getByRole('checkbox');
    const submitButton = screen.getByText('Create account').closest('button');

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.click(termsCheckbox);
    fireEvent.click(submitButton);

    expect(mockSignUp).toHaveBeenCalledWith('test@example.com', 'Password123', 'John Doe');
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('handles sign up error', async () => {
    const error = { code: 'auth/email-already-in-use' };
    mockSignUp.mockRejectedValueOnce(error);
    
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const termsCheckbox = screen.getByRole('checkbox');
    const submitButton = screen.getByText('Create account').closest('button');

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.click(termsCheckbox);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/An account with this email already exists/)).toBeInTheDocument();
    });
  });

  test('handles Google sign up', async () => {
    mockSignInWithGoogle.mockResolvedValueOnce();
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const googleButton = screen.getByText('Continue with Google').closest('button');
    fireEvent.click(googleButton);

    await waitFor(() => {
      expect(mockSignInWithGoogle).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('handles GitHub sign up', async () => {
    mockSignInWithGitHub.mockResolvedValueOnce();
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const githubButton = screen.getByText('Continue with GitHub').closest('button');
    fireEvent.click(githubButton);

    await waitFor(() => {
      expect(mockSignInWithGitHub).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('shows loading state during sign up', async () => {
    mockSignUp.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');
    const termsCheckbox = screen.getByRole('checkbox');
    const submitButton = screen.getByText('Create account').closest('button');

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.click(termsCheckbox);
    fireEvent.click(submitButton);

    // Check loading state
    expect(screen.getByText('Creating account...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText('Creating account...')).not.toBeInTheDocument();
    });
  });

  test('handles terms and conditions checkbox', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const termsCheckbox = screen.getByLabelText(/I agree to the Terms of Service/);
    const submitButton = screen.getByText('Create account').closest('button');
    
    // Initially unchecked and button disabled
    expect(termsCheckbox).not.toBeChecked();

    // Fill all other fields
    const nameInput = screen.getByLabelText('Full Name');
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const confirmPasswordInput = screen.getByLabelText('Confirm Password');

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });

    // Still disabled without terms acceptance
    expect(submitButton).toBeDisabled();

    // Check terms and conditions
    fireEvent.click(termsCheckbox);
    expect(termsCheckbox).toBeChecked();
    expect(submitButton).not.toBeDisabled();
  });

  test('displays auth context error', () => {
    const authContextWithError = {
      ...defaultAuthContext,
      error: 'Registration failed',
    };
    
    const Wrapper = createWrapper(authContextWithError);
    render(<SignUpPage />, { wrapper: Wrapper });

    expect(screen.getByText('Registration failed')).toBeInTheDocument();
  });

  test('navigates back when back button is clicked', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const backButton = screen.getByLabelText('Go back');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  test('validates password strength requirements', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignUpPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    
    // Test weak password
    fireEvent.change(passwordInput, { target: { value: 'weak' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
    });

    // Test strong password
    fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.queryByText('Password must be at least 8 characters long')).not.toBeInTheDocument();
    });
  });
});