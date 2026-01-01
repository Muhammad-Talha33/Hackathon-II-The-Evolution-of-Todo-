'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { api, SignupRequest, SigninRequest } from '@/lib/api';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  signup: (data: SignupRequest) => Promise<void>;
  signin: (data: SigninRequest) => Promise<void>;
  signout: () => void;
  getAccessToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user has valid access token on mount
    const accessToken = Cookies.get('access_token');
    setIsAuthenticated(!!accessToken);
    setIsLoading(false);
  }, []);

  const signup = async (data: SignupRequest) => {
    try {
      const response = await api.signup(data);

      // Store tokens in cookies
      Cookies.set('access_token', response.access_token, { expires: 1/96 }); // 15 minutes
      Cookies.set('refresh_token', response.refresh_token, { expires: 7 }); // 7 days

      setIsAuthenticated(true);
      router.push('/tasks');
    } catch (error) {
      throw error;
    }
  };

  const signin = async (data: SigninRequest) => {
    try {
      const response = await api.signin(data);

      // Store tokens in cookies
      Cookies.set('access_token', response.access_token, { expires: 1/96 }); // 15 minutes
      Cookies.set('refresh_token', response.refresh_token, { expires: 7 }); // 7 days

      setIsAuthenticated(true);
      router.push('/tasks');
    } catch (error) {
      throw error;
    }
  };

  const signout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    setIsAuthenticated(false);
    router.push('/auth/signin');
  };

  const getAccessToken = () => {
    return Cookies.get('access_token') || null;
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        signup,
        signin,
        signout,
        getAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
