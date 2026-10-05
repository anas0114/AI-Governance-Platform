import ChatWindow from "@/components/chat/ChatWindow";

export default function ChatPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">AI Copilot</h1>
      <p className="mt-2 text-slate-600">Ask questions grounded in your policies and regulations.</p>
      <div className="mt-6">
        <ChatWindow />
      </div>
    </div>
  );
}
