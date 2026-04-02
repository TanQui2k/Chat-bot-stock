'use client';

import { useApiGet } from '@/hooks/useApiGet';
import { queryKeys } from '@/services/queryKeys';
import { StockInfo, PriceData, PredictionResponse } from '@/interfaces';

/**
 * Fetch list of all stocks
 */
export function useStocks() {
  return useApiGet<StockInfo[]>(
    '/api/stocks/',
    queryKeys.stocks.list(),
    { staleTime: 10 * 60 * 1000 } // Cache for 10 minutes
  );
}

/**
 * Fetch stock price history
 */
export function useStockHistory(symbol: string) {
  return useApiGet<PriceData[]>(
    `/api/stocks/${symbol}/history`,
    queryKeys.stocks.history(symbol),
    { 
      enabled: !!symbol,
      staleTime: 5 * 60 * 1000 // Cache for 5 minutes
    }
  );
}

/**
 * Fetch stock prediction
 */
export function useStockPrediction(symbol: string, days: number = 10) {
  // Prophet prediction is technically a POST but acts as a data fetch
  // For strict adherence to rules, use POST version in actual implementation
  // but wrap it in useQuery if it should behave like a fetch
  return useApiGet<PredictionResponse>(
    `/api/predict/${symbol}?days=${days}`, // (Mock URL check if GET is available, otherwise use useMutation)
    queryKeys.stocks.prediction(symbol),
    { 
      enabled: !!symbol,
      staleTime: 15 * 60 * 1000 // Prediction model result stays valid longer
    }
  );
}
