'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

// Helper to generate a valid UUID v4
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export default function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const initSession = async () => {
    setIsInitializing(true);
    try {
      // Must be a valid UUID string to prevent FastAPI 422 error
      const userId = user?.id || generateUUID();
      
      const res = await fetch('http://localhost:8000/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userId, 
          title: `Assistant Chat`
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        console.error("Session Init Detail:", errorData);
        throw new Error("Backend rejected session creation");
      }
      
      const data = await res.json();
      if (data.id) {
        setSessionId(data.id);
        return data.id;
      }
    } catch (err) {
      console.error("Failed to init chat session", err);
    } finally {
      setIsInitializing(false);
    }
    return null;
  };

  useEffect(() => {
    initSession();
  }, [user?.id]);

  const suggestions = [
    { icon: '💰', text: 'Giá FPT hiện tại', action: 'Giá FPT hiện tại là bao nhiêu?' },
    { icon: '📈', text: 'Phân tích kỹ thuật VNM', action: 'Phân tích kỹ thuật cổ phiếu VNM' },
    { icon: '📊', text: 'Dự báo xu hướng MSN', action: 'Dự đoán giá MSN trong 24h tới' },
    { icon: '❓', text: 'Câu hỏi thường gặp', action: 'Bạn có thể hỗ trợ tôi những gì?' },
  ];

  const handleSend = async (forcedInput?: string) => {
    const textToSend = forcedInput || input.trim();
    if (!textToSend || isLoading) return;

    let currentSessionId = sessionId;
    
    // If session fails to init or is not ready, try to init one now
    if (!currentSessionId) {
      currentSessionId = await initSession();
    }

    if (!currentSessionId) {
      alert("Kết nối AI đang bận (Lỗi 422/UUID). Vui lòng tải lại trang!");
      return;
    }
    
    if (!forcedInput) setInput('');
    
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(`http://localhost:8000/api/chat/sessions/${currentSessionId}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: textToSend }),
      });
      
      if (!res.ok) throw new Error("Gửi tin nhắn thất bại.");
      
      const turnResponse = await res.json();
      setMessages(prev => [...prev, { 
        id: turnResponse.assistant_message.id.toString(), 
        role: 'assistant', 
        content: turnResponse.assistant_message.content 
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { id: 'err', role: 'assistant', content: "Có lỗi xảy ra khi kết nối với AI." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`flex flex-col h-full bg-background text-foreground overflow-hidden relative ${
      messages.length === 0 ? 'justify-center items-center px-4' : ''
    }`}>
      
      {messages.length > 0 && (
        <div className="flex-1 w-full overflow-y-auto px-4 md:px-10 space-y-6 pb-4 pt-10 scrollbar-hide">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2`}>
                <div className={`max-w-[90%] rounded-[1.5rem] px-6 py-4 shadow-xl ${
                  msg.role === 'user' 
                    ? 'bg-primary text-primary-foreground border border-primary/20 rounded-tr-md' 
                    : 'bg-transparent text-foreground rounded-tl-md'
                }`}>
                  {msg.role === 'assistant' && (
                    <div className="text-emerald-500 mb-2 font-bold text-[10px] uppercase tracking-widest flex items-center gap-1.5">
                      <span className="w-1 h-3 bg-emerald-500 rounded-full"></span> Assistant
                    </div>
                  )}
                  <p className="text-base leading-relaxed tracking-tight whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex flex-col items-start px-2">
                 <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-emerald-500/50 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-emerald-500/50 rounded-full animate-bounce delay-150"></span>
                    <span className="w-1.5 h-1.5 bg-emerald-500/50 rounded-full animate-bounce delay-300"></span>
                 </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      <div className={`w-full transition-all duration-500 px-4 md:px-0 ${
        messages.length > 0 ? 'pb-6 pt-4 border-t border-border bg-card/30 shrink-0' : 'flex flex-col items-center flex-none'
      }`}>
        <div className="max-w-3xl mx-auto flex flex-col items-center w-full">
          
          {!messages.length && (
            <div className="flex flex-col items-center mb-10 animate-in fade-in zoom-in duration-1000">
               <div className="flex items-center gap-4 mb-2">
                  <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 shadow-lg">
                    <svg viewBox="0 0 24 24" className="w-10 h-10 text-emerald-500" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                       <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                       <polyline points="16 7 22 7 22 13" />
                    </svg>
                  </div>
                  <h1 className="text-6xl font-bold tracking-tighter text-foreground">StockAI</h1>
               </div>
               <p className="text-muted-foreground text-xl font-medium">Trao đổi cùng Trợ lý Chứng khoán AI</p>
            </div>
          )}

          <div className="w-full relative group max-w-2xl px-2">
            <div className="absolute inset-0 bg-emerald-500/5 rounded-[2rem] blur-2xl group-focus-within:bg-emerald-500/10 transition-all duration-500"></div>
            <div className="relative bg-card/80 border border-border rounded-[2rem] flex items-end p-2.5 px-4 transition-all group-focus-within:border-emerald-500/40 group-focus-within:bg-card shadow-2xl backdrop-blur-3xl">
              <textarea
                ref={inputRef}
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Nhập câu hỏi bất kỳ..."
                className="flex-1 bg-transparent border-none focus:ring-0 outline-none text-foreground font-medium placeholder:text-muted-foreground/80 px-4 py-3.5 resize-none max-h-[150px] overflow-y-auto leading-relaxed text-base text-center"
              />
              <div className="flex items-center gap-2 pr-1 pb-2">
                <button className="p-2.5 text-muted-foreground hover:text-foreground transition-colors cursor-pointer" title="Voice Input">
                  <svg viewBox="0 0 24 24" className="w-5.5 h-5.5" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                </button>
                <button 
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className={`p-2.5 rounded-full transition-all shadow-lg cursor-pointer ${
                    input.trim() ? 'bg-emerald-500 text-white hover:bg-emerald-400 hover:scale-105 active:scale-95' : 'bg-muted text-muted-foreground opacity-50'
                  }`}
                >
                  <svg viewBox="0 0 24 24" className="w-5.5 h-5.5" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                </button>
              </div>
            </div>
          </div>

          {!messages.length && (
            <div className="w-full mt-12 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
               <div className="flex items-center justify-center gap-6 mb-8">
                 <div className="h-px bg-border flex-1 max-w-[100px]"></div>
                 <span className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground font-bold whitespace-nowrap">Câu hỏi thường gặp</span>
                 <div className="h-px bg-border flex-1 max-w-[100px]"></div>
               </div>
               <div className="grid grid-cols-1 gap-3.5 max-w-xl mx-auto px-4">
                 {suggestions.map((item, idx) => (
                   <button
                     key={idx}
                     onClick={() => handleSend(item.action)}
                     className="flex items-center justify-center gap-4 p-4 rounded-[1.8rem] bg-card/60 border border-border hover:border-emerald-500/30 hover:bg-muted transition-all text-center group shadow-md cursor-pointer"
                   >
                     <span className="text-2xl transition-opacity transform group-hover:scale-110 duration-300 pointer-events-none">{item.icon}</span>
                     <span className="text-muted-foreground group-hover:text-foreground text-sm font-semibold tracking-wide pointer-events-none">{item.text}</span>
                   </button>
                 ))}
               </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
