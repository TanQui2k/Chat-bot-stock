'use client';

import React from 'react';

export default function InteractiveChart({ symbol }: { symbol: string }) {
  return (
    <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl shadow-lg relative overflow-hidden flex flex-col min-h-[400px]">
      {/* Asset Header Info */}
      <div className="border-b border-slate-800/60 bg-slate-900/50 p-4 shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
            <span className="text-indigo-400 font-bold text-sm tracking-widest">{symbol}</span>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-200">Mã Cổ phiếu {symbol}</h2>
            <p className="text-xs text-slate-500 font-medium">HOSE</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white tracking-tight">112.500 ₫</div>
          <div className="text-sm text-emerald-400 font-medium flex items-center justify-end gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clipRule="evenodd" />
            </svg>
            +1.500 (1,35%)
          </div>
        </div>
      </div>

      {/* Chart Area Placeholder */}
      <div className="p-6 flex-1 flex flex-col items-center justify-center text-slate-500 bg-gradient-to-b from-slate-900 to-slate-950/50">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" className="w-20 h-20 mb-4 opacity-30 text-emerald-400">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
          <h3 className="text-xl font-medium text-slate-300 mb-2">Biểu đồ thị trường tương tác</h3>
          <p className="text-sm text-center max-w-[320px] mb-4 text-slate-500">
            Khu vực biểu đồ. Cập nhật dữ liệu động sau này.
          </p>
      </div>
    </div>
  );
}
