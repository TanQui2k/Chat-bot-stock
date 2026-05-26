"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authApi, AuthUser, AuthResponse } from "@/lib/api";
import { GoogleOAuthProvider } from "@react-oauth/google";

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (response: AuthResponse) => void;
  logout: () => void;
  showAuthModal: () => void;
  isAuthModalOpen: boolean;
  setIsAuthModalOpen: (isOpen: boolean) => void;
}

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const profile = await authApi.getProfile();
        setUser(profile);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = (response: AuthResponse) => {
    setUser(response.user);
    setIsAuthModalOpen(false);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      console.error("Logout API error", e);
    } finally {
      setUser(null);
    }
  };

  const showAuthModal = () => setIsAuthModalOpen(true);

  const contextValue = {
    user,
    isLoading,
    login,
    logout,
    showAuthModal,
    isAuthModalOpen,
    setIsAuthModalOpen,
  };

  const content = (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );

  return GOOGLE_CLIENT_ID ? (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      {content}
    </GoogleOAuthProvider>
  ) : content;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
