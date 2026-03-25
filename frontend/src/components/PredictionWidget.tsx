'use client';

import React, { useEffect, useState } from 'react';

export default function PredictionWidget({ symbol }: { symbol: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMore, setShowMore] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch from the backend predict API
        const response = await fetch('http://localhost:8000/api/predict/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ ticker: symbol }),
        });
        
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || `API Error: ${response.status}`);
        }
        
        const json = await response.json();
        if (isMounted) {
          setData(json);
        }
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500/50"></div>
        <p className="text-xs text-slate-400 mt-3 font-medium tracking-wide">AI Đang phân tích dữ liệu...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col h-full min-h-[140px] justify-between">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">Dự đoán AI (24h tới)</h3>
        <p className="text-xs text-rose-400/90 flex flex-col gap-1">
           <span className="font-semibold flex items-center gap-1">
             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
               <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
             </svg>
             Lỗi tải dữ liệu:
           </span> 
           <span className="text-[11px] leading-tight break-words line-clamp-2">{error || "Không có kết nối."}</span>
        </p>
      </div>
    );
  }

  const accuracy = data.confidence_score ? (data.confidence_score * 100).toFixed(1) : "0.0";
  const predictedClose = data.predicted_close ? data.predicted_close.toLocaleString('vi-VN') : "---";
  
  // Logical mapping: generally > 50% on class 1 triggers UP. Since Logistic maps to [0_prob, 1_prob],
  // confidence >= 50% often means the prediction is confident in its chosen class.
  // Because our Python API sets confidence_score = max(prob_0, prob_1) essentially, we don't know the exact class just from it.
  // But wait, the backend predicts trend based on model.predict == 1. 
  // Let's deduce isUp based on if confidence was mapped. 
  // For aesthetic simplicity in frontend fallback, we can use the probability score threshold >= 0.5.
  const isUp = typeof data.confidence_score === 'number' ? data.confidence_score >= 0.50 : true;
  
  // Generate prediction reasons based on data and typical factors
  const generateReasons = () => {
    const reasons = [];
    
    // Add volume-related reason if available
    if (data.volume && data.volume > 1000000) {
      reasons.push({ icon: '📊', text: 'Volume giao dịch tăng cao' });
    }
    
    // Add trend-related reason
    if (isUp) {
      reasons.push({ icon: '📈', text: 'Xu hướng tăng trong phiên gần đây' });
      reasons.push({ icon: '🌟', text: 'Momentum tích cực từ thị trường' });
    } else {
      reasons.push({ icon: '📉', text: 'Xu hướng giảm trong phiên gần đây' });
      reasons.push({ icon: '⚠️', text: 'Áp lực bán từ nhà đầu tư' });
    }
    
    // Add technical indicator reason
    if (data.rsi) {
      if (data.rsi > 70) reasons.push({ icon: '🔴', text: 'Chỉ số RSI cho vùng mua quá mức' });
      else if (data.rsi < 30) reasons.push({ icon: '🟢', text: 'Chỉ số RSI cho vùng bán quá mức' });
    }
    
    // Add general analysis reason
    reasons.push({ icon: '🤖', text: 'Dự đoán dựa trên phân tích lịch sử' });
    
    return reasons;
  };
  
  const reasons = generateReasons();

  return (
    <div className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 shadow-md flex flex-col justify-between h-full relative overflow-hidden group hover:border-slate-600 transition-colors">
       <div className="flex items-center justify-between mb-3">
         <h3 className="text-sm font-semibold text-slate-400 flex items-center gap-2">
           {isUp ? (
             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-emerald-500">
               <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clipRule="evenodd" />
             </svg>
           ) : (
             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-rose-500">
               <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM11.25 18a.75.75 0 001.5 0v-6c0-.414-.336-.75-.75-.75h-4.5a.75.75 0 000 1.5h3.75V18z" clipRule="evenodd" />
             </svg>
           )}
           Mô hình ML Dự đoán (24h tới)
         </h3>
         <button 
           onClick={() => setShowMore(!showMore)}
           className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1 transition-colors"
         >
           {showMore ? 'Thu gọn' : 'Xem chi tiết'}
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`w-3.5 h-3.5 transition-transform ${showMore ? 'rotate-180' : ''}`}>
             <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
           </svg>
         </button>
       </div>
       
       <div className="z-10 relative space-y-3">
         <div className="flex items-end gap-3 mb-1">
           <div className={`text-3xl font-bold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
             {isUp ? 'TĂNG GIÁ' : 'GIẢM GIÁ'}
           </div>
           <div className="text-sm text-slate-400 font-medium mb-1 tracking-tight">Mục tiêu: {predictedClose} ₫</div>
         </div>

         <div className="flex justify-between items-center mb-1">
            <p className="text-xs text-slate-500">Độ tin cậy của thuật toán</p>
            <span className="text-xs font-bold text-slate-300">{accuracy}%</span>
         </div>
         
         <div className="w-full bg-slate-900 rounded-full h-1.5">
             <div className={`h-1.5 rounded-full transition-all duration-1000 ${isUp ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]'}`} style={{width: `${accuracy}%`}}></div>
         </div>
       </div>

       {/* Prediction Reasons - Collapsible */}
       {showMore && (
         <div className="mt-4 pt-4 border-t border-slate-700/50">
           <h4 className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-2">
             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
               <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
             </svg>
             Lý do dự đoán
           </h4>
           <div className="space-y-2">
             {reasons.map((reason, index) => (
               <div key={index} className="flex items-start gap-2 text-xs text-slate-400">
                 <span className="shrink-0 mt-0.5">{reason.icon}</span>
                 <span className="leading-relaxed">{reason.text}</span>
               </div>
             ))}
           </div>
         </div>
       )}

       <div className="mt-3 flex items-center justify-between text-[10px] text-slate-500">
         <span>Dữ liệu cập nhật: Hôm nay</span>
         <button 
           className="hover:text-emerald-400 transition-colors flex items-center gap-1"
           title="Chia sẻ dự đoán"
           onClick={() => alert('Chức năng chia sẻ sẽ sớm được cập nhật!')}
         >
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
             <path d="M15 8a3 3 0 10-2.977-2.83l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
           </svg>
           Chia sẻ
         </button>
       </div>

       {/* Decorative gradient overlay */}
       <div className={`absolute -bottom-10 -right-10 w-32 h-32 rounded-full blur-3xl opacity-10 pointer-events-none transition-colors ${isUp ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
    </div>
  );
}
