"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authApi, AuthUser } from "@/lib/api";

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (response: any) => void;
  logout: () => void;
  showAuthModal: () => void;
  isAuthModalOpen: boolean;
  setIsAuthModalOpen: (isOpen: boolean) => void;
}

import { GoogleOAuthProvider } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("access_token");
      if (token && token !== "undefined") {
        try {
          const profile = await authApi.getProfile(token);
          setUser(profile);
        } catch (error) {
          console.error("Failed to load profile", error);
          localStorage.removeItem("access_token");
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = (response: any) => {
    setUser(response.user);
    localStorage.setItem("access_token", response.access_token);
    setIsAuthModalOpen(false);
  };

  const logout = async () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        await authApi.logout(token);
      } catch (e) {
        console.error("Logout API error", e);
      }
    }
    setUser(null);
    localStorage.removeItem("access_token");
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
