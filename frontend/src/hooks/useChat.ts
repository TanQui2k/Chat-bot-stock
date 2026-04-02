'use client';

import { useApiGet } from '@/hooks/useApiGet';
import { useApiPost } from '@/hooks/useApiPost';
import { queryKeys } from '@/services/queryKeys';
import { ChatMessage, ChatSession, ApiResponse } from '@/interfaces';

/**
 * Hook to initialize a chat session
 */
export function useCreateChatSession() {
  return useApiPost<{ user_id: string; title: string }, ChatSession>(
    '/api/chat/sessions',
    [queryKeys.chat.sessions()],
    'post'
  );
}

/**
 * Hook to send a chat message
 */
export function useSendChatMessage(sessionId: string) {
  return useApiPost<{ content: string }, ApiResponse<{ assistant_message: ChatMessage }>>(
    `/api/chat/sessions/${sessionId}/turn`,
    [queryKeys.chat.history(sessionId)],
    'post'
  );
}

/**
 * Hook to fetch chat history for a session
 */
export function useChatHistory(sessionId: string) {
  return useApiGet<ChatMessage[]>(
    `/api/chat/sessions/${sessionId}/history`,
    queryKeys.chat.history(sessionId),
    { enabled: !!sessionId, staleTime: 0 } // Chat history should not be cached long
  );
}
