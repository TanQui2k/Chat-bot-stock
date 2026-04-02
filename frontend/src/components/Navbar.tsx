"use client";

import React from "react";
import { AuthModal } from "./AuthModal";
import { useAuth } from "@/context/AuthContext";

export const Navbar: React.FC = () => {
  const { user, logout, showAuthModal, isAuthModalOpen, setIsAuthModalOpen, login } = useAuth();

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
        <div className="flex h-16 w-full items-center justify-between px-4 sm:px-6 lg:px-10">
          <div className="flex items-center gap-3">
            {/* App Tile / Logo Mock */}
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500 font-bold text-slate-950 shadow-lg shadow-emerald-500/20">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M15.22 6.268a.75.75 0 0 1 .968-.431l5.942 2.28a.75.75 0 0 1 .431.97l-2.28 5.94a.75.75 0 1 1-1.4-.537l1.63-4.251-5.341 5.341a.75.75 0 0 1-1.06 0L9.89 11.36l-4.711 4.71a.75.75 0 0 1-1.06-1.06l5.241-5.241a.75.75 0 0 1 1.06 0l4.22 4.22 4.881-4.881-4.25 1.63a.75.75 0 0 1-.971-.432Z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent shrink-0">
              StockAI Predictor
            </div>
          </div>

          {/* Central Page Title - Moved from Dashboard */}
          <div className="hidden lg:flex flex-col items-center justify-center animate-in fade-in slide-in-from-top-2 duration-700">
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></span>
              Tổng quan thị trường
            </h1>
            <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase opacity-80">
              PHÂN TÍCH VÀ DỰ ĐOÁN AI THỜI GIAN THỰC
            </p>
          </div>
          
          {/* User Avatar / Login Mock */}
          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-8 mr-6">
              <a href="#" className="text-sm font-semibold text-emerald-400 border-b-2 border-emerald-500 pb-1 flex items-center gap-1.5 transition-all">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                  <path d="M10 3a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM10 8.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM11.5 15.5a1.5 1.5 0 10-3 0 1.5 1.5 0 003 0z" />
                </svg>
                Bảng điều khiển
              </a>
              <a href="#" className="text-sm font-medium text-slate-400 hover:text-emerald-400 transition-all flex items-center gap-1.5 group">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-colors">
                  <path fillRule="evenodd" d="M10 2c-2.236 0-4.43.18-6.57.532a.75.75 0 00-.627.74v11.854a.75.75 0 00.977.716L10 14.206l6.22 1.636a.75.75 0 00.977-.716V3.272a.75.75 0 00-.627-.74C14.43 2.18 12.236 2 10 2z" clipRule="evenodd" />
                </svg>
                Lịch sử Chat
              </a>
            </nav>

            {user ? (
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-semibold text-slate-200">{user.full_name || user.username}</p>
                  <button 
                    onClick={logout}
                    className="text-[10px] text-slate-400 hover:text-red-400 transition-colors"
                  >
                    Đăng xuất
                  </button>
                </div>
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm text-white font-bold shadow-sm border border-slate-700">
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt="Avatar" className="h-full w-full rounded-full object-cover" />
                  ) : (
                    (user.full_name || user.username || "U").substring(0, 2).toUpperCase()
                  )}
                </div>
              </div>
            ) : (
              <button 
                onClick={showAuthModal}
                className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 pl-3 pr-1 py-1 text-sm font-medium transition-all hover:bg-slate-800 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 group"
              >
                <span className="text-slate-200 group-hover:text-emerald-400 transition-colors">Đăng nhập</span>
                <div className="h-7 w-7 rounded-full bg-slate-700 flex items-center justify-center text-xs text-slate-400 font-bold shadow-sm group-hover:bg-emerald-500 group-hover:text-slate-950 transition-all">
                  VA
                </div>
              </button>
            )}
          </div>
        </div>
      </header>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
        onSuccess={login}
      />
    </>
  );
};
