'use client';

import { useEffect, useState } from 'react';
import {
  Search,
  Instagram,
  Phone,
  Bot,
  User,
  Send,
  Sparkles,
  ShieldAlert,
  UserCheck,
  CheckCircle2,
  Clock,
  MapPin,
  Flame,
  ShoppingBag
} from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Conversation, Message, Customer } from '@/types';
import { formatDate, formatCurrency } from '@/lib/utils';

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [channelFilter, setChannelFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  // Load conversations
  const loadConversations = async () => {
    try {
      const convs = await apiRequest<Conversation[]>('/api/v1/conversations');
      setConversations(convs);
      if (convs.length > 0 && !selectedId) {
        setSelectedId(convs[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Load messages for selected conversation
  const loadMessages = async (convId: string) => {
    try {
      const msgs = await apiRequest<Message[]>(`/api/v1/conversations/${convId}/messages`);
      setMessages(msgs);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (selectedId) {
      loadMessages(selectedId);
    }
  }, [selectedId]);

  const selectedConv = conversations.find((c) => c.id === selectedId);

  // Handle human takeover / handoff
  const toggleHandoff = async () => {
    if (!selectedConv) return;
    const targetState = !selectedConv.is_ai_handled;
    try {
      const updated = await apiRequest<Conversation>(`/api/v1/conversations/${selectedConv.id}/handoff`, {
        method: 'POST',
        body: JSON.stringify({
          is_ai_handled: targetState,
          reason: targetState ? 'Staff enabled AI' : 'Manual staff takeover from dashboard',
        }),
      });
      setConversations((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    } catch (err) {
      console.error(err);
    }
  };

  // Send manual staff message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId || !newMessage.trim()) return;

    setSending(true);
    try {
      const msg = await apiRequest<Message>(`/api/v1/conversations/${selectedId}/messages`, {
        method: 'POST',
        body: JSON.stringify({
          content: newMessage,
          sender_type: 'AGENT',
        }),
      });
      setMessages((prev) => [...prev, msg]);
      setNewMessage('');
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  // Filter conversations
  const filteredConvs = conversations.filter((c) => {
    const matchesChannel = channelFilter === 'ALL' || c.channel === channelFilter;
    const matchesSearch =
      (c.customer_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.customer_phone || '').includes(searchQuery);
    return matchesChannel && matchesSearch;
  });

  return (
    <div className="h-[calc(100vh-7rem)] flex rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      {/* ------------------------------------------------------------- */}
      {/* COLUMN 1: Conversation List */}
      {/* ------------------------------------------------------------- */}
      <div className="w-80 border-r border-slate-200 flex flex-col shrink-0 bg-slate-50/50">
        <div className="p-4 border-b border-slate-200 space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-600">
            {['ALL', 'INSTAGRAM', 'WHATSAPP'].map((ch) => (
              <button
                key={ch}
                onClick={() => setChannelFilter(ch)}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  channelFilter === ch ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-200/70 hover:bg-slate-200 text-slate-700'
                }`}
              >
                {ch === 'ALL' ? 'All' : ch === 'INSTAGRAM' ? 'Instagram' : 'WhatsApp'}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation Items */}
        <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
          {filteredConvs.map((conv) => {
            const isSelected = conv.id === selectedId;
            return (
              <button
                key={conv.id}
                onClick={() => setSelectedId(conv.id)}
                className={`w-full p-3.5 text-left transition-colors flex items-start gap-3 ${
                  isSelected ? 'bg-indigo-50/80 border-l-4 border-indigo-600' : 'hover:bg-slate-100/60'
                }`}
              >
                <div className="relative">
                  <div className="w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-xs">
                    {conv.customer_name ? conv.customer_name.slice(0, 2).toUpperCase() : 'CU'}
                  </div>
                  <div className="absolute -bottom-1 -right-1 p-0.5 bg-white rounded-full shadow-xs">
                    {conv.channel === 'INSTAGRAM' ? (
                      <Instagram className="w-3.5 h-3.5 text-pink-600" />
                    ) : (
                      <Phone className="w-3.5 h-3.5 text-emerald-600" />
                    )}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="font-bold text-xs text-slate-900 truncate">{conv.customer_name || 'Customer'}</p>
                    <span className="text-[10px] text-slate-400">{formatDate(conv.last_message_at)}</span>
                  </div>

                  <p className="text-[11px] text-slate-500 truncate mt-0.5">
                    {conv.latest_message ? conv.latest_message.content : 'No messages yet'}
                  </p>

                  <div className="flex items-center gap-1.5 mt-1.5">
                    {conv.is_ai_handled ? (
                      <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200/60 px-1.5 py-0.2 rounded flex items-center gap-1">
                        <Bot className="w-2.5 h-2.5" />
                        <span>AI Handling</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.2 rounded flex items-center gap-1">
                        <UserCheck className="w-2.5 h-2.5" />
                        <span>Human Staff</span>
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* COLUMN 2: Chat Feed & Realtime Messaging */}
      {/* ------------------------------------------------------------- */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50/20">
        {/* Chat Header */}
        {selectedConv ? (
          <div className="h-16 px-6 border-b border-slate-200 flex items-center justify-between bg-white shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center font-bold text-xs text-slate-800">
                {selectedConv.customer_name?.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                  <span>{selectedConv.customer_name}</span>
                  <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {selectedConv.channel}
                  </span>
                </h3>
                <p className="text-xs text-slate-400">{selectedConv.customer_phone || 'Direct Message'}</p>
              </div>
            </div>

            {/* Handoff Toggle Button */}
            <button
              onClick={toggleHandoff}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-xs ${
                selectedConv.is_ai_handled
                  ? 'bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
              }`}
            >
              {selectedConv.is_ai_handled ? (
                <>
                  <UserCheck className="w-3.5 h-3.5 text-amber-600" />
                  <span>Take Over from AI</span>
                </>
              ) : (
                <>
                  <Bot className="w-3.5 h-3.5 text-white" />
                  <span>Resume AI Automation</span>
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="h-16 px-6 border-b border-slate-200 flex items-center text-sm text-slate-400">
            Select a conversation
          </div>
        )}

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg) => {
            const isCustomer = msg.sender_type === 'CUSTOMER';
            const isAI = msg.sender_type === 'AI';

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isCustomer ? 'items-start' : 'items-end'}`}
              >
                <div className="flex items-center gap-1 text-[10px] text-slate-400 mb-1 px-1">
                  {isAI ? (
                    <span className="font-semibold text-indigo-600 flex items-center gap-1">
                      <Bot className="w-3 h-3" /> ReachOut AI
                    </span>
                  ) : isCustomer ? (
                    <span className="font-medium text-slate-600">Customer</span>
                  ) : (
                    <span className="font-medium text-amber-600">Staff Agent</span>
                  )}
                  <span>• {formatDate(msg.created_at)}</span>
                </div>

                <div
                  className={`max-w-md p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-line shadow-xs ${
                    isCustomer
                      ? 'bg-white border border-slate-200 text-slate-900 rounded-tl-sm'
                      : isAI
                      ? 'bg-indigo-600 text-white rounded-tr-sm'
                      : 'bg-amber-600 text-white rounded-tr-sm'
                  }`}
                >
                  {/* Media attachment if any */}
                  {msg.media_url && (
                    <div className="mb-2.5 rounded-lg overflow-hidden border border-white/20">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={msg.media_url}
                        alt="Product attachment"
                        className="w-full h-48 object-cover"
                      />
                    </div>
                  )}
                  <p>{msg.content}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Reply Box */}
        {selectedConv && (
          <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-slate-200 flex gap-2">
            <input
              type="text"
              placeholder={
                selectedConv.is_ai_handled
                  ? 'AI is currently active. Type to send a manual override reply...'
                  : 'Type message to send to customer...'
              }
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={sending || !newMessage.trim()}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        )}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* COLUMN 3: Customer Context & Lead Scoring */}
      {/* ------------------------------------------------------------- */}
      {selectedConv && (
        <div className="w-80 border-l border-slate-200 bg-slate-50/40 p-5 flex flex-col shrink-0 overflow-y-auto space-y-6">
          <div>
            <span className="text-[10px] uppercase font-extrabold tracking-wider text-slate-400">Customer CRM Profile</span>
            <h4 className="font-extrabold text-base text-slate-900 mt-1">{selectedConv.customer_name}</h4>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{selectedConv.customer_phone || 'No phone'}</p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="p-3 bg-white rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase">Channel</span>
              <p className="text-xs font-bold text-slate-900 mt-0.5">{selectedConv.channel}</p>
            </div>
            <div className="p-3 bg-white rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase">Language</span>
              <p className="text-xs font-bold text-indigo-600 mt-0.5">Telugu / EN</p>
            </div>
          </div>

          {/* AI Lead Status Card */}
          <div className="p-4 bg-white rounded-xl border border-slate-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1">
                <Flame className="w-3.5 h-3.5 text-rose-500" />
                <span>AI Lead Score</span>
              </span>
              <span className="text-xs font-extrabold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                HOT (85/100)
              </span>
            </div>
            <p className="text-[11px] text-slate-500 leading-tight">
              Customer inquired about red sarees under ₹1,500 and delivery to Miyapur. High purchase intent detected.
            </p>
          </div>

          {/* Delivery & Address */}
          <div className="p-4 bg-white rounded-xl border border-slate-200 space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
              <MapPin className="w-3.5 h-3.5 text-indigo-600" />
              <span>Delivery Zone</span>
            </div>
            <p className="text-xs text-slate-600">Miyapur, Hyderabad</p>
            <p className="text-[11px] text-emerald-600 font-semibold">Standard Delivery: ₹50</p>
          </div>

          {/* Automation Safety */}
          <div className="p-3.5 rounded-xl bg-slate-100 text-[11px] text-slate-600 space-y-1">
            <p className="font-semibold text-slate-800 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Zero-Hallucination Mode</span>
            </p>
            <p>Prices, stock levels, and order IDs are verified directly against the PostgreSQL database.</p>
          </div>
        </div>
      )}
    </div>
  );
}
