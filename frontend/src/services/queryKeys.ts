import { Article, ArticleListParams, ChatMessage, User } from '@/interfaces/index';

export const queryKeys = {
  stocks: {
    all: ['stocks'] as const,
    list: () => [...queryKeys.stocks.all, 'list'] as const,
    history: (symbol: string) => [...queryKeys.stocks.all, 'history', symbol] as const,
    prediction: (symbol: string) => [...queryKeys.stocks.all, 'prediction', symbol] as const,
  },
  chat: {
    all: ['chat'] as const,
    sessions: () => [...queryKeys.chat.all, 'sessions'] as const,
    history: (sessionId: string) => [...queryKeys.chat.all, 'history', sessionId] as const,
  },
  auth: {
    me: ['auth', 'me'] as const,
  }
};
