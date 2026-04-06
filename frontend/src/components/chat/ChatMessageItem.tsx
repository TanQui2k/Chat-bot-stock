import React from 'react';
import { Message } from '@/services/chatService';

interface ChatMessageItemProps {
  message: Message;
}

export default function ChatMessageItem({ message }: ChatMessageItemProps) {
  return (
    <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2`}>
      <div
        className={`max-w-[90%] rounded-[1.5rem] px-6 py-4 shadow-xl ${
          message.role === 'user'
            ? 'bg-primary text-primary-foreground border border-primary/20 rounded-tr-md'
            : 'bg-transparent text-foreground rounded-tl-md'
        }`}
      >
        {message.role === 'assistant' && (
          <div className="text-emerald-500 mb-2 font-bold text-[10px] uppercase tracking-widest flex items-center gap-1.5">
            <span className="w-1 h-3 bg-emerald-500 rounded-full"></span> Assistant
          </div>
        )}
        <p className="text-base leading-relaxed tracking-tight whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
