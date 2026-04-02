export interface User {
  id: string;
  username: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
}

export interface StockInfo {
  symbol: string;
  name: string;
}

export interface PriceData {
  id: number;
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface PredictionPoint {
  date: string;
  predicted_close: number;
  lower_bound: number;
  upper_bound: number;
  trend: string;
}

export interface PredictionResponse {
  symbol: string;
  version: string;
  trained_at: string;
  metrics: { mae?: number; rmse?: number; mape?: number };
  predictions: PredictionPoint[];
  history: { date: string; close: number | null }[];
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface Article { id: number; title: string; } // Placeholder
export interface ArticleListParams { page?: number; } // Placeholder
