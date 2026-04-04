'use client';

import React, { useState } from "react";
import InteractiveChart from "@/components/InteractiveChart";
import ChatInterface from "@/components/ChatInterface";
import { useAuth } from "@/context/AuthContext";

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('FPT');
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen flex flex-col bg-background overflow-hidden transition-colors duration-300">
      <DashboardContent
        selectedTicker={selectedTicker}
        setSelectedTicker={setSelectedTicker}
      />
    </div>
  );
}

function DashboardContent({
  selectedTicker,
  setSelectedTicker,
}: {
  selectedTicker: string;
  setSelectedTicker: (ticker: string) => void;
}) {
  const [isMobileChatOpen, setIsMobileChatOpen] = useState(false);

  return (
    <div className="w-full flex-1 flex flex-col px-6 pb-6 pt-2 overflow-hidden">
      {/* Main Grid Layout Container */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1 min-h-0 relative">

        {/* Left Column: Market Chart - Full Height */}
        <div className="md:col-span-8 flex flex-col min-h-0 w-full animate-in fade-in slide-in-from-left-4 duration-700 h-full relative">
          <InteractiveChart
            symbol={selectedTicker}
            setSelectedTicker={setSelectedTicker}
          />
        </div>

        {/* Right Column: AI Trading Assistant - Stretched to fill Height */}
        <div className={`md:col-span-4 h-full relative z-40 transition-all duration-300 md:block animate-in fade-in slide-in-from-right-4 duration-700 ${isMobileChatOpen
            ? 'fixed inset-0 top-0 pt-20 p-4 bg-background/90 backdrop-blur-md shadow-2xl block'
            : 'hidden'
          }`}>
          {isMobileChatOpen && (
            <button
              onClick={() => setIsMobileChatOpen(false)}
              className="md:hidden absolute top-6 right-6 p-2.5 bg-card text-foreground rounded-full border border-border z-50 hover:bg-muted shadow-lg"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          {/* Wrapper to fix Chat height within the grid cell */}
          <div className="absolute inset-x-0 inset-y-0 h-full overflow-hidden">
            <ChatInterface />
          </div>
        </div>

        {/* Mobile FAB to open Chat */}
        {!isMobileChatOpen && (
          <button
            onClick={() => setIsMobileChatOpen(true)}
            className="md:hidden fixed bottom-8 right-8 w-16 h-16 bg-violet-600 shadow-[0_8px_30px_rgba(124,58,237,0.5)] rounded-full flex items-center justify-center text-white z-50 hover:bg-violet-500 hover:scale-110 active:scale-95 transition-all duration-200 animate-bounce-subtle"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8">
              <path fillRule="evenodd" d="M4.804 21.644A6.707 6.707 0 006 21.75a6.721 6.721 0 003.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 01-.814 1.686.75.75 0 00.44 1.223zM8.25 10.875a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25zM10.875 12a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0zm4.875-1.125a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}