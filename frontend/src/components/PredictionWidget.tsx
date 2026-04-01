'use client';

import React, { useEffect, useState } from 'react';

interface PredictionPoint {
  date: string;
  predicted_close: number;
  lower_bound: number;
  upper_bound: number;
  trend: string;
}

interface PredictionData {
  symbol: string;
  version: string;
  trained_at: string;
  metrics: { mae?: number; rmse?: number; mape?: number };
  predictions: PredictionPoint[];
}

export default function PredictionWidget({ symbol }: { symbol: string }) {
  const [data, setData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMore, setShowMore] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:8000/api/predict/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticker: symbol, days: 10 }),
        });
        
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || `API Error: ${response.status}`);
        }
        
        const json = await response.json();
        if (isMounted) setData(json);
      } catch (err: any) {
        if (isMounted) setError(err.message);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPrediction();
    return () => { isMounted = false; };
  }, [symbol]);

  if (loading) {
    return (
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-center items-center h-full min-h-[140px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500/50"></div>
        <p className="text-xs text-slate-400 mt-3 font-medium tracking-wide">Prophet đang phân tích...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col h-full min-h-[140px] justify-between">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">Dự báo Prophet (10 phiên)</h3>
        <p className="text-xs text-rose-400/90 flex flex-col gap-1">
           <span className="font-semibold flex items-center gap-1">
             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
               <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
             </svg>
             Chưa có mô hình:
           </span> 
           <span className="text-[11px] leading-tight break-words line-clamp-2">{error || "Không có kết nối."}</span>
        </p>
      </div>
    );
  }

  const preds = data.predictions;
  const firstPred = preds[0];
  const lastPred = preds[preds.length - 1];
  const isUp = lastPred.predicted_close >= firstPred.predicted_close;
  const changePercent = ((lastPred.predicted_close - firstPred.predicted_close) / firstPred.predicted_close * 100);
  const mape = data.metrics?.mape;
  const confidence = mape != null ? Math.max(0, Math.min(100, 100 - mape)) : null;

  return (
    <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-between h-full relative overflow-hidden group hover:border-slate-600 transition-colors">
       <div className="flex items-center justify-between mb-3">
         <h3 className="text-sm font-semibold text-slate-400 flex items-center gap-2">
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-amber-500">
             <path fillRule="evenodd" d="M12.577 4.878a.75.75 0 01.919-.53l4.78 1.281a.75.75 0 01.531.919l-1.281 4.78a.75.75 0 01-1.449-.387l.81-3.022a19.407 19.407 0 00-5.594 5.203.75.75 0 01-1.139.093L7 10.06l-4.72 4.72a.75.75 0 01-1.06-1.06l5.25-5.25a.75.75 0 011.06 0l3.074 3.073a20.923 20.923 0 015.545-4.931l-3.042.815a.75.75 0 01-.53-.919z" clipRule="evenodd" />
           </svg>
           Dự báo Prophet (10 phiên)
         </h3>
         <button 
           onClick={() => setShowMore(!showMore)}
           className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center gap-1 transition-colors"
         >
           {showMore ? 'Thu gọn' : 'Chi tiết'}
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`w-3.5 h-3.5 transition-transform ${showMore ? 'rotate-180' : ''}`}>
             <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
           </svg>
         </button>
       </div>
       
       <div className="z-10 relative space-y-3">
         <div className="flex items-end gap-3 mb-1">
           <div className={`text-3xl font-bold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
             {isUp ? 'TĂNG' : 'GIẢM'}
           </div>
           <div className={`text-sm font-medium mb-1 tracking-tight ${isUp ? 'text-emerald-500/70' : 'text-rose-500/70'}`}>
             {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
           </div>
         </div>

         {/* Mini sparkline of predictions */}
         <div className="flex items-end gap-[2px] h-8">
           {preds.map((p, i) => {
             const min = Math.min(...preds.map(x => x.predicted_close));
             const max = Math.max(...preds.map(x => x.predicted_close));
             const range = max - min || 1;
             const height = ((p.predicted_close - min) / range) * 100;
             return (
               <div
                 key={i}
                 className={`flex-1 rounded-t-sm transition-all ${
                   p.trend === 'UP' ? 'bg-emerald-500/60' : 'bg-rose-500/60'
                 }`}
                 style={{ height: `${Math.max(10, height)}%` }}
                 title={`${new Date(p.date).toLocaleDateString('vi-VN')}: ${p.predicted_close.toLocaleString('vi-VN')} ₫`}
               />
             );
           })}
         </div>

         <div className="flex justify-between items-center text-[10px] text-slate-500">
           <span>{new Date(firstPred.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}</span>
           <span>→</span>
           <span>{new Date(lastPred.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}</span>
         </div>

         {confidence != null && (
           <>
             <div className="flex justify-between items-center">
                <p className="text-xs text-slate-500">Độ chính xác (100 - MAPE)</p>
                <span className="text-xs font-bold text-slate-300">{confidence.toFixed(1)}%</span>
             </div>
             <div className="w-full bg-slate-900 rounded-full h-1.5">
                 <div className={`h-1.5 rounded-full transition-all duration-1000 ${confidence > 90 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : confidence > 80 ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]'}`} style={{width: `${confidence}%`}}></div>
             </div>
           </>
         )}
       </div>

       {/* Detailed predictions table */}
       {showMore && (
         <div className="mt-4 pt-4 border-t border-slate-700/50">
           <div className="space-y-1.5 max-h-48 overflow-y-auto">
             {preds.map((p, i) => (
               <div key={i} className="flex items-center justify-between text-xs py-1 px-2 rounded-lg hover:bg-slate-700/20 transition-colors">
                 <span className="text-slate-400 font-medium w-16">
                   {new Date(p.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })}
                 </span>
                 <span className={`font-bold ${p.trend === 'UP' ? 'text-emerald-400' : 'text-rose-400'}`}>
                   {p.predicted_close.toLocaleString('vi-VN')} ₫
                 </span>
                 <span className="text-slate-500 text-[10px] w-28 text-right">
                   {p.lower_bound.toLocaleString('vi-VN')} – {p.upper_bound.toLocaleString('vi-VN')}
                 </span>
                 <span className={`text-[10px] font-bold ${p.trend === 'UP' ? 'text-emerald-500' : 'text-rose-500'}`}>
                   {p.trend === 'UP' ? '▲' : '▼'}
                 </span>
               </div>
             ))}
           </div>
           {data.metrics && (
             <div className="mt-3 pt-3 border-t border-slate-700/30 grid grid-cols-3 gap-2 text-[10px]">
               <div className="text-center">
                 <span className="text-slate-500 block">MAE</span>
                 <span className="text-slate-300 font-bold">{data.metrics.mae?.toFixed(4) || '-'}</span>
               </div>
               <div className="text-center">
                 <span className="text-slate-500 block">RMSE</span>
                 <span className="text-slate-300 font-bold">{data.metrics.rmse?.toFixed(4) || '-'}</span>
               </div>
               <div className="text-center">
                 <span className="text-slate-500 block">MAPE</span>
                 <span className="text-slate-300 font-bold">{data.metrics.mape?.toFixed(2) || '-'}%</span>
               </div>
             </div>
           )}
         </div>
       )}

       <div className="mt-3 flex items-center justify-between text-[10px] text-slate-500">
         <span>Model: {data.version}</span>
         <span className="flex items-center gap-1">
           <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
           Prophet Forecast
         </span>
       </div>

       {/* Decorative gradient overlay */}
       <div className={`absolute -bottom-10 -right-10 w-32 h-32 rounded-full blur-3xl opacity-10 pointer-events-none transition-colors ${isUp ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
    </div>
  );
}
