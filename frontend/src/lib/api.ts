"use client";

// API Client for StockAI Application
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// ==========================================
// Authentication API
// ==========================================

export interface PhoneVerificationRequest {
  phone_number: string;
}

export interface PhoneVerificationVerify {
  phone_number: string;
  verification_code: string;
}

export interface GoogleLoginRequest {
  id_token: string;
}

export interface AuthUser {
  id: string;
  username?: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
  phone_number?: string;
  phone_verified: boolean;
  google_id?: string;
  auth_providers: string[];
  default_auth_method: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface AuthMethods {
  phone: boolean;
  google: boolean;
  password: boolean;
}

// Auth API
export const authApi = {
  // Phone Authentication
  sendPhoneCode: async (phone: string): Promise<{ message: string; code: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/phone/send-code`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phone }),
    });
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to send verification code");
    }
    return data;
  },

  verifyPhoneCode: async (
    phone: string,
    code: string
  ): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/phone/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: phone,
        verification_code: code,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Invalid verification code");
    }
    return data;
  },

  // Google OAuth
  googleLogin: async (idToken: string): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/google/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: idToken }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Google login failed");
    }
    return data;
  },

  // Password Login
  login: async (
    identifier: string,
    password: string
  ): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Invalid credentials");
    }
    return data;
  },

  // Profile
  getProfile: async (token: string): Promise<AuthUser> => {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to get profile");
    }
    return data;
  },

  getAuthMethods: async (token: string): Promise<AuthMethods> => {
    const response = await fetch(`${API_BASE_URL}/auth/auth-methods`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to get auth methods");
    }
    return data;
  },

  // Logout
  logout: async (token: string): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Logout failed");
    }
    return data;
  },
};

// ==========================================
// Stock API (Existing)
// ==========================================

export interface StockPrice {
  symbol: string;
  price: number;
  currency: string;
  as_of: string;
}

export interface StockInfo {
  symbol: string;
  name?: string;
  price: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  market_cap?: number;
}

export const stockApi = {
  getLatestPrice: async (symbol: string): Promise<StockPrice> => {
    const response = await fetch(`${API_BASE_URL}/stocks/price/${symbol}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to get stock price");
    }
    return data;
  },

  getStockInfo: async (symbol: string): Promise<StockInfo> => {
    const response = await fetch(`${API_BASE_URL}/stocks/info/${symbol}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to get stock info");
    }
    return data;
  },
};

// ==========================================
// Chat API (Existing)
// ==========================================

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export const chatApi = {
  sendMessage: async (
    message: string,
    token: string
  ): Promise<{ content: string; timestamp: string }> => {
    const response = await fetch(`${API_BASE_URL}/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to send message");
    }
    return data;
  },
};