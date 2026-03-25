"use client";

import React from "react";
import { AuthModal } from "./AuthModal";
import { useAuth } from "@/context/AuthContext";

export const Navbar: React.FC = () => {
  const { user, logout, showAuthModal, isAuthModalOpen, setIsAuthModalOpen, login } = useAuth();

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            {/* App Tile / Logo Mock */}
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500 font-bold text-slate-950 shadow-lg shadow-emerald-500/20">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M15.22 6.268a.75.75 0 0 1 .968-.431l5.942 2.28a.75.75 0 0 1 .431.97l-2.28 5.94a.75.75 0 1 1-1.4-.537l1.63-4.251-5.341 5.341a.75.75 0 0 1-1.06 0L9.89 11.36l-4.711 4.71a.75.75 0 0 1-1.06-1.06l5.241-5.241a.75.75 0 0 1 1.06 0l4.22 4.22 4.881-4.881-4.25 1.63a.75.75 0 0 1-.971-.432Z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              StockAI Predictor
            </div>
          </div>
          
          {/* User Avatar / Login Mock */}
          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-6 mr-4">
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Bảng điều khiển</a>
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Thị trường</a>
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Theo dõi</a>
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
