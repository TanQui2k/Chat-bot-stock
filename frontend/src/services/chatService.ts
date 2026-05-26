import { API_BASE_URL } from '@/lib/apiConfig';

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

const CHAT_API_BASE_URL = `${API_BASE_URL}/chat`;

async function readError(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json() as { detail?: string };
    return body.detail || fallback;
  } catch {
    return fallback;
  }
}

export const chatService = {
  async initSession(userId: string): Promise<string> {
    const res = await fetch(`${CHAT_API_BASE_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        user_id: userId,
        title: 'Assistant Chat',
      }),
    });

    if (!res.ok) {
      throw new Error(await readError(res, 'Không thể tạo phiên chat.'));
    }

    const data = await res.json() as { id?: string };
    if (!data.id) {
      throw new Error('Backend không trả về mã phiên chat.');
    }

    return data.id;
  },

  async sendMessage(sessionId: string, content: string): Promise<Message> {
    const res = await fetch(`${CHAT_API_BASE_URL}/sessions/${sessionId}/turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ content }),
    });

    if (!res.ok) {
      throw new Error(await readError(res, 'Gửi tin nhắn thất bại.'));
    }

    const turnResponse = await res.json();
    return {
      id: turnResponse.assistant_message.id.toString(),
      role: 'assistant',
      content: turnResponse.assistant_message.content,
    };
  },
};
