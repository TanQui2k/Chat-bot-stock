import { API_BASE_URL } from '@/lib/apiConfig';

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

// Helper to generate a valid UUID v4
export const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

const CHAT_API_BASE_URL = `${API_BASE_URL}/chat`;

export const chatService = {
  async initSession(userId: string): Promise<string | null> {
    try {
      const res = await fetch(`${CHAT_API_BASE_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          title: `Assistant Chat`,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error('Session Init Detail:', errorData);
        throw new Error('Backend rejected session creation');
      }

      const data = await res.json();
      return data.id || null;
    } catch (err) {
      console.error('Failed to init chat session', err);
      return null;
    }
  },

  async sendMessage(sessionId: string, content: string): Promise<Message> {
    const res = await fetch(`${CHAT_API_BASE_URL}/sessions/${sessionId}/turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });

    if (!res.ok) {
      throw new Error('Gửi tin nhắn thất bại.');
    }

    const turnResponse = await res.json();
    return {
      id: turnResponse.assistant_message.id.toString(),
      role: 'assistant',
      content: turnResponse.assistant_message.content,
    };
  },
};
