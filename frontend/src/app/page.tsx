"use client";

import React, { useState, useEffect } from "react";
import InteractiveChart from "../components/InteractiveChart";
import ChatInterface from "../components/ChatInterface";
import PredictionWidget from "../components/PredictionWidget";
import { AuthModal } from "../components/AuthModal";
import { useAuth } from "../context/AuthContext";

const popularTickers = ['FPT', 'VNM', 'MSN', 'VPB', 'ACB', 'HPG', 'VIC', 'VCB'];

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('FPT');
  const [timeframe, setTimeframe] = useState('1M');
  const [showTickerMenu, setShowTickerMenu] = useState(false);
  
  const { user, isLoading, showAuthModal } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)] bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col">
      {/* Dashboard Content */}
      <DashboardContent 
        selectedTicker={selectedTicker} 
        setSelectedTicker={setSelectedTicker}
        timeframe={timeframe} 
        setTimeframe={setTimeframe}
        showTickerMenu={showTickerMenu}
        setShowTickerMenu={setShowTickerMenu}
      />
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
  const [isMobileChatOpen, setIsMobileChatOpen] = useState(false);

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
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1 min-h-0 relative">
        
        {/* Left Column: Market Chart (8/12 width on desktop) */}
        <div className="md:col-span-8 flex flex-col gap-6 min-h-0 w-full">
          <InteractiveChart symbol={selectedTicker} />
          
          {/* Sentiment & Quick Insights Widgets */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 shrink-0 pb-20 md:pb-0">
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

        {/* Right Column: AI Trading Assistant (4/12 width on desktop, hidden on mobile) */}
        <div className={`md:col-span-4 md:h-[calc(100vh-12rem)] sticky top-24 z-40 transition-transform duration-300 md:block ${isMobileChatOpen ? 'fixed inset-0 top-0 pt-20 p-4 bg-slate-950/90 backdrop-blur-sm shadow-2xl block animate-in slide-in-from-bottom' : 'hidden'}`}>
          {isMobileChatOpen && (
            <button 
              onClick={() => setIsMobileChatOpen(false)}
              className="md:hidden absolute top-6 right-6 p-2 bg-slate-800 text-slate-300 rounded-full border border-slate-700 z-50 hover:bg-slate-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
          <ChatInterface />
        </div>

        {/* Mobile FAB to open Chat */}
        {!isMobileChatOpen && (
          <button 
            onClick={() => setIsMobileChatOpen(true)}
            className="md:hidden fixed bottom-6 right-6 w-14 h-14 bg-violet-600 shadow-[0_0_20px_rgba(124,58,237,0.5)] rounded-full flex items-center justify-center text-white z-50 hover:bg-violet-500 hover:scale-105 transition-all"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 animate-pulse">
              <path fillRule="evenodd" d="M4.804 21.644A6.707 6.707 0 006 21.75a6.721 6.721 0 003.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 01-.814 1.686.75.75 0 00.44 1.223zM8.25 10.875a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25zM10.875 12a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0zm4.875-1.125a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25z" clipRule="evenodd" />
            </svg>
          </button>
        )}

      </div>
    </div>
  );
}