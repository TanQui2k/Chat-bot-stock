'use client';

import React, { useState, useRef, useEffect } from 'react';

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
      content: 'Xin chào! Mình là Trợ lý AI Chứng khoán. Mình có thể hỗ trợ thông tin giá và phân tích chuyên sâu cho bạn. VD: "Giá FPT bao nhiêu?"'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
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
      const userId = (typeof crypto !== 'undefined' && crypto.randomUUID) 
          ? crypto.randomUUID() 
          : '123e4567-e89b-12d3-a456-426614174000'.replace(/[xy]/g, function(c) {
              var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
              return v.toString(16);
            });
      
      const res = await fetch('http://localhost:8000/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, title: 'Phiên Chat Giao Diện' })
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
  }, []);

  const handleReset = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Xin chào! Mình là Trợ lý AI Chứng khoán. Mình có thể hỗ trợ thông tin giá và phân tích chuyên sâu cho bạn. VD: "Giá FPT bao nhiêu?"'
      }
    ]);
    initSession();
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
      // Gọi Endpoint thật trên Backend: POST /sessions/{id}/turn
      const res = await fetch(`http://localhost:8000/api/chat/sessions/${sessionId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userMsg }),
      });
      
      if (!res.ok) throw new Error("Backend API gặp lỗi hoặc chưa phản hồi.");
      
      // Parse payload trả về (ChatTurnResponse chứa assistant_message)
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
    <div className="bg-slate-800/90 border border-slate-700 rounded-2xl shadow-xl h-full flex flex-col min-h-[500px]">
      {/* Chat Header */}
      <div className="border-b border-slate-700/80 p-4 shrink-0 flex items-center justify-between bg-slate-800/40 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <h2 className="text-base font-semibold text-slate-200">Trợ lý Tương tác AI</h2>
        </div>
        
        <button 
          onClick={handleReset}
          className="px-2.5 py-1.5 rounded-lg border border-slate-700/80 bg-slate-800/50 hover:bg-slate-700/50 hover:border-slate-600 text-slate-400 hover:text-emerald-400 transition-all flex items-center gap-1.5 text-xs font-semibold shadow-sm focus:outline-none"
          title="Làm mới cuộc trò chuyện"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
            <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H4.25a.75.75 0 00-.75.75v3.982a.75.75 0 001.5 0v-2.18l.423.423a7 7 0 0011.666-3.86.75.75 0 00-1.777-.282zm-10.624-2.848a5.5 5.5 0 019.201-2.466l.312.311H11.77a.75.75 0 000 1.5h3.982a.75.75 0 00.75-.75V3.439a.75.75 0 00-1.5 0v2.18l-.423-.423a7 7 0 00-11.666 3.86.75.75 0 001.777.282z" clipRule="evenodd" />
          </svg>
          Làm mới
        </button>
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
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg text-xs font-bold text-white uppercase">
                VA
              </div>
            )}
            <div className={`rounded-2xl p-3.5 text-sm shadow-sm border leading-relaxed whitespace-pre-wrap ${
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
            ref={inputRef}
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isInitializing ? "Đang kết nối Backend..." : "Nhắn tin cho AI..."} 
            disabled={isInitializing || isLoading}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-4 pr-16 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all shadow-inner disabled:opacity-50"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim() || isInitializing}
            className="absolute right-2 p-1.5 rounded-lg bg-emerald-500 text-slate-900 hover:bg-emerald-400 font-medium text-xs transition-colors disabled:opacity-50 disabled:bg-slate-700 disabled:text-slate-500"
          >
            Gửi
          </button>
        </div>
      </div>
    </div>
  );
}
