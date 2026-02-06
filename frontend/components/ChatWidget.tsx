"use client";

import { useState, useEffect, useRef } from "react";
import { MessageCircle, X, Send, Minimize2 } from "lucide-react";
import Cookies from "js-cookie";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useTaskRefresh } from "@/contexts/TaskRefreshContext";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated } = useAuth();
  const { refreshTasks } = useTaskRefresh();

  // Reset chat state on logout so messages don't persist across accounts
  useEffect(() => {
    if (!isAuthenticated) {
      setIsOpen(false);
      setMessages([]);
      setConversationId(null);
      setError(null);
    }
  }, [isAuthenticated]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isMinimized]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);

    // Add user message to UI immediately
    const userMsg: Message = {
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const token = Cookies.get("access_token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const data = await api.sendChatMessage(token, {
        message: userMessage,
        conversation_id: conversationId,
      });

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add assistant message
      const assistantMsg: Message = {
        role: "assistant",
        content: data.message,
        created_at: data.created_at,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Detect task-related operations and trigger refresh
      // The agent confirms actions with specific phrases
      const taskActionKeywords = [
        "added", "created", "completed", "marked", "done",
        "deleted", "removed", "updated", "changed", "modified"
      ];
      const responseText = data.message.toLowerCase();
      const hasTaskAction = taskActionKeywords.some(keyword =>
        responseText.includes(keyword)
      );

      if (hasTaskAction) {
        // Trigger task list refresh after a short delay to ensure backend has processed
        setTimeout(() => {
          refreshTasks();
        }, 300);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove the optimistically added user message on error
      setMessages((prev) => prev.slice(0, -1));
      setInput(userMessage); // Restore the input
    } finally {
      setIsLoading(false);
    }
  };

  // Don't render widget until client-side auth check completes
  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 h-14 w-14 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full shadow-2xl hover:shadow-purple-500/50 hover:scale-110 transition-all flex items-center justify-center group z-50"
          >
            <MessageCircle className="h-6 w-6 text-white group-hover:scale-110 transition-transform" />
            {messages.length > 0 && !isMinimized && (
              <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full border-2 border-white text-xs font-bold text-white flex items-center justify-center">
                {messages.length}
              </span>
            )}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Widget */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Mobile Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
              onClick={() => setIsOpen(false)}
            />

            {/* Widget Container */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className={`fixed z-50 bg-white shadow-2xl border border-gray-200 overflow-hidden ${
                isMinimized
                  ? "bottom-6 right-6 w-80 md:w-96 h-16 rounded-2xl"
                  : "inset-x-0 bottom-0 top-0 md:inset-auto md:bottom-6 md:right-6 md:w-96 md:h-[600px] md:rounded-2xl md:top-auto"
              } transition-all`}
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 bg-white/20 backdrop-blur rounded-full flex items-center justify-center">
                    <MessageCircle className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Task Assistant</h3>
                    <p className="text-xs text-blue-100">Always here to help</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    className="hidden md:block p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                  >
                    <Minimize2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              {!isMinimized && (
                <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(600px-8rem)]">
                  <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <MessageCircle className="h-8 w-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 text-sm">
                      Hi! I'm your task assistant. Ask me to add, view, update, or complete your tasks!
                    </p>
                  </div>
                ) : (
                  <>
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${
                          message.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        <div
                          className={`max-w-[85%] px-4 py-3 rounded-2xl ${
                            message.role === "user"
                              ? "bg-blue-600 text-white"
                              : "bg-gray-100 text-gray-900"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap break-words">
                            {message.content}
                          </p>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                          <div className="flex space-x-1">
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="px-4 py-2 bg-red-50 border-t border-red-100 flex items-center justify-between">
                  <p className="text-xs text-red-600">{error}</p>
                  <button
                    onClick={() => setError(null)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}

              {/* Input */}
              <form
                onSubmit={sendMessage}
                className="px-4 py-3 bg-gray-50 border-t border-gray-200"
              >
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me anything about your tasks..."
                    disabled={isLoading}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isLoading ? (
                      <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
