'use client';

import { useState } from 'react';
import {
  Sparkles,
  Send,
  Instagram,
  Phone,
  Bot,
  User,
  ShoppingBag,
  Truck,
  CheckCircle2,
  RefreshCw,
  ArrowRight,
  Flame,
  CreditCard
} from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { SimulatorMessageResponse } from '@/types';
import { formatCurrency } from '@/lib/utils';

interface ChatEntry {
  sender: 'CUSTOMER' | 'AI';
  text: string;
  media_url?: string;
  tool_calls?: string[];
  recommended_products?: any[];
  timestamp: string;
}

export default function SimulatorPage() {
  const [channel, setChannel] = useState<'INSTAGRAM' | 'WHATSAPP'>('INSTAGRAM');
  const [customerName, setCustomerName] = useState('Deepika Rao');
  const [customerPhone, setCustomerPhone] = useState('+919988776655');
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatEntry[]>([
    {
      sender: 'AI',
      text: 'నమస్తే! Rani Fashions AI Sales Assistant కి స్వాగతం 😊 మా దగ్గర Kanjeevaram, Banarasi, Handloom Sarees సిద్ధంగా ఉన్నాయి. మీకు ఏ శారీ కావాలి?',
      timestamp: 'Just now',
    },
  ]);

  const [lastTools, setLastTools] = useState<string[]>([]);

  const handleSend = async (messageToSend?: string) => {
    const text = messageToSend || inputText;
    if (!text.trim() || loading) return;

    const userEntry: ChatEntry = {
      sender: 'CUSTOMER',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatHistory((prev) => [...prev, userEntry]);
    if (!messageToSend) setInputText('');
    setLoading(true);

    try {
      const res = await apiRequest<SimulatorMessageResponse>('/api/v1/simulator/message', {
        method: 'POST',
        body: JSON.stringify({
          channel,
          customer_name: customerName,
          customer_phone: customerPhone,
          message: text,
        }),
      });

      const aiEntry: ChatEntry = {
        sender: 'AI',
        text: res.ai_response.content,
        media_url: res.ai_response.media_url,
        tool_calls: res.tool_calls_executed,
        recommended_products: res.recommended_products,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setLastTools(res.tool_calls_executed);
      setChatHistory((prev) => [...prev, aiEntry]);
    } catch (err: any) {
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'AI',
          text: `Error connecting to backend: ${err.message}`,
          timestamp: 'Just now',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickScenarios = [
    {
      label: 'Step 1: Telugu Enquiry',
      text: 'Anna red saree undha? Under 1500 kavali.',
      desc: 'Searches products & replies with Crimson Kanjeevaram saree image',
    },
    {
      label: 'Step 2: Delivery Check',
      text: 'Delivery Miyapur?',
      desc: 'Calculates ₹50 delivery fee for Miyapur zone',
    },
    {
      label: 'Step 3: Book Order',
      text: 'Okay book chesthara. Flat 304, Sri Sai Residency, Miyapur, Hyderabad',
      desc: 'Creates verified order in database & decrements inventory',
    },
    {
      label: 'Human Escalation',
      text: 'I want to talk to human manager please',
      desc: 'Automatically triggers human handoff',
    },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Simulator Intro Header */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-950 border border-emerald-800/40 rounded-3xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Interactive Multi-Channel Dev Simulator</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight">Test Conversational Sales Funnel</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Simulate real customer DMs via Instagram or WhatsApp. Experience natural Telugu language understanding, product image cards, delivery calculation, and instant order creation.
          </p>
        </div>

        {/* Channel Selection Chips */}
        <div className="bg-slate-900/90 border border-slate-700/80 p-1.5 rounded-2xl flex items-center gap-1 shrink-0">
          <button
            onClick={() => setChannel('INSTAGRAM')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              channel === 'INSTAGRAM'
                ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Instagram className="w-4 h-4" />
            <span>Instagram DM</span>
          </button>
          <button
            onClick={() => setChannel('WHATSAPP')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              channel === 'WHATSAPP'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Phone className="w-4 h-4" />
            <span>WhatsApp Cloud</span>
          </button>
        </div>
      </div>

      {/* 2-Column Interface: Left = Quick Scenarios & Tool Traces, Right = Live Chat Device */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left Column: Quick Scenarios & Backend Telemetry */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-400">1-Click Test Scenarios</h3>
            <div className="space-y-2">
              {quickScenarios.map((sc, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(sc.text)}
                  disabled={loading}
                  className="w-full text-left p-3 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/40 transition-all group"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-800 group-hover:text-indigo-600">{sc.label}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 transition-transform group-hover:translate-x-0.5" />
                  </div>
                  <p className="text-xs font-mono text-indigo-700 font-medium mt-1">"{sc.text}"</p>
                  <p className="text-[11px] text-slate-400 mt-1">{sc.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Customer Metadata Inputs */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-400">Simulated Customer</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-semibold text-slate-500 uppercase">Customer Name</label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full mt-1 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium"
                />
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 uppercase">Customer Phone</label>
                <input
                  type="text"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                  className="w-full mt-1 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium font-mono"
                />
              </div>
            </div>
          </div>

          {/* Backend Tool Calling Telemetry */}
          <div className="bg-slate-900 text-slate-200 rounded-2xl p-5 shadow-xs space-y-2 border border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <Bot className="w-4 h-4" /> Backend Tool Execution
              </span>
              <span className="text-[10px] text-slate-400 font-mono">PostgreSQL Backed</span>
            </div>
            {lastTools.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {lastTools.map((t, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-800"
                  >
                    ✓ {t}()
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 pt-1">Send a message to view live tool calls</p>
            )}
          </div>
        </div>

        {/* Right Column: Live Mobile / DM Chat Interface */}
        <div className="lg:col-span-7">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden flex flex-col h-[640px]">
            {/* Chat Device Header */}
            <div
              className={`p-4 text-white flex items-center justify-between shrink-0 shadow-sm ${
                channel === 'INSTAGRAM'
                  ? 'bg-gradient-to-r from-purple-700 via-pink-600 to-rose-500'
                  : 'bg-emerald-700'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center font-bold text-sm shadow-inner">
                  RF
                </div>
                <div>
                  <h4 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                    <span>Rani Fashions Official</span>
                    <CheckCircle2 className="w-4 h-4 text-white" />
                  </h4>
                  <p className="text-[11px] text-white/80">
                    {channel === 'INSTAGRAM' ? 'Instagram Direct' : 'WhatsApp Business Verified'} • AI Assistant
                  </p>
                </div>
              </div>

              <span className="text-[10px] bg-black/20 text-white font-semibold px-2 py-0.5 rounded-full backdrop-blur-xs">
                Active Now
              </span>
            </div>

            {/* Chat History Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
              {chatHistory.map((item, idx) => {
                const isCust = item.sender === 'CUSTOMER';
                return (
                  <div
                    key={idx}
                    className={`flex flex-col ${isCust ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl p-3.5 text-xs sm:text-sm whitespace-pre-line shadow-xs ${
                        isCust
                          ? channel === 'INSTAGRAM'
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-tr-xs'
                            : 'bg-emerald-600 text-white rounded-tr-xs'
                          : 'bg-white border border-slate-200 text-slate-900 rounded-tl-xs'
                      }`}
                    >
                      {/* Product Image Attachment */}
                      {item.media_url && (
                        <div className="mb-2.5 rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={item.media_url}
                            alt="Product"
                            className="w-full h-52 object-cover"
                          />
                        </div>
                      )}

                      <p>{item.text}</p>
                    </div>

                    <span className="text-[10px] text-slate-400 mt-1 px-1">{item.timestamp}</span>
                  </div>
                );
              })}

              {loading && (
                <div className="flex items-center gap-2 text-xs text-slate-500 italic p-2 bg-white rounded-xl border border-slate-200 max-w-xs shadow-xs">
                  <Bot className="w-4 h-4 text-indigo-600 animate-spin" />
                  <span>AI Agent is searching catalogue & verifying delivery...</span>
                </div>
              )}
            </div>

            {/* Input Bar */}
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-3 bg-white border-t border-slate-200 flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type customer message in Telugu, Hindi or English..."
                className="flex-1 px-4 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={loading || !inputText.trim()}
                className={`px-5 py-2.5 rounded-xl text-xs font-bold text-white flex items-center gap-1.5 transition-all shadow-sm ${
                  channel === 'INSTAGRAM'
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90'
                    : 'bg-emerald-600 hover:bg-emerald-500'
                } disabled:opacity-40`}
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
