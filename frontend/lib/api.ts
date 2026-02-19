// frontend/lib/api.ts

import { useAuthStore } from './state/auth-store';

export interface ChatMessageRequest {
  message: string;
}

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/api`
    : 'http://localhost:8000/api';

interface RequestOptions extends RequestInit {
  token?: string;
}

// ================= AUTHENTICATED FETCH =================
export async function fetchAuthenticated(
  url: string,
  options: RequestOptions = {}
): Promise<Response> {
  const { token: requestToken, ...fetchOptions } = options;
  const { token: storedToken } = useAuthStore.getState();

  const token = requestToken || storedToken;

  const headers = new Headers(fetchOptions.headers);

  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  if (response.status === 401) {
    useAuthStore.getState().logout();
  }

  return response;
}

// ================= LOGIN =================
export async function loginUser(credentials: {
  email: string;
  password: string;
}): Promise<{ token: string; user: any }> {

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed. Please check your credentials.');
  }

  const token = data.access_token;

  const user = {
    id: data.user?.id?.toString() || '',
    email: data.user?.email || credentials.email,
    username:
      data.user?.username ||
      data.user?.email?.split('@')[0] ||
      credentials.email.split('@')[0],
  };

  useAuthStore.getState().setToken(token);
  useAuthStore.getState().setUser(user);

  return { token, user };
}

// ================= REGISTER =================
export async function registerUser(credentials: {
  email: string;
  password: string;
  username?: string;
}): Promise<any> {

  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password,
      username: credentials.username, // ✅ FIXED
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Registration failed');
  }

  return data;
}

// ================= LOGOUT =================
export function logoutUser(): void {
  useAuthStore.getState().logout();
}

// ================= CHAT =================
export async function sendChatMessage(
  message: string,
  onNewMessage: (msg: any) => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const { token } = useAuthStore.getState();

    if (!token) {
      onError('You must be logged in to chat.');
      return;
    }

    const response = await fetchAuthenticated(
      `${API_BASE_URL}/v1/chat`,
      {
        method: 'POST',
        body: JSON.stringify({ message } as ChatMessageRequest),
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      onError(errorData.detail || `API error: ${response.statusText}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError('Failed to get readable stream from chat API.');
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.substring(6);
            const data = JSON.parse(jsonStr);
            onNewMessage(data);
          } catch {
            onError('Failed to parse response from server.');
          }
        }
      }
    }

  } catch (error) {
    console.error('Network error:', error);
    onError('Could not connect to the chat service.');
  }
}
