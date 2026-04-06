import React from 'react';

const SUGGESTIONS = [
  { icon: '💰', text: 'Giá FPT hiện tại', action: 'Giá FPT hiện tại là bao nhiêu?' },
  { icon: '📈', text: 'Phân tích kỹ thuật VNM', action: 'Phân tích kỹ thuật cổ phiếu VNM' },
  { icon: '📊', text: 'Dự báo xu hướng MSN', action: 'Dự đoán giá MSN trong 24h tới' },
];

interface ChatWelcomeProps {
  onSuggestionClick: (action: string) => void;
}

export default function ChatWelcome({ onSuggestionClick }: ChatWelcomeProps) {
  return (
    <>
      <div className="flex flex-col items-center mb-10 animate-in fade-in zoom-in duration-1000">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 shadow-lg">
            <svg
              viewBox="0 0 24 24"
              className="w-10 h-10 text-emerald-500"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <h1 className="text-6xl font-bold tracking-tighter text-foreground">StockAI</h1>
        </div>
        <p className="text-muted-foreground text-xl font-medium">Trao đổi cùng Trợ lý Chứng khoán AI</p>
      </div>

      <div className="w-full mt-12 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
        <div className="flex items-center justify-center gap-6 mb-8">
          <div className="h-px bg-border flex-1 max-w-[100px]"></div>
          <span className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground font-bold whitespace-nowrap">
            Câu hỏi thường gặp
          </span>
          <div className="h-px bg-border flex-1 max-w-[100px]"></div>
        </div>
        <div className="grid grid-cols-1 gap-3.5 max-w-xl mx-auto px-4">
          {SUGGESTIONS.map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSuggestionClick(item.action)}
              className="flex items-center justify-center gap-4 p-4 rounded-[1.8rem] bg-card/60 border border-border hover:border-emerald-500/30 hover:bg-muted transition-all text-center group shadow-md cursor-pointer"
            >
              <span className="text-2xl transition-opacity transform group-hover:scale-110 duration-300 pointer-events-none">
                {item.icon}
              </span>
              <span className="text-muted-foreground group-hover:text-foreground text-sm font-semibold tracking-wide pointer-events-none">
                {item.text}
              </span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}
