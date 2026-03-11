import React from "react";

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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        {/* Left Column: Market Chart (2/3 width on desktop) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl shadow-lg relative overflow-hidden flex flex-col min-h-[400px]">
            {/* Asset Header Info */}
            <div className="border-b border-slate-800/60 bg-slate-900/50 p-4 shrink-0 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <span className="text-indigo-400 font-bold text-sm tracking-widest">FPT</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-200">Công ty Cổ phần FPT</h2>
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
                  Đây là khu vực server component. Hãy đặt các thư viện Client Components chuyên về biểu đồ như TradingView, Recharts ở đây.
               </p>
               <div className="px-4 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/50 text-xs text-slate-400 font-mono">
                 {'<InteractiveChart symbol="FPT" />'}
               </div>
            </div>
          </div>
          
          {/* Sentiment & Quick Insights Widgets */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-between">
               <h3 className="text-sm font-semibold text-slate-400 mb-3 flex items-center gap-2">
                 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-emerald-500">
                   <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clipRule="evenodd" />
                 </svg>
                 AI Phân tích Cảm xúc
               </h3>
               <div>
                 <div className="flex items-end gap-3 mb-4">
                   <div className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Tăng giá</div>
                   <div className="text-sm text-emerald-500 font-medium mb-1">↑ 92% Tin cậy</div>
                 </div>
                 <div className="w-full bg-slate-900 rounded-full h-2">
                   <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-2 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" style={{width: '92%'}}></div>
                 </div>
               </div>
            </div>
            
            <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-between">
               <h3 className="text-sm font-semibold text-slate-400 mb-3">Xu hướng dự đoán (24h tới)</h3>
               <div>
                 <div className="flex items-end gap-3 mb-2">
                   <div className="text-3xl font-bold text-slate-100">+2,1%</div>
                   <div className="text-sm text-slate-400 font-medium mb-1">Mục tiêu: 115.000 ₫</div>
                 </div>
                 <p className="text-xs text-slate-500">Dựa trên mô hình đa lớp phân tích văn bản tin tức tài chính và dòng tiền trong 7 ngày qua.</p>
               </div>
            </div>
          </div>
        </div>

        {/* Right Column: AI Trading Assistant (1/3 width on desktop) */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800/90 border border-slate-700 rounded-2xl shadow-xl h-full flex flex-col min-h-[500px]">
             {/* Chat Header */}
             <div className="border-b border-slate-700/80 p-4 shrink-0 flex items-center justify-between bg-slate-800/40 rounded-t-2xl">
               <div className="flex items-center gap-3">
                 <span className="relative flex h-3 w-3">
                   <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                   <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                 </span>
                 <h2 className="text-base font-semibold text-slate-200">Trợ lý giao dịch AI</h2>
               </div>
               <button className="text-slate-400 hover:text-slate-200 bg-slate-700/30 hover:bg-slate-700 rounded-md p-1.5 transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                  </svg>
               </button>
             </div>
             
             {/* Chat History Messages */}
             <div className="flex-1 p-5 overflow-y-auto space-y-5 bg-gradient-to-b from-slate-800/20 to-slate-900/40">
               {/* Incoming AI message */}
               <div className="flex gap-3">
                 <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20 text-slate-900">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                      <path fillRule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5zM18 1.5a.75.75 0 01.728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 010 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 01-1.456 0l-.258-1.036a2.625 2.625 0 00-1.91-1.91l-1.036-.258a.75.75 0 010-1.456l1.036-.258a2.625 2.625 0 001.91-1.91l.258-1.036A.75.75 0 0118 1.5zM16.5 15a.75.75 0 01.712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 010 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 01-1.422 0l-.395-1.183a1.5 1.5 0 00-.948-.948l-1.183-.395a.75.75 0 010-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0116.5 15z" clipRule="evenodd" />
                    </svg>
                 </div>
                 <div className="bg-slate-700/50 rounded-2xl rounded-tl-sm p-3.5 text-sm text-slate-200 shadow-sm border border-slate-600/50 leading-relaxed">
                   Xin chào! Mình đang theo dõi nhóm ngành viễn thông công nghệ. Mã <span className="font-semibold text-emerald-400">FPT</span> đang kiểm tra vùng kháng cự quan trọng trong hôm nay. Mình có thể giúp gì cho danh mục của bạn?
                 </div>
               </div>
               
               {/* Outgoing user message */}
               <div className="flex gap-3 flex-row-reverse">
                 <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg text-xs font-bold text-white">
                    VA
                 </div>
                 <div className="bg-emerald-600/20 rounded-2xl rounded-tr-sm p-3.5 text-sm text-emerald-50 shadow-sm border border-emerald-500/30">
                   Mức hỗ trợ cứng nếu cổ phiếu điều chỉnh giảm là bao nhiêu vậy?
                 </div>
               </div>
               
               {/* Incoming AI loading indicator */}
               <div className="flex gap-3">
                 <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20 text-slate-900">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                      <path fillRule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5z" clipRule="evenodd" />
                    </svg>
                 </div>
                 <div className="bg-slate-700/50 rounded-2xl rounded-tl-sm p-4 text-sm flex items-center gap-1.5 shadow-sm border border-slate-600/50">
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></span>
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></span>
                 </div>
               </div>
             </div>

             {/* Input Area */}
             <div className="p-4 border-t border-slate-700/80 bg-slate-800/80 rounded-b-2xl">
               <div className="relative">
                 <input 
                   type="text" 
                   disabled
                   placeholder="Hỏi về một mã cổ phiếu hoặc xu hướng..." 
                   className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-4 pr-12 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none transition-all cursor-not-allowed shadow-inner"
                 />
                 <button disabled className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30 transition-colors cursor-not-allowed">
                   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 -rotate-45">
                     <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
                   </svg>
                 </button>
               </div>
               <p className="text-[10px] text-center text-slate-500 mt-3 font-medium uppercase tracking-wider">
                  Khu vực chèn component Client {"<ChatInterface />"} sau này
               </p>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
}
