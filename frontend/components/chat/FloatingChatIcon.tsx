// frontend/components/chat/FloatingChatIcon.tsx

import React from 'react';
import Image from 'next/image';

interface FloatingChatIconProps {
  onClick: () => void;
  isOpen: boolean;
}

const FloatingChatIcon: React.FC<FloatingChatIconProps> = ({ onClick, isOpen }) => {
  return (
    <button
      onClick={onClick}
      className={`fixed bottom-10 right-8 bg-primary hover:bg-primary/90 text-white p-3 rounded-full shadow-lg transition-transform transform border-2 border-white z-50 ${
        isOpen ? 'rotate-90' : 'rotate-0'
      }`}
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      <Image
        src="/chatbot.jpg"
        alt="Chatbot Icon"
        width={32}
        height={32}
        className="rounded-full"
      />
    </button>
  );
};

export default FloatingChatIcon;
