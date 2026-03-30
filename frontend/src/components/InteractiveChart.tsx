'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface PriceData {
  id: number;
  ticker_id: number;
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export default function InteractiveChart({ symbol }: { symbol: string }) {
  const [data, setData] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState('1M');
  const [showIndicators, setShowIndicators] = useState(true);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchPrices = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`http://localhost:8000/api/stocks/${symbol}/history`);
        if (!res.ok) throw new Error("Lỗi tải dữ liệu hoặc mã không tồn tại!");
        
        const json = await res.json();
        if (isMounted) setData(json);
      } catch (err: any) {
        if (isMounted) setError(err.message);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchPrices();
    return () => { isMounted = false; };
  }, [symbol]);

  // Transform for recharts format (DD/MM labeling requires date objects or strings)
  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
    price: item.close || 0
  }));

  const latestPrice = data.length > 0 ? (data[data.length - 1].close || 0) : 0;
  const prevPrice = data.length > 1 ? (data[data.length - 2].close || 0) : 0;
  const diff = latestPrice - prevPrice;
  const pct = prevPrice > 0 ? (diff / prevPrice) * 100 : 0;
  
  // Calculate simple MA20
  const calculateMA = (period: number) => {
    if (data.length < period) return null;
    const slice = data.slice(-period);
    const sum = slice.reduce((acc, curr) => acc + (curr.close || 0), 0);
    return sum / period;
  };
  
  const ma20 = calculateMA(20);
  const ma50 = calculateMA(50);
  
  // Calculate RSI (simplified)
  const calculateRSI = () => {
    if (data.length < 14) return 50;
    let gains = 0, losses = 0;
    for (let i = data.length - 14; i < data.length - 1; i++) {
      const diff = (data[i + 1].close || 0) - (data[i].close || 0);
      if (diff >= 0) gains += diff;
      else losses -= diff;
    }
    const rs = losses > 0 ? gains / losses : 100;
    return 100 - (100 / (1 + rs));
  };
  
  const rsi = calculateRSI();
  const rsiColor = rsi > 70 ? 'text-rose-400' : rsi < 30 ? 'text-emerald-400' : 'text-slate-400';
  const rsiLabel = rsi > 70 ? 'Mua quá mức' : rsi < 30 ? 'Bán quá mức' : 'Trung tính';
  
  return (
    <div className="flex-1 bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl relative overflow-hidden flex flex-col min-h-[400px] ring-1 ring-white/5">
      {/* Asset Header Info with Indicators and Controls */}
      <div className="border-b border-slate-800/60 bg-slate-900/50 p-4 shrink-0 flex flex-col gap-3 z-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 flex-1">
            <div className="h-10 w-10 rounded-full bg-violet-500/10 border border-violet-500/20 flex items-center justify-center shrink-0">
              <span className="text-violet-400 font-bold text-sm tracking-widest">{symbol}</span>
            </div>
            <div className="flex flex-col">
              <h2 className="text-lg font-semibold text-slate-200">Mã Cổ phiếu {symbol}</h2>
              <p className="text-xs text-slate-500 font-medium tracking-wide">LỊCH SỬ GIAO DỊCH DATABASE</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setShowIndicators(!showIndicators)}
              className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/50 hover:bg-slate-700/50 hover:border-slate-600 text-slate-300 hover:text-emerald-400 text-xs font-semibold transition-all flex items-center gap-1.5"
              title="Hiện/Ẩn chỉ số kỹ thuật"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.663.104 1.364.025 2.002a12.02 12.02 0 01-3.675 6.576.915 915 0 01-2.773 1.248 10.56 10.56 0 00-3.353.982.915 915 0 01-1.385-1.385c.503-.466.925-1.022 1.248-1.659A12.03 12.03 0 015.166 9.66a12.02 12.02 0 01-3.675-4.665c-.079-.638-.085-1.339.025-2.002z" />
                <path d="M10 13a3 3 0 100-6 3 3 0 000 6z" />
              </svg>
              Indicators
            </button>
            <div className="flex bg-slate-800/50 rounded-lg p-0.5 border border-slate-700">
              {['1D', '1W', '1M', '3M', '6M', '1Y'].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    timeframe === tf 
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
            <button 
              className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/50 hover:bg-slate-700/50 hover:border-slate-600 text-slate-300 hover:text-emerald-400 text-xs font-semibold transition-all flex items-center gap-1.5"
              title="Tải biểu đồ"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Tải
            </button>
          </div>
        </div>
        
        {/* Technical Indicators Display */}
        {showIndicators && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs border-t border-slate-800/50 pt-3">
            <div className="flex flex-col gap-0.5">
              <span className="text-slate-500">Giá hiện tại</span>
              <span className={`font-semibold ${diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {(latestPrice).toLocaleString('vi-VN')} ₫
              </span>
              <span className={`${diff >= 0 ? 'text-emerald-500/70' : 'text-rose-500/70'} text-[10px]`}>
                {diff >= 0 ? '+' : ''}{(diff).toLocaleString('vi-VN')} ({diff >= 0 ? '+' : ''}{pct.toFixed(2)}%)
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-slate-500">MA 20</span>
              <span className="text-indigo-400 font-medium">
                {ma20 ? ma20.toLocaleString('vi-VN', { maximumFractionDigits: 0 }) : '-'} ₫
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-slate-500">MA 50</span>
              <span className="text-cyan-400 font-medium">
                {ma50 ? ma50.toLocaleString('vi-VN', { maximumFractionDigits: 0 }) : '-'} ₫
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-slate-500">RSI (14)</span>
              <span className={`font-medium ${rsiColor}`}>
                {rsi.toFixed(1)} - {rsiLabel}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Chart Canvas utilizing Recharts */}
      <div className="p-2 flex-1 flex flex-col relative bg-transparent">
        {loading ? (
             <div className="flex flex-col items-center justify-center flex-1 p-8 space-y-4">
                 <div className="w-full h-full bg-slate-800/30 rounded-xl animate-pulse flex items-center justify-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
                      <span className="text-xs font-medium">Đang tải dữ liệu biểu đồ...</span>
                    </div>
                 </div>
             </div>
        ) : error ? (
            <div className="flex items-center justify-center flex-1 text-rose-500 text-sm">{error}</div>
        ) : data.length === 0 ? (
            <div className="flex items-center justify-center flex-1 text-slate-500 text-sm">Chưa có dữ liệu giao dịch.</div>
        ) : (
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                 <defs>
                   <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor={diff >= 0 ? "#10b981" : "#f43f5e"} stopOpacity={0.3}/>
                     <stop offset="95%" stopColor={diff >= 0 ? "#10b981" : "#f43f5e"} stopOpacity={0}/>
                   </linearGradient>
                   {showIndicators && ma20 && (
                     <linearGradient id="colorMA20" x1="0" y1="0" x2="0" y2="1">
                       <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.5}/>
                       <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                     </linearGradient>
                   )}
                   {showIndicators && ma50 && (
                     <linearGradient id="colorMA50" x1="0" y1="0" x2="0" y2="1">
                       <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.5}/>
                       <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1}/>
                     </linearGradient>
                   )}
                 </defs>
                 <XAxis dataKey="date" stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} />
                 <YAxis 
                    stroke="#475569" 
                    fontSize={11} 
                    tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} 
                    domain={['auto', 'auto']}
                    axisLine={false}
                    tickLine={false}
                  />
                 {showIndicators && ma20 && (
                   <ReferenceLine y={ma20} stroke="#8b5cf6" strokeDasharray="3 3" label={{ position: 'right', value: 'MA20', fill: '#8b5cf6', fontSize: 10 }} ifOverflow="extendDomain" />
                 )}
                 {showIndicators && ma50 && (
                   <ReferenceLine y={ma50} stroke="#06b6d4" strokeDasharray="3 3" label={{ position: 'right', value: 'MA50', fill: '#06b6d4', fontSize: 10 }} ifOverflow="extendDomain" />
                 )}
                 <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                 <Tooltip 
                   contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                   itemStyle={{ color: diff >= 0 ? '#10b981' : '#f43f5e', fontWeight: 600 }}
                   labelStyle={{ color: '#94a3b8' }}
                   formatter={(value: any) => [`${Number(value).toLocaleString('vi-VN')} ₫`, 'Giá đóng cửa']}
                 />
                 <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke={diff >= 0 ? "#10b981" : "#f43f5e"} 
                    strokeWidth={2} 
                    fillOpacity={1} 
                    fill="url(#colorPrice)" 
                  />
               </AreaChart>
             </ResponsiveContainer>
        )}
      </div>
      
      {/* Chart Tools Footer */}
      <div className="border-t border-slate-800/60 bg-slate-900/50 px-4 py-2 flex items-center justify-between text-xs text-slate-500">
        <div className="flex gap-4">
          <span>Thời gian: {timeframe}</span>
          <span>Lượt chạm: {data.length}</span>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => alert('Chức năng đo lường sẽ sớm được cập nhật!')}
            className="flex items-center gap-1 hover:text-emerald-400 transition-colors"
            title="Đo lường khoảng cách"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M8.5 2.5a.5.5 0 01.5-.5h3a.5.5 0 01.5.5v.5h.5a1 1 0 011 1v3a.5.5 0 01-.5.5h-.5v.5a.5.5 0 01-.5.5h-3a.5.5 0 01-.5-.5v-.5h-.5a1 1 0 01-1-1v-3a.5.5 0 01.5-.5h.5v-.5z" />
              <path fillRule="evenodd" d="M3 10a7 7 0 1114 0 7 7 0 01-14 0zm14 0a6 6 0 11-12 0 6 6 0 0112 0z" clipRule="evenodd" />
            </svg>
            Measure
          </button>
          <button 
            onClick={() => alert('Reset view')}
            className="flex items-center gap-1 hover:text-emerald-400 transition-colors"
            title="Đặt lại hiển thị"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
