'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { chatService, Message } from '@/services/chatService';
import ChatMessageItem from './chat/ChatMessageItem';
import ChatWelcome from './chat/ChatWelcome';
import ChatInput from './chat/ChatInput';

export default function ChatInterface() {
  const { user, showAuthModal } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initSession = useCallback(async () => {
    if (!user?.id) return null;

    try {
      const id = await chatService.initSession(user.id);
      setSessionId(id);
      return id;
    } catch (err) {
      console.error('Failed to init chat session', err);
      return null;
    }
  }, [user?.id]);

  useEffect(() => {
    setMessages([]);
    setSessionId(null);

    if (user?.id) {
      void initSession();
    }
  }, [initSession, user?.id]);

  const handleSend = async (forcedInput?: string) => {
    const textToSend = forcedInput || input.trim();
    if (!textToSend || isLoading) return;

    if (!user?.id) {
      showAuthModal();
      return;
    }

    let currentSessionId = sessionId;

    if (!currentSessionId) {
      currentSessionId = await initSession();
    }

    if (!currentSessionId) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: 'Không thể tạo phiên chat. Vui lòng thử lại sau.',
        },
      ]);
      return;
    }

    if (!forcedInput) setInput('');

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const assistantMsg = await chatService.sendMessage(currentSessionId, textToSend);
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Có lỗi xảy ra khi kết nối với AI.';
      setMessages(prev => [
        ...prev,
        { id: `err-${Date.now()}`, role: 'assistant', content: message },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    if (!user?.id) {
      showAuthModal();
      return;
    }

    setMessages([]);
    setSessionId(null);
    setInput('');
    void initSession();
  };

  return (
    <div className={`flex flex-col h-full bg-background text-foreground overflow-hidden relative ${
      messages.length === 0 ? 'justify-center items-center px-4' : ''
    }`}>
      {messages.length > 0 && (
        <div className="absolute top-4 left-4 z-50">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card/80 border border-border text-muted-foreground hover:text-foreground hover:border-border/80 transition-all text-xs font-semibold shadow-sm backdrop-blur-md group"
            title="Tạo đoạn chat mới"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 transition-transform group-hover:rotate-180 duration-500">
              <path fillRule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.982a.75.75 0 00-.75.75v4.25a.75.75 0 001.5 0v-2.42l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.44-.437zm0-2.848a.75.75 0 001.44-.437 7 7 0 00-11.712-3.138l-.31.31v2.42a.75.75 0 001.5 0V3.482a.75.75 0 00-.75-.75H3.982a.75.75 0 000 1.5h2.433l.312.311a5.5 5.5 0 019.201-2.466l.312.311h-2.433a.75.75 0 000 1.5h4.25a.75.75 0 00.75-.75V3.482a.75.75 0 00-1.5 0v2.42l-.31-.31a7 7 0 00-11.712 3.138.75.75 0 001.44.437z" clipRule="evenodd" />
            </svg>
            Chat mới
          </button>
        </div>
      )}

      {messages.length > 0 && (
        <div className="flex-1 w-full overflow-y-auto px-4 md:px-10 space-y-6 pb-4 pt-10 scrollbar-hide">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg) => (
              <ChatMessageItem key={msg.id} message={msg} />
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
        messages.length > 0 ? 'pb-4 pt-4 border-t border-border bg-card/30 shrink-0' : 'flex flex-col items-center flex-none mt-16'
      }`}>
        <div className="max-w-3xl mx-auto flex flex-col items-center w-full">
          {!messages.length && (
            <ChatWelcome onSuggestionClick={(action) => handleSend(action)} />
          )}

          <ChatInput
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            onSend={() => handleSend()}
          />
        </div>
      </div>
    </div>
  );
}
