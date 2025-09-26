import React, { createContext, useContext } from 'react';

// Mock AuthContext for testing
export const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: null,
      signIn: jest.fn(),
      signUp: jest.fn(),
      signOut: jest.fn(),
      signInWithGoogle: jest.fn(),
      signInWithGitHub: jest.fn(),
      clearError: jest.fn(),
      error: null,
      loading: false
    };
  }
  return context;
};

export const AuthProvider = ({ children, value }) => {
  const defaultValue = {
    user: null,
    signIn: jest.fn(),
    signUp: jest.fn(),
    signOut: jest.fn(),
    signInWithGoogle: jest.fn(),
    signInWithGitHub: jest.fn(),
    clearError: jest.fn(),
    error: null,
    loading: false,
    ...value
  };

  return (
    <AuthContext.Provider value={defaultValue}>
      {children}
    </AuthContext.Provider>
  );
};