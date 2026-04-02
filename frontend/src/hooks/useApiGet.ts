'use client';

import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export function useApiGet<T>(
  url: string,
  queryKey: readonly any[],
  options?: Partial<UseQueryOptions<T, Error>>
) {
  return useQuery<T, Error>({
    queryKey,
    queryFn: async () => {
      const response = await api.get(url);
      return response.data;
    },
    ...options,
  });
}
