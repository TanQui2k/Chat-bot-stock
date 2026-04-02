'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

export default function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Mình là Trợ lý AI Chứng khoán (StockAI Assistant). Mình có thể hỗ trợ bạn:\n\n• Xem giá cổ phiếu hiện tại\n• Phân tích kỹ thuật và xu hướng\n• Dự đoán giá trong 24h tới\n• Giải đáp câu hỏi về thị trường\n\nVí dụ: "Giá FPT bao nhiêu?" hoặc "Phân tích VNM"'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Tự động Focus lại ô input sau khi AI trả lời xong
  useEffect(() => {
    if (!isLoading && !isInitializing) {
      inputRef.current?.focus();
    }
  }, [isLoading, isInitializing]);

  // Khởi tạo Chat Session thật qua /api/chat/sessions
  const initSession = async () => {
    setIsInitializing(true);
    try {
      const userId = user?.id || (typeof crypto !== 'undefined' && crypto.randomUUID 
          ? crypto.randomUUID() 
          : '123e4567-e89b-12d3-a456-426614174000');
      
      const res = await fetch('http://localhost:8000/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userId, 
          title: `Phiên Chat ${new Date().toLocaleDateString()}` 
        })
      });
      const data = await res.json();
      if (data.id) setSessionId(data.id);
    } catch (err) {
      console.error("Không thể khởi tạo session Backend:", err);
    } finally {
      setIsInitializing(false);
    }
  };

  useEffect(() => {
    initSession();
  }, [user?.id]); // Re-init when user changes (e.g. login)

  const quickActions = [
    { icon: '💰', text: 'Giá FPT hiện tại', action: 'Giá FPT hiện tại là bao nhiêu?' },
    { icon: '📈', text: 'Phân tích VNM', action: 'Phân tích kỹ thuật cổ phiếu VNM' },
    { icon: '📊', text: 'Dự đoán MSN', action: 'Dự đoán giá MSN trong 24h tới' },
    { icon: '❓', text: 'Câu hỏi thường gặp', action: 'Bạn có thể giúp tôi những gì?' },
  ];

  const handleReset = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Xin chào! Mình là Trợ lý AI Chứng khoán (StockAI Assistant). Mình có thể hỗ trợ bạn:\n\n• Xem giá cổ phiếu hiện tại\n• Phân tích kỹ thuật và xu hướng\n• Dự đoán giá trong 24h tới\n• Giải đáp câu hỏi về thị trường\n\nVí dụ: "Giá FPT bao nhiêu?" hoặc "Phân tích VNM"'
      }
    ]);
    initSession();
    setShowQuickActions(false);
  };

  const handleQuickAction = (actionText: string) => {
    setInput(actionText);
    setShowQuickActions(false);
    // Auto-send after a short delay
    setTimeout(() => {
      handleSend();
    }, 100);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    if (!sessionId) {
      alert("Kết nối Chatbot chưa sẵn sàng hoặc Backend chưa khởi tạo thành công. Vui lòng F5 tải lại trang!");
      return;
    }
    
    // Gửi tin nhắn user lên UI nội bộ trước
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/api/chat/sessions/${sessionId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userMsg }),
      });
      
      if (!res.ok) throw new Error("Backend API gặp lỗi hoặc chưa phản hồi.");
      
      const turnResponse = await res.json();
      const assistantText = turnResponse.assistant_message.content;
      
      setMessages(prev => [
        ...prev, 
        { 
          id: turnResponse.assistant_message.id.toString(), 
          role: 'assistant', 
          content: assistantText 
        }
      ]);
    } catch (error: any) {
      setMessages(prev => [
        ...prev,
        { id: Date.now().toString(), role: 'assistant', content: `Lỗi kết nối LLM: ${error.message}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="bg-slate-800/90 border border-slate-700 rounded-2xl shadow-xl h-full flex flex-col ring-1 ring-white/5 overflow-hidden">
      {/* Chat Header */}
      <div className="border-b border-slate-700/80 p-4 shrink-0 flex flex-col gap-3 bg-slate-800/40 rounded-t-2xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <h2 className="text-lg font-bold text-slate-100 italic tracking-wide">Trợ lý Tương tác AI</h2>
          </div>
          
          <div className="flex items-center gap-1">
            <button 
              onClick={() => setShowQuickActions(!showQuickActions)}
              className="p-1.5 rounded-lg border border-slate-700/80 bg-slate-800/50 hover:bg-slate-700/50 hover:border-slate-600 text-slate-400 hover:text-emerald-400 transition-all"
              title="Hành động nhanh"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 16a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
              </svg>
            </button>
            <button 
              onClick={handleReset}
              className="px-2.5 py-1.5 rounded-lg border border-slate-700/80 bg-slate-800/50 hover:bg-slate-700/50 hover:border-slate-600 text-slate-400 hover:text-emerald-400 transition-all flex items-center gap-1.5 text-xs font-semibold shadow-sm"
              title="Làm mới cuộc trò chuyện"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H4.25a.75.75 0 00-.75.75v3.982a.75.75 0 001.5 0v-2.18l.423.423a7 7 0 0011.666-3.86.75.75 0 00-1.777-.282zm-10.624-2.848a5.5 5.5 0 019.201-2.466l.312.311H11.77a.75.75 0 000 1.5h3.982a.75.75 0 00.75-.75V3.439a.75.75 0 00-1.5 0v2.18l-.423-.423a7 7 0 00-11.666 3.86.75.75 0 001.777.282z" clipRule="evenodd" />
              </svg>
              Làm mới
            </button>
          </div>
        </div>
        
        {/* Quick Actions Bar */}
        {(showQuickActions || messages.length <= 1) && (
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-700/50 animate-in fade-in slide-in-from-top-2">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleQuickAction(action.action)}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-700/50 hover:bg-emerald-500/20 hover:text-emerald-400 border border-slate-600/50 hover:border-emerald-500/30 transition-all text-sm font-medium"
              >
                <span className="text-base">{action.icon}</span>
                <span>{action.text}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Chat History Messages */}
      <div className="flex-1 p-5 overflow-y-auto space-y-5 bg-gradient-to-b from-slate-800/20 to-slate-900/40">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {msg.role === 'assistant' ? (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20 text-slate-900 font-bold text-xs uppercase">
                AI
              </div>
            ) : (
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg border border-slate-700 overflow-hidden shadow-indigo-500/20">
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="User Avatar" className="h-full w-full object-cover" />
                ) : (
                  <span className="text-white font-bold text-xs">{(user?.full_name || user?.username || "U").substring(0, 2).toUpperCase()}</span>
                )}
              </div>
            )}
            <div className={`rounded-2xl p-4 text-base shadow-md border leading-relaxed tracking-tight whitespace-pre-wrap ${
              msg.role === 'user' 
                ? 'bg-emerald-600/20 rounded-tr-sm text-emerald-50 border-emerald-500/30 font-medium' 
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
            ref={inputRef}
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isInitializing ? "Đang kết nối Backend..." : "Nhắn tin cho AI..."} 
            disabled={isInitializing || isLoading}
            className="w-full bg-slate-900 border border-slate-700 rounded-2xl pl-5 pr-20 py-4 text-base text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all shadow-inner disabled:opacity-50"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim() || isInitializing}
            className="absolute right-3 px-4 py-2 rounded-xl bg-violet-600 text-white hover:bg-violet-500 font-bold text-sm transition-all shadow-lg active:scale-95 disabled:opacity-50 disabled:bg-slate-700 disabled:text-slate-500"
          >
            Gửi
          </button>
        </div>
      </div>
    </div>
  );
}
