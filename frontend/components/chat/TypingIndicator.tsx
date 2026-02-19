// frontend/components/chat/TypingIndicator.tsx

import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-1 p-2 bg-white rounded-lg max-w-min shadow"> {/* Changed bg to white, added shadow */}
      <div className="dot animate-bounce delay-0 bg-primary"></div> {/* Changed to bg-primary */}
      <div className="dot animate-bounce delay-75 bg-primary"></div> {/* Changed to bg-primary */}
      <div className="dot animate-bounce delay-150 bg-primary"></div> {/* Changed to bg-primary */}
      <style jsx>{`
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-5px); }
        }
        .animate-bounce {
          animation: bounce 1.4s infinite ease-in-out both;
        }
        .delay-0 { animation-delay: -0.32s; }
        .delay-75 { animation-delay: -0.16s; }
        .delay-150 { animation-delay: 0s; }
      `}</style>
    </div>
  );
};

export default TypingIndicator;
