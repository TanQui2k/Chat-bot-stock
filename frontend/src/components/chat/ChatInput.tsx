import React, { useRef, useEffect } from 'react';

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  isLoading: boolean;
  onSend: () => void;
}

export default function ChatInput({ input, setInput, isLoading, onSend }: ChatInputProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
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
          <button
            onClick={onSend}
            disabled={!input.trim() || isLoading}
            className={`p-2.5 rounded-full transition-all shadow-lg cursor-pointer ${
              input.trim() && !isLoading
                ? 'bg-emerald-500 text-white hover:bg-emerald-400 hover:scale-105 active:scale-95'
                : 'bg-muted text-muted-foreground opacity-50'
            }`}
            aria-label="Gửi tin nhắn"
          >
            <svg
              viewBox="0 0 24 24"
              className="w-5.5 h-5.5"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
