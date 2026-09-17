'use client';

import { useEffect, useState } from 'react';
import { Share2, Instagram, Phone, CheckCircle2, AlertTriangle, ShieldCheck, Copy, RefreshCw } from 'lucide-react';
import { apiRequest } from '@/lib/api';

export default function IntegrationsPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  const loadStatus = async () => {
    try {
      const data = await apiRequest<any>('/api/v1/integrations/status');
      setStatus(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  const connectInstagram = async () => {
    await apiRequest('/api/v1/integrations/instagram/connect', {
      method: 'POST',
      body: JSON.stringify({ username: 'ranifashions_official' }),
    });
    loadStatus();
  };

  const connectWhatsApp = async () => {
    await apiRequest('/api/v1/integrations/whatsapp/connect', {
      method: 'POST',
      body: JSON.stringify({ phone_number: '+919876543210' }),
    });
    loadStatus();
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Channel Integrations</h2>
        <p className="text-xs text-slate-500 mt-1">
          Connect your Instagram Professional account and WhatsApp Cloud API. Webhook ingress endpoints are secured with HMAC SHA-256 verification.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Instagram Integration Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 via-pink-500 to-purple-600 flex items-center justify-center text-white shadow-md">
                  <Instagram className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900">Instagram Messaging API</h3>
                  <p className="text-xs text-slate-400">Meta Graph API v21.0+</p>
                </div>
              </div>

              <span
                className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                  status?.instagram?.connected
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {status?.instagram?.connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Handles direct messages, multilingual replies in Telugu/Hindi/English, and rich media saree image responses.
            </p>

            {status?.instagram?.connected && (
              <div className="p-3 bg-slate-50 rounded-xl space-y-1 text-xs">
                <p className="text-slate-500">Connected Account: <strong className="text-slate-900">@{status.instagram.username}</strong></p>
                <p className="text-slate-500">Permissions: <code className="text-indigo-600 font-mono text-[10px]">instagram_business_manage_messages</code></p>
              </div>
            )}

            {/* Webhook details */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Instagram Callback URL</span>
                <div className="mt-1 flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs font-mono text-slate-700 overflow-x-auto">
                  <span className="flex-1 truncate">{status?.instagram?.webhook_url}</span>
                  <button
                    onClick={() => copyToClipboard(status?.instagram?.webhook_url, 'ig_url')}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
                {copied === 'ig_url' && <span className="text-[10px] text-emerald-600 font-bold">Copied!</span>}
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Verify Token</span>
                <div className="mt-1 flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs font-mono text-slate-700">
                  <span className="flex-1">{status?.instagram?.verify_token}</span>
                  <button
                    onClick={() => copyToClipboard(status?.instagram?.verify_token, 'ig_token')}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
                {copied === 'ig_token' && <span className="text-[10px] text-emerald-600 font-bold">Copied!</span>}
              </div>
            </div>
          </div>

          <button
            onClick={connectInstagram}
            className="w-full py-2.5 bg-gradient-to-r from-pink-600 to-purple-600 hover:opacity-90 text-white rounded-xl text-xs font-bold shadow-xs transition-all"
          >
            {status?.instagram?.connected ? 'Reconnect Instagram Account' : 'Connect Instagram Professional'}
          </button>
        </div>

        {/* WhatsApp Cloud API Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white shadow-md">
                  <Phone className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900">WhatsApp Cloud API</h3>
                  <p className="text-xs text-slate-400">Meta WhatsApp Business Platform</p>
                </div>
              </div>

              <span
                className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                  status?.whatsapp?.connected
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {status?.whatsapp?.connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Handles WhatsApp chat conversations, catalogue lookups, locality delivery calculations, and interactive order buttons.
            </p>

            {status?.whatsapp?.connected && (
              <div className="p-3 bg-slate-50 rounded-xl space-y-1 text-xs">
                <p className="text-slate-500">Business Phone: <strong className="text-slate-900">{status.whatsapp.username}</strong></p>
                <p className="text-slate-500">Scopes: <code className="text-emerald-600 font-mono text-[10px]">whatsapp_business_messaging</code></p>
              </div>
            )}

            {/* Webhook details */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">WhatsApp Callback URL</span>
                <div className="mt-1 flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs font-mono text-slate-700 overflow-x-auto">
                  <span className="flex-1 truncate">{status?.whatsapp?.webhook_url}</span>
                  <button
                    onClick={() => copyToClipboard(status?.whatsapp?.webhook_url, 'wa_url')}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
                {copied === 'wa_url' && <span className="text-[10px] text-emerald-600 font-bold">Copied!</span>}
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Verify Token</span>
                <div className="mt-1 flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs font-mono text-slate-700">
                  <span className="flex-1">{status?.whatsapp?.verify_token}</span>
                  <button
                    onClick={() => copyToClipboard(status?.whatsapp?.verify_token, 'wa_token')}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
                {copied === 'wa_token' && <span className="text-[10px] text-emerald-600 font-bold">Copied!</span>}
              </div>
            </div>
          </div>

          <button
            onClick={connectWhatsApp}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-xs transition-all"
          >
            {status?.whatsapp?.connected ? 'Reconnect WhatsApp Number' : 'Connect Dedicated Business Phone'}
          </button>
        </div>
      </div>
    </div>
  );
}
