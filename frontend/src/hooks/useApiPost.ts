'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { queryKeys } from '@/services/queryKeys';
import { toast } from 'sonner';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export function useApiPost<TRequest, TResponse>(
  url: string,
  invalidateKeys?: (readonly any[])[],
  method: 'post' | 'put' | 'patch' | 'delete' = 'post'
) {
  const queryClient = useQueryClient();

  return useMutation<TResponse, Error, TRequest>({
    mutationFn: async (data: TRequest) => {
      const response = await (method === 'delete' ? api.delete(url, { data }) : (api as any)[method](url, data));
      return response.data;
    },
    onSuccess: () => {
      if (invalidateKeys) {
        invalidateKeys.forEach(key => {
          queryClient.invalidateQueries({ queryKey: key });
        });
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || error.message || 'Thao tác thất bại';
      toast.error(message);
    }
  });
}
