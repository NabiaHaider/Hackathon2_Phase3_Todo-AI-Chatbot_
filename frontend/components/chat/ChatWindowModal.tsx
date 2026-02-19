"use client";

// frontend/components/chat/ChatWindowModal.tsx

import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '@/lib/chat-store';
import { sendChatMessage } from '@/lib/api';
import Message from './Message';
import TypingIndicator from './TypingIndicator';
import ErrorDisplay from './ErrorDisplay';
import { useAuthStore } from '@/lib/state/auth-store';

interface ChatWindowModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatWindowModal: React.FC<ChatWindowModalProps> = ({ isOpen, onClose }) => {
  const { messages, isLoading, error, addMessage, setLoading, setError } = useChatStore();
  const [inputMessage, setInputMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, error]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    const userMessageContent = inputMessage;
    addMessage({ text: userMessageContent, isUser: true });
    setInputMessage('');
    setLoading(true);
    setError(null);

    let assistantResponseBuffer = '';

    const onNewMessage = (data: any) => {
      if (data.type === 'final_response') {
        addMessage({ text: data.message, isUser: false });
        setLoading(false);
      } else if (data.type === 'tool_code') {
        addMessage({
          text: `(Tool: ${data.name} executed. Output: ${JSON.stringify(data.output)})`,
          isUser: false
        });
      } else if (data.type === 'error') {
        setError(data.message);
        setLoading(false);
      } else {
        assistantResponseBuffer += data.message;
      }
    };

    try {
      await sendChatMessage(userMessageContent, onNewMessage, setError);
    } catch (err: any) {
      setError(err.message || "Failed to send message to chatbot.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-16 right-10 z-50 w-[320px] h-[600px]">
      <div className="bg-white rounded-2xl shadow-2xl w-full h-full flex flex-col border border-primary">

        <div className="flex justify-between items-center border-b p-4 bg-primary text-white rounded-t-2xl">
          <h2 className="text-lg font-semibold">AI Chatbot</h2>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 p-4 overflow-y-auto bg-white">
          {messages.map((msg) => (
            <Message key={msg.id} text={msg.text} isUser={msg.isUser} />
          ))}
          {isLoading && <TypingIndicator />}
          {error && <ErrorDisplay message={error} onClose={() => setError(null)} />}
          <div ref={messagesEndRef} />
        </div>

        {/* ✅ ONLY THIS PART UPDATED */}
        <div className="border-t p-4 flex bg-gray-50">
          <input
            type="text"
            className="flex-1 bg-white border border-primary rounded-l-lg p-2 
                       focus:outline-none focus:ring-2 focus:ring-primary 
                       text-black placeholder-gray-400"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isLoading) handleSendMessage();
            }}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            className="bg-primary hover:bg-primary/90 text-white rounded-r-lg px-4 py-2"
            disabled={isLoading}
          >
            Send
          </button>
        </div>

      </div>
    </div>
  );
};

export default ChatWindowModal;
