import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import SignInPage from '../../src/pages/signInPage';
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

describe('SignInPage Component', () => {
  const mockSignIn = jest.fn();
  const mockSignInWithGoogle = jest.fn();
  const mockSignInWithGitHub = jest.fn();
  const mockClearError = jest.fn();

  const defaultAuthContext = {
    signIn: mockSignIn,
    signInWithGoogle: mockSignInWithGoogle,
    signInWithGitHub: mockSignInWithGitHub,
    clearError: mockClearError,
    error: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  test('renders the sign in form with all elements', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    // Check for main elements
    expect(screen.getByText('Welcome back')).toBeInTheDocument();
    expect(screen.getByText('Sign in to continue to your dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByText('Sign in')).toBeInTheDocument();
    expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    expect(screen.getByText('Continue with GitHub')).toBeInTheDocument();
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
    expect(screen.getByText('Create one')).toBeInTheDocument();
  });

  test('handles email input validation', async () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

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
    render(<SignInPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    
    // Test short password
    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 6 characters long')).toBeInTheDocument();
    });

    // Test valid password
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.blur(passwordInput);

    await waitFor(() => {
      expect(screen.queryByText('Password must be at least 6 characters long')).not.toBeInTheDocument();
    });
  });

  test('toggles password visibility', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const passwordInput = screen.getByLabelText('Password');
    const toggleButton = screen.getByLabelText('Show password');

    // Initially password should be hidden
    expect(passwordInput.type).toBe('password');

    // Click to show password
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('text');

    // Click to hide password again
    fireEvent.click(toggleButton);
    expect(passwordInput.type).toBe('password');
  });

  test('disables submit button when form is invalid', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const submitButton = screen.getByText('Sign in').closest('button');
    
    // Initially disabled (empty form)
    expect(submitButton).toBeDisabled();

    // Fill only email
    const emailInput = screen.getByLabelText('Email');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    expect(submitButton).toBeDisabled();

    // Fill both email and password
    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    expect(submitButton).not.toBeDisabled();
  });

  test('submits form with valid credentials', async () => {
    mockSignIn.mockResolvedValueOnce();
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByText('Sign in').closest('button');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('handles sign in error', async () => {
    const error = { code: 'auth/user-not-found' };
    mockSignIn.mockRejectedValueOnce(error);
    
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByText('Sign in').closest('button');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/No account found with this email address/)).toBeInTheDocument();
    });
  });

  test('handles Google sign in', async () => {
    mockSignInWithGoogle.mockResolvedValueOnce();
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const googleButton = screen.getByText('Continue with Google').closest('button');
    fireEvent.click(googleButton);

    await waitFor(() => {
      expect(mockSignInWithGoogle).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('handles GitHub sign in', async () => {
    mockSignInWithGitHub.mockResolvedValueOnce();
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const githubButton = screen.getByText('Continue with GitHub').closest('button');
    fireEvent.click(githubButton);

    await waitFor(() => {
      expect(mockSignInWithGitHub).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/content-detect');
    });
  });

  test('shows loading state during sign in', async () => {
    mockSignIn.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByText('Sign in').closest('button');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Check loading state
    expect(screen.getByText('Signing in…')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText('Signing in…')).not.toBeInTheDocument();
    });
  });

  test('handles remember me checkbox', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const rememberMeCheckbox = screen.getByLabelText('Remember me');
    
    // Initially unchecked
    expect(rememberMeCheckbox).not.toBeChecked();

    // Click to check
    fireEvent.click(rememberMeCheckbox);
    expect(rememberMeCheckbox).toBeChecked();

    // Click to uncheck
    fireEvent.click(rememberMeCheckbox);
    expect(rememberMeCheckbox).not.toBeChecked();
  });

  test('displays auth context error', () => {
    const authContextWithError = {
      ...defaultAuthContext,
      error: 'Authentication failed',
    };
    
    const Wrapper = createWrapper(authContextWithError);
    render(<SignInPage />, { wrapper: Wrapper });

    expect(screen.getByText('Authentication failed')).toBeInTheDocument();
  });

  test('navigates back when back button is clicked', () => {
    const Wrapper = createWrapper(defaultAuthContext);
    render(<SignInPage />, { wrapper: Wrapper });

    const backButton = screen.getByLabelText('Go back');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });
});