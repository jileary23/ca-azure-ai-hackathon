import { useState, useCallback } from 'react';
import { postChat } from '../api/apiClient';
import type { ChatMessage } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    setMessages(prev => [...prev, { role: 'user', content }]);
    setIsLoading(true);
    setError(null);
    try {
      const data = await postChat(content);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        eligibility: data.eligibility,
        citations: data.citations,
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I could not process your request.',
      }]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, isLoading, error, sendMessage };
}
