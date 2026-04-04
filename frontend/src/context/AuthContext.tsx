"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
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
      } catch (error: unknown) {
        // Not logged in or session expired - silent failure during init
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

  if (!GOOGLE_CLIENT_ID) {
    return (
      <AuthContext.Provider 
        value={{ 
          user, 
          isLoading, 
          login, 
          logout, 
          showAuthModal, 
          isAuthModalOpen, 
          setIsAuthModalOpen 
        }}
      >
        <div className="bg-amber-900/20 border border-amber-500/50 p-4 rounded-lg m-4 text-amber-200 text-sm">
          <strong>Lỗi cấu hình:</strong> Cần đặt biến môi trường <code>NEXT_PUBLIC_GOOGLE_CLIENT_ID</code> để sử dụng tính năng Google Auth.
        </div>
        {children}
      </AuthContext.Provider>
    );
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthContext.Provider 
        value={{ 
          user, 
          isLoading, 
          login, 
          logout, 
          showAuthModal, 
          isAuthModalOpen, 
          setIsAuthModalOpen 
        }}
      >
        {children}
      </AuthContext.Provider>
    </GoogleOAuthProvider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
