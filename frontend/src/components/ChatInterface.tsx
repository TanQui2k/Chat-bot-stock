'use client';

import React, { useState, useRef, useEffect } from 'react';
import { predictStock } from '../lib/api';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Mình đang theo dõi nhóm ngành viễn thông công nghệ. Mình có thể giúp gì cho danh mục của bạn?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      // Logic mock: Trích xuất mã chứng khoán nếu có, nếu không thì mặc định là FPT
      const match = userMsg.match(/[a-zA-Z]{3}/);
      const ticker = match ? match[0].toUpperCase() : "FPT";

      const res = await predictStock(ticker);
      
      const assistantMsg = `Dự đoán cho ${res.ticker}: ${res.prediction} với độ tin cậy ${(res.probability * 100).toFixed(0)}%.`;
      
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: assistantMsg }]);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      setMessages(prev => [
        ...prev,
        { id: Date.now().toString(), role: 'assistant', content: `Lỗi: ${message}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
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
      </div>
      
      {/* Chat History Messages */}
      <div className="flex-1 p-5 overflow-y-auto space-y-5 bg-gradient-to-b from-slate-800/20 to-slate-900/40">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {msg.role === 'assistant' ? (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20 text-slate-900 font-bold text-xs">
                AI
              </div>
            ) : (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg text-xs font-bold text-white">
                VA
              </div>
            )}
            <div className={`rounded-2xl p-3.5 text-sm shadow-sm border leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-emerald-600/20 rounded-tr-sm text-emerald-50 border-emerald-500/30' 
                : 'bg-slate-700/50 rounded-tl-sm text-slate-200 border-slate-600/50'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20 text-slate-900 font-bold text-xs">
              AI
            </div>
            <div className="bg-slate-700/50 rounded-2xl rounded-tl-sm p-4 text-sm flex items-center gap-1.5 shadow-sm border border-slate-600/50">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"></span>
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></span>
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-700/80 bg-slate-800/80 rounded-b-2xl">
        <div className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Hỏi mã cổ phiếu (VD: VCB, FPT)..." 
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-4 pr-16 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all shadow-inner"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="absolute right-2 p-1.5 rounded-lg bg-emerald-500 text-slate-900 hover:bg-emerald-400 font-medium text-xs transition-colors disabled:opacity-50 disabled:bg-slate-700 disabled:text-slate-500"
          >
            Gửi
          </button>
        </div>
      </div>
    </div>
  );
}
