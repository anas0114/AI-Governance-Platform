"use client";

import { useState } from "react";
import { getErrorMessage, sendChatMessage } from "@/lib/api";
import type { ChatMessage, ChatSource } from "@/types/chat";

interface DisplayMessage extends ChatMessage {
  sources?: ChatSource[];
  isError?: boolean;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMessage: DisplayMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    try {
      const response = await sendChatMessage(userMessage.content);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer, sources: response.sources }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: getErrorMessage(err, "The copilot request failed."), isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[500px] flex-col rounded-lg border border-slate-200 bg-white">
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((message, i) => (
          <div
            key={i}
            className={
              message.role === "user"
                ? "ml-auto max-w-md rounded-lg bg-brand-600 px-4 py-2 text-sm text-white"
                : message.isError
                  ? "max-w-md rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700"
                  : "max-w-md rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-900"
            }
          >
            <p>{message.content}</p>
            {message.sources && message.sources.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1 border-t border-slate-200 pt-2">
                {message.sources.map((source) => (
                  <span
                    key={source.citation}
                    title={source.snippet}
                    className="rounded-full bg-white px-2 py-0.5 text-xs text-slate-500 shadow-sm"
                  >
                    [{source.citation}] {source.filename ?? source.clause_number ?? source.document_id}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-sm text-slate-400">Thinking…</div>}
      </div>
      <div className="flex gap-2 border-t border-slate-200 p-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about a policy or regulation..."
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          onClick={handleSend}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
