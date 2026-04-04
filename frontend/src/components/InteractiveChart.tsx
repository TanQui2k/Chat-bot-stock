'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

import Fuse from 'fuse.js';

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

interface PredictionPoint {
  date: string;
  predicted_close: number;
  lower_bound: number;
  upper_bound: number;
  trend: string;
}

interface PredictionResponse {
  symbol: string;
  version: string;
  trained_at: string;
  metrics: { mae?: number; rmse?: number; mape?: number };
  predictions: PredictionPoint[];
  history: { date: string; close: number | null }[];
}

const popularTickers = ['FPT', 'VNM', 'MSN', 'VPB', 'ACB', 'HPG', 'VIC', 'VCB'];

export default function InteractiveChart({
  symbol,
  setSelectedTicker
}: {
  symbol: string;
  setSelectedTicker: (ticker: string) => void;
}) {
  const [data, setData] = useState<PriceData[]>([]);
  const [allTickers, setAllTickers] = useState<{ symbol: string, name: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState('1M');
  const [showTickerMenu, setShowTickerMenu] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const chartRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Prediction state
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [predLoading, setPredLoading] = useState(false);
  const [showPrediction, setShowPrediction] = useState(true);

  // Fetch all tickers from database
  useEffect(() => {
    let isMounted = true;
    const fetchTickers = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const res = await fetch(`${baseUrl}/stocks/`);
        if (res.ok) {
          const json = await res.json();
          if (isMounted) {
            setAllTickers(json.map((t: any) => ({
              symbol: t.symbol,
              name: t.name || t.company_name || 'Công ty Cổ phần ' + t.symbol
            })));
          }
        }
      } catch (err) {
        console.error("Failed to load tickers", err);
      }
    };
    fetchTickers();
    return () => { isMounted = false; };
  }, []);

  const fuseOptions = {
    keys: ['symbol', 'name'],
    threshold: 0.3,
    minMatchCharLength: 1
  };
  const fuse = new Fuse(allTickers, fuseOptions);

  // Auto-focus search input when menu opens
  useEffect(() => {
    if (showTickerMenu && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 50);
    }
  }, [showTickerMenu]);

  const searchResults = searchTerm
    ? fuse.search(searchTerm).map(result => result.item)
    : popularTickers.filter(ticker => allTickers.map(t => t.symbol).includes(ticker))
      .map(ticker => allTickers.find(t => t.symbol === ticker) || { symbol: ticker, name: '' });

  const displayResults = searchTerm
    ? searchResults
    : (searchResults.length > 0 ? searchResults : allTickers.slice(0, 20));

  const handleSearch = () => {
    if (searchResults.length > 0) {
      setSelectedTicker(searchResults[0].symbol);
      setShowTickerMenu(false);
      setSearchTerm("");
    } else {
      const val = searchTerm.trim().toUpperCase();
      if (val) {
        setSelectedTicker(val);
        setShowTickerMenu(false);
        setSearchTerm("");
      }
    }
  };

  // Fetch historical prices
  useEffect(() => {
    let isMounted = true;
    const fetchPrices = async () => {
      try {
        setLoading(true);
        setError(null);
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const res = await fetch(`${baseUrl}/stocks/${symbol}/history`);
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

  // Fetch prediction when symbol changes
  useEffect(() => {
    let isMounted = true;
    const fetchPrediction = async () => {
      try {
        setPredLoading(true);
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const res = await fetch(`${baseUrl.replace('/api', '')}/api/predict/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticker: symbol, days: 10 }),
        });
        if (res.ok) {
          const json = await res.json();
          if (isMounted) setPrediction(json);
        } else {
          if (isMounted) setPrediction(null);
        }
      } catch (err) {
        console.error("Prediction fetch failed:", err);
        if (isMounted) setPrediction(null);
      } finally {
        if (isMounted) setPredLoading(false);
      }
    };
    fetchPrediction();
    return () => { isMounted = false; };
  }, [symbol]);

  // Merge historical data + prediction into single chart dataset
  const chartData = (() => {
    // Historical data points
    const historyPoints = data.map(item => ({
      date: new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
      fullDate: item.date,
      price: item.close || 0,
      predicted: null as number | null,
      upperBound: null as number | null,
      lowerBound: null as number | null,
    }));

    // If we have predictions and they should be shown
    if (showPrediction && prediction && prediction.predictions.length > 0) {
      // Add bridge point: last historical point also starts prediction line
      if (historyPoints.length > 0) {
        const lastPoint = historyPoints[historyPoints.length - 1];
        lastPoint.predicted = lastPoint.price;
        lastPoint.upperBound = lastPoint.price;
        lastPoint.lowerBound = lastPoint.price;
      }

      // Add prediction points
      for (const pred of prediction.predictions) {
        historyPoints.push({
          date: new Date(pred.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
          fullDate: pred.date,
          price: null as any,
          predicted: pred.predicted_close,
          upperBound: pred.upper_bound,
          lowerBound: pred.lower_bound,
        });
      }
    }

    return historyPoints;
  })();

  const latestPrice = data.length > 0 ? (data[data.length - 1].close || 0) : 0;
  const prevPrice = data.length > 1 ? (data[data.length - 2].close || 0) : 0;
  const diff = latestPrice - prevPrice;
  const pct = prevPrice > 0 ? (diff / prevPrice) * 100 : 0;



  // Prediction summary info
  const predSummary = prediction?.predictions?.length
    ? {
      lastPred: prediction.predictions[prediction.predictions.length - 1],
      firstPred: prediction.predictions[0],
      mape: prediction.metrics?.mape,
    }
    : null;

  const predTrend = predSummary
    ? (predSummary.lastPred.predicted_close >= latestPrice ? 'UP' : 'DOWN')
    : null;

  const predChange = predSummary
    ? ((predSummary.lastPred.predicted_close - latestPrice) / latestPrice * 100)
    : 0;

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) return null;

    const priceVal = payload.find((p: any) => p.dataKey === 'price');
    const predVal = payload.find((p: any) => p.dataKey === 'predicted');
    const upperVal = payload.find((p: any) => p.dataKey === 'upperBound');
    const lowerVal = payload.find((p: any) => p.dataKey === 'lowerBound');

    return (
      <div className="bg-slate-900/95 border border-slate-700/50 rounded-xl px-5 py-4 shadow-2xl backdrop-blur-md ring-1 ring-white/10">
        <p className="text-slate-400 text-xs uppercase tracking-wider mb-3 font-bold">{label}</p>
        {priceVal?.value != null && (
          <div className="flex items-center justify-between gap-6">
            <span className="text-slate-400 text-sm">Giá:</span>
            <span className="text-base font-bold text-white">
              {Number(priceVal.value).toLocaleString('vi-VN')} ₫
            </span>
          </div>
        )}
        {predVal?.value != null && (
          <div className="mt-3 pt-3 border-t border-slate-800">
            <div className="flex items-center justify-between gap-6">
              <span className="text-amber-400/80 text-sm">Dự báo:</span>
              <span className="text-base font-bold text-amber-400">
                {Number(predVal.value).toLocaleString('vi-VN')} ₫
              </span>
            </div>
            {upperVal?.value != null && lowerVal?.value != null && (
              <div className="flex items-center justify-between gap-6 mt-1.5">
                <span className="text-slate-500 text-[11px]">Khoảng tin cậy:</span>
                <span className="text-[11px] text-slate-400 font-medium">
                  {Number(lowerVal.value).toLocaleString('vi-VN')} - {Number(upperVal.value).toLocaleString('vi-VN')}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full bg-card/40 backdrop-blur-xl border border-border/80 rounded-2xl shadow-2xl relative overflow-hidden flex flex-col min-h-[700px] ring-1 ring-inset ring-white/5 dark:ring-white/10">
      <div className="border-b border-border/60 bg-card/50 p-5 shrink-0 flex flex-col gap-3 z-20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 flex-1">
            <div className="relative">
              <button
                onClick={() => setShowTickerMenu(!showTickerMenu)}
                className="h-10 px-3 min-w-[70px] rounded-xl bg-violet-600 shadow-[0_0_15px_rgba(124,58,237,0.3)] border border-violet-400/30 flex items-center justify-center hover:bg-violet-500 transition-all group"
              >
                <span className="text-white font-bold text-sm tracking-widest">{symbol}</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`w-3.5 h-3.5 text-violet-200 ml-1.5 transition-transform duration-200 ${showTickerMenu ? 'rotate-180' : ''}`}>
                  <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                </svg>
              </button>

              {showTickerMenu && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-card/95 border border-border/80 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100 backdrop-blur-xl flex flex-col">
                  <div className="p-2.5 border-b border-border bg-card/60">
                    <div className="relative flex items-center gap-1.5">
                      <input
                        ref={searchInputRef}
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Tìm mã hoặc tên công ty..."
                        className="w-full px-3 py-2 text-xs bg-muted border border-border rounded-lg focus:outline-none focus:border-violet-500 transition-all text-foreground"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSearch();
                        }}
                      />
                    </div>
                  </div>
                  <div className="px-3 py-2 border-b border-border bg-card/40 text-xs font-semibold text-muted-foreground uppercase tracking-widest flex justify-between">
                    <span>{searchTerm ? 'Kết quả tìm kiếm' : 'Nổi bật'}</span>
                    {searchTerm && <span className="text-violet-400">{displayResults.length}</span>}
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {displayResults.length > 0 ? displayResults.map((item) => (
                      <button
                        key={item.symbol}
                        onClick={() => {
                          setSelectedTicker(item.symbol);
                          setShowTickerMenu(false);
                          setSearchTerm("");
                        }}
                        className={`w-full px-4 py-2.5 text-left text-sm transition-colors flex justify-between items-center group ${symbol === item.symbol
                          ? 'bg-violet-500/10 text-violet-400'
                          : 'text-foreground/80 hover:bg-muted'
                          }`}
                      >
                        <div className="flex flex-col gap-0.5">
                          <span className="font-bold flex items-center gap-2 text-sm">{item.symbol}</span>
                          {item.name && <span className="text-[10px] text-muted-foreground font-medium truncate max-w-[160px]">{item.name}</span>}
                        </div>
                        {symbol === item.symbol && (
                          <div className="w-1.5 h-1.5 rounded-full bg-violet-400 shadow-[0_0_8px_rgba(167,139,250,0.6)]"></div>
                        )}
                      </button>
                    )) : (
                      <div className="px-4 py-6 text-center text-muted-foreground text-xs">
                        Không tìm thấy &quot;{searchTerm}&quot;
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col">
              <h2 className="text-lg font-semibold text-foreground leading-tight">Mã Cổ phiếu {symbol}</h2>
              <p className="text-[10px] text-muted-foreground font-bold tracking-widest uppercase">LỊCH SỬ GIAO DỊCH DATABASE</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Prediction Toggle Button */}
            <button
              onClick={() => setShowPrediction(!showPrediction)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all flex items-center gap-1.5 ${showPrediction
                ? 'border-amber-500/40 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20'
                : 'border-border bg-muted/50 text-muted-foreground hover:text-amber-400 hover:border-border/80'
                }`}
              title="Hiện/Ẩn dự báo Prophet"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                <path fillRule="evenodd" d="M12.577 4.878a.75.75 0 01.919-.53l4.78 1.281a.75.75 0 01.531.919l-1.281 4.78a.75.75 0 01-1.449-.387l.81-3.022a19.407 19.407 0 00-5.594 5.203.75.75 0 01-1.139.093L7 10.06l-4.72 4.72a.75.75 0 01-1.06-1.06l5.25-5.25a.75.75 0 011.06 0l3.074 3.073a20.923 20.923 0 015.545-4.931l-3.042.815a.75.75 0 01-.53-.919z" clipRule="evenodd" />
              </svg>
              {predLoading ? 'Đang tải...' : 'Dự báo'}
            </button>
            <div className="flex bg-muted/50 rounded-lg p-0.5 border border-border">
              {['1D', '1W', '1M', '1Y'].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${timeframe === tf
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'text-muted-foreground hover:text-foreground'
                    }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm border-t border-border/50 pt-4">
          <div className="flex flex-col gap-1">
            <span className="text-muted-foreground text-[10px] uppercase tracking-wider font-bold">Giá hiện tại</span>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${diff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {(latestPrice).toLocaleString('vi-VN')}
              </span>
              <span className="text-muted-foreground text-xs font-medium">₫</span>
            </div>
            <div className={`flex items-center gap-1 text-xs font-bold ${diff >= 0 ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>
              <span className="flex items-center justify-center w-4 h-4 rounded-full bg-current/10">
                {diff >= 0 ? '▲' : '▼'}
              </span>
              <span>{Math.abs(pct).toFixed(2)}%</span>
              <span className="text-[10px] opacity-60 ml-0.5">({diff >= 0 ? '+' : ''}{diff.toLocaleString('vi-VN')} ₫)</span>
            </div>
          </div>
          <div className="hidden sm:block"></div>
          {/* Prediction summary in row */}
          {showPrediction && predSummary ? (
            <div className="flex flex-col gap-1 col-span-2 sm:col-span-2 border-l border-border/50 pl-4">
              <span className="text-amber-400/90 flex items-center gap-1.5 text-[10px] uppercase font-bold tracking-wider">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shadow-[0_0_8px_rgba(251,191,36,0.5)]"></div>
                Dự báo AI (10 phiên)
              </span>
              <div className="flex items-baseline gap-2">
                <span className={`text-2xl font-bold ${predTrend === 'UP' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {predSummary.lastPred.predicted_close.toLocaleString('vi-VN')}
                </span>
                <span className="text-muted-foreground text-xs font-medium">₫</span>
              </div>
              <div className={`flex items-center gap-2 text-xs font-bold ${predChange >= 0 ? 'text-emerald-400/80' : 'text-rose-400/80'}`}>
                <span>{predChange >= 0 ? 'Tăng' : 'Giảm'} {Math.abs(predChange).toFixed(2)}%</span>
                {predSummary.mape != null && (
                  <span className="px-1.5 py-0.5 rounded bg-muted text-[9px] text-muted-foreground uppercase tracking-tighter">
                    Độ tin cậy: {Math.max(0, 100 - predSummary.mape).toFixed(1)}%
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="col-span-2"></div>
          )}
        </div>
      </div>

      <div className="p-2 flex-1 flex flex-col relative bg-transparent">
        {loading ? (
          <div className="flex flex-col items-center justify-center flex-1 p-8 space-y-4">
            <div className="w-full h-full bg-muted/30 rounded-xl animate-pulse flex items-center justify-center">
              <div className="flex flex-col items-center gap-3 text-muted-foreground">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
                <span className="text-xs font-medium">Đang tải dữ liệu biểu đồ...</span>
              </div>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center flex-1 text-rose-500 text-sm">{error}</div>
        ) : data.length === 0 ? (
          <div className="flex items-center justify-center flex-1 text-muted-foreground text-sm">Chưa có dữ liệu giao dịch.</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={diff >= 0 ? "#10b981" : "#f43f5e"} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={diff >= 0 ? "#10b981" : "#f43f5e"} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorPrediction" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.08} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickMargin={12} axisLine={false} tickLine={false} minTickGap={50} interval="preserveStartEnd" />
              <YAxis
                stroke="#94a3b8"
                fontSize={12}
                tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value.toString()}
                domain={['auto', 'auto']}
                axisLine={false}
                tickLine={false}
                width={50}
              />

              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={true} opacity={0.3} />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#94a3b8', strokeWidth: 1.5, strokeDasharray: '4 4' }} />

              {/* Historical price area */}
              <Area
                type="monotone"
                dataKey="price"
                stroke={diff >= 0 ? "#10b981" : "#f43f5e"}
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorPrice)"
                connectNulls={false}
                dot={false}
              />

              {/* Confidence band (upper/lower) */}
              {showPrediction && prediction && (
                <>
                  <Area
                    type="monotone"
                    dataKey="upperBound"
                    stroke="none"
                    fillOpacity={1}
                    fill="url(#colorConfidence)"
                    connectNulls={false}
                    dot={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="lowerBound"
                    stroke="#f59e0b"
                    strokeWidth={0.5}
                    strokeDasharray="2 4"
                    strokeOpacity={0.3}
                    fillOpacity={0}
                    fill="transparent"
                    connectNulls={false}
                    dot={false}
                  />
                </>
              )}

              {/* Prediction line */}
              {showPrediction && prediction && (
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="#f59e0b"
                  strokeWidth={2.5}
                  strokeDasharray="6 3"
                  dot={{ r: 3, fill: '#f59e0b', stroke: '#1e293b', strokeWidth: 2 }}
                  activeDot={{ r: 5, fill: '#f59e0b', stroke: '#fff', strokeWidth: 2 }}
                  connectNulls={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="border-t border-border/60 bg-card/50 px-4 py-2 flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex gap-4">
          <span>Timeframe: {timeframe}</span>
          <span>Datapoints: {data.length}</span>
          {showPrediction && prediction && (
            <span className="text-amber-400/70 flex items-center gap-1">
              <span className="w-3 h-0 border-t-2 border-dashed border-amber-400 inline-block"></span>
              Prophet Forecast: {prediction.predictions.length} phiên
            </span>
          )}
        </div>
        <div className="flex gap-3">
          {prediction?.metrics?.mape != null && showPrediction && (
            <span className="text-amber-400/60" title="Mean Absolute Percentage Error">
              MAPE: {prediction.metrics.mape}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
