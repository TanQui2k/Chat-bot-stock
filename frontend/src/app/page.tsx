import React from "react";
import InteractiveChart from "../components/InteractiveChart";
import ChatInterface from "../components/ChatInterface";
import PredictionWidget from "../components/PredictionWidget";

export default function Dashboard() {
  return (
    <div className="w-full h-full flex flex-col">
      {/* Dashboard Header */}
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Tổng quan thị trường</h1>
          <p className="text-sm text-slate-400 mt-1">Phân tích và dự đoán bằng AI theo thời gian thực</p>
        </div>
        {/* Quick controls mock */}
        <div className="flex bg-slate-800/80 rounded-lg p-1 border border-slate-700/60 shadow-sm">
          <button className="px-4 py-1.5 text-sm font-medium rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm transition-colors">1 Ngày</button>
          <button className="px-4 py-1.5 text-sm font-medium rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors">1 Tuần</button>
          <button className="px-4 py-1.5 text-sm font-medium rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors">1 Tháng</button>
          <button className="px-4 py-1.5 text-sm font-medium rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors">1 Năm</button>
        </div>
      </div>

      {/* Main Grid Layout Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        
        {/* Left Column: Market Chart (2/3 width on desktop) */}
        <div className="lg:col-span-2 flex flex-col gap-6 min-h-0">
          <InteractiveChart symbol="FPT" />
          
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
            
            <PredictionWidget symbol="FPT" />
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
