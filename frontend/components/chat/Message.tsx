// frontend/components/chat/Message.tsx

import React from 'react';

interface MessageProps {
  text: string;
  isUser: boolean;
}

const Message: React.FC<MessageProps> = ({ text, isUser }) => {
  return (
    <div
      className={`flex mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`rounded-lg p-3 max-w-[70%] shadow ${
          isUser
            ? 'bg-primary text-white' // Primary color for User
            : 'bg-white text-primary' // White for AI
        }`}
      >
        {text}
      </div>
    </div>
  );
};

export default Message;
