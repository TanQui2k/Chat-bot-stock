'use client';

import React, { useEffect, useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
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
  
  return (
    <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl shadow-lg relative overflow-hidden flex flex-col min-h-[400px]">
      {/* Asset Header Info */}
      <div className="border-b border-slate-800/60 bg-slate-900/50 p-4 shrink-0 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
            <span className="text-indigo-400 font-bold text-sm tracking-widest">{symbol}</span>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-200">Mã Cổ phiếu {symbol}</h2>
            <p className="text-xs text-slate-500 font-medium tracking-wide">LỊCH SỬ GIAO DỊCH DATABASE</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white tracking-tight">{(latestPrice).toLocaleString('vi-VN')} ₫</div>
          <div className={`text-sm font-medium flex items-center justify-end gap-1 ${diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {diff >= 0 ? '+' : ''}{(diff).toLocaleString('vi-VN')} ({diff >= 0 ? '+' : ''}{pct.toFixed(2)}%)
          </div>
        </div>
      </div>

      {/* Chart Canvas utilizing Recharts */}
      <div className="p-4 flex-1 flex flex-col relative bg-slate-950/20">
        {loading ? (
             <div className="flex items-center justify-center flex-1">
                 <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
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
    </div>
  );
}
