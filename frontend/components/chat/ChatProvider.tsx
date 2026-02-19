"use client";

import { useEffect } from "react";
import { useChatStore } from "@/lib/chat-store";
import FloatingChatIcon from "@/components/chat/FloatingChatIcon";
import ChatWindowModal from "@/components/chat/ChatWindowModal";

export default function ChatProvider() {
  const { isOpen, toggleChat } = useChatStore();

  return (
    <>
      <FloatingChatIcon onClick={toggleChat} isOpen={isOpen} />
      <ChatWindowModal isOpen={isOpen} onClose={toggleChat} />
    </>
  );
}
