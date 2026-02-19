// frontend/lib/state/auth-store.ts
import { create } from 'zustand';

interface AuthState {
  token: string | null;
  user: { username: string; id: string } | null; // Adjust user type as per your backend's user schema
  setToken: (token: string | null) => void;
  setUser: (user: { username: string; id: string } | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('authToken') : null,
  user: typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('authUser') || 'null') : null,

  setToken: (token) => {
    set({ token });
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  },
  setUser: (user) => {
    set({ user });
    if (user) {
      localStorage.setItem('authUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('authUser');
    }
  },
  logout: () => {
    set({ token: null, user: null });
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
  },
}));
