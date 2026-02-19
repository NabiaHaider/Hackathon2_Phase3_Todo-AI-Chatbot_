// frontend/lib/chat-store.ts
import { create } from 'zustand';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  isError?: boolean;
}

interface ChatState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  toggleChat: () => void;
  addMessage: (message: Omit<Message, 'id'>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  isOpen: false,
  messages: [],
  isLoading: false,
  error: null,
  toggleChat: () => set((state) => ({ isOpen: !state.isOpen })),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, { ...message, id: Date.now().toString() }],
  })),
  setLoading: (loading) => set(() => ({ isLoading: loading })),
  setError: (error) => set(() => ({ error: error })),
  clearChat: () => set(() => ({ messages: [], error: null })),
}));
