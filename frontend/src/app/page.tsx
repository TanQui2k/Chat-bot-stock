"use client";

import React, { useState, useEffect } from "react";
import InteractiveChart from "../components/InteractiveChart";
import ChatInterface from "../components/ChatInterface";
import PredictionWidget from "../components/PredictionWidget";
import { AuthModal } from "../components/AuthModal";
import { authApi, AuthUser } from "../lib/api";

const popularTickers = ['FPT', 'VNM', 'MSN', 'VPB', 'ACB', 'HPG', 'VIC', 'VCB'];

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('FPT');
  const [timeframe, setTimeframe] = useState('1M');
  const [showTickerMenu, setShowTickerMenu] = useState(false);
  
  // Authentication state
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const user = await authApi.getProfile(token);
          setCurrentUser(user);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('access_token');
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = (user: AuthUser) => {
    setCurrentUser(user);
    setIsAuthModalOpen(false);
    // Store token in localStorage
    // Note: In a real app, store in httpOnly cookie for better security
    localStorage.setItem('access_token', 'mock_token_for_demo');
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await authApi.logout(token);
      }
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setCurrentUser(null);
      localStorage.removeItem('access_token');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleLoginSuccess}
      />

      {/* Navbar */}
      <nav className="bg-slate-800/50 backdrop-blur-md border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">AI</span>
              </div>
              <span className="text-xl font-bold text-slate-100">StockAI</span>
            </div>

            <div className="flex items-center gap-4">
              {currentUser ? (
                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-end">
                    <span className="text-sm font-medium text-slate-200">
                      {currentUser.full_name || currentUser.username || currentUser.email || 'Người dùng'}
                    </span>
                    <span className="text-xs text-slate-400">
                      {currentUser.phone_verified ? 'SĐT đã xác thực' : 'Chưa xác thực'}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-red-400 hover:text-red-300 transition-colors"
                  >
                    Đăng xuất
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="px-4 py-2 text-sm font-medium text-violet-400 hover:text-violet-300 transition-colors bg-violet-500/10 hover:bg-violet-500/20 rounded-lg"
                >
                  Đăng nhập Google
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardContent 
          selectedTicker={selectedTicker} 
          setSelectedTicker={setSelectedTicker}
          timeframe={timeframe} 
          setTimeframe={setTimeframe}
          showTickerMenu={showTickerMenu}
          setShowTickerMenu={setShowTickerMenu}
        />
      </div>
    </div>
  );
}

// Separate component for dashboard content to avoid re-renders
function DashboardContent({
  selectedTicker,
  setSelectedTicker,
  timeframe,
  setTimeframe,
  showTickerMenu,
  setShowTickerMenu
}: {
  selectedTicker: string;
  setSelectedTicker: (ticker: string) => void;
  timeframe: string;
  setTimeframe: (tf: string) => void;
  showTickerMenu: boolean;
  setShowTickerMenu: (show: boolean) => void;
}) {
  return (
    <div className="w-full h-full flex flex-col">
      {/* Dashboard Header */}
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Tổng quan thị trường</h1>
          <p className="text-sm text-slate-400 mt-1">Phân tích và dự đoán bằng AI theo thời gian thực</p>
        </div>
        
        {/* Improved Filter Controls */}
        <div className="flex items-center gap-2">
          {/* Stock Symbol Selector */}
          <div className="relative">
            <button
              onClick={() => setShowTickerMenu(!showTickerMenu)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 hover:border-emerald-500/50 transition-all"
            >
              <span className="font-semibold text-emerald-400">{selectedTicker}</span>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 text-slate-400">
                <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
              </svg>
            </button>
            
            {showTickerMenu && (
              <div className="absolute top-full left-0 mt-1 w-40 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                {popularTickers.map((ticker) => (
                  <button
                    key={ticker}
                    onClick={() => {
                      setSelectedTicker(ticker);
                      setShowTickerMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-slate-300 hover:bg-emerald-500/20 hover:text-emerald-400 transition-colors flex justify-between items-center group"
                  >
                    <span>{ticker}</span>
                    <span className="text-xs text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">Xem</span>
                  </button>
                ))}
                <div className="border-t border-slate-800 pt-1">
                  <input
                    type="text"
                    placeholder="Tìm mã..."
                    className="w-full px-3 py-2 text-sm bg-slate-800 border-b border-slate-700 focus:outline-none text-slate-200"
                  />
                </div>
              </div>
            )}
          </div>
          
          {/* Timeframe Selector */}
          <div className="flex bg-slate-800/80 rounded-lg p-0.5 border border-slate-700/60 shadow-sm">
            {['1D', '1W', '1M', '3M', '6M', '1Y'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  timeframe === tf 
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Grid Layout Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        
        {/* Left Column: Market Chart (2/3 width on desktop) */}
        <div className="lg:col-span-2 flex flex-col gap-6 min-h-0">
          <InteractiveChart symbol={selectedTicker} />
          
          {/* Sentiment & Quick Insights Widgets */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 shrink-0">
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-between h-[150px]">
               <h3 className="text-sm font-semibold text-slate-400 mb-3 flex items-center gap-2">
                 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-emerald-500">
                   <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clipRule="evenodd" />
                 </svg>
                 AI Phân tích Cảm xúc
               </h3>
               <div>
                 <div className="flex items-end gap-3 mb-4">
                   <div className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Tích cực</div>
                   <div className="text-sm text-emerald-500 font-medium mb-1">↑ 92% Tin cậy</div>
                 </div>
                 <div className="w-full bg-slate-900 rounded-full h-2">
                   <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-2 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" style={{width: '92%'}}></div>
                 </div>
               </div>
            </div>
            
            <PredictionWidget symbol={selectedTicker} />
          </div>
        </div>

        {/* Right Column: AI Trading Assistant (1/3 width on desktop) */}
        <div className="lg:col-span-1 lg:h-[calc(100vh-12rem)] sticky top-24">
          <ChatInterface />
        </div>

      </div>
    </div>
  );
}