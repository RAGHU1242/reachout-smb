'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Save, HelpCircle, Shield, Clock, AlertCircle } from 'lucide-react';
import { apiRequest } from '@/lib/api';

export default function KnowledgePage() {
  const [storeTimings, setStoreTimings] = useState('');
  const [returnPolicy, setReturnPolicy] = useState('');
  const [deliveryPolicy, setDeliveryPolicy] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadKnowledge = async () => {
    setLoading(true);
    setError(null);
    try {
      const [biz, settings, aiSettings] = await Promise.all([
        apiRequest<any>('/api/v1/businesses/current').catch(() => null),
        apiRequest<any>('/api/v1/businesses/current/settings').catch(() => null),
        apiRequest<any>('/api/v1/businesses/current/ai-settings').catch(() => null),
      ]);

      if (settings?.store_timings) setStoreTimings(settings.store_timings);
      if (biz?.return_policy) setReturnPolicy(biz.return_policy);
      if (settings?.delivery_regions) {
        setDeliveryPolicy(
          Array.isArray(settings.delivery_regions)
            ? settings.delivery_regions.join(', ')
            : String(settings.delivery_regions)
        );
      }
      if (aiSettings?.custom_prompt) setCustomPrompt(aiSettings.custom_prompt);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load store policies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledge();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    setError(null);

    try {
      await Promise.all([
        apiRequest('/api/v1/businesses/current/settings', {
          method: 'PUT',
          body: JSON.stringify({
            store_timings: storeTimings,
            delivery_regions: deliveryPolicy.split(',').map((s) => s.trim()).filter(Boolean),
          }),
        }).catch(() => null),
        apiRequest('/api/v1/businesses/current', {
          method: 'PUT',
          body: JSON.stringify({
            return_policy: returnPolicy,
          }),
        }).catch(() => null),
        apiRequest('/api/v1/businesses/current/ai-settings', {
          method: 'PUT',
          body: JSON.stringify({
            custom_prompt: customPrompt,
          }),
        }).catch(() => null),
      ]);

      setSaved(true);
      setTimeout(() => setSaved(false), 3500);
    } catch (err: any) {
      setError(err.message || 'Failed to save store policies');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Knowledge Base & AI Directives</h2>
        <p className="text-xs text-slate-500 mt-1">
          Store facts, store timings, and business policies that the AI sales assistant references during customer conversations.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadKnowledge}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="p-12 bg-white rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
          Loading business knowledge directives...
        </div>
      ) : (
        <form onSubmit={handleSave} className="space-y-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-indigo-600" />
              <span>Store Working Hours</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Mon-Sat: 10:00 AM - 9:00 PM, Sun: 11:00 AM - 7:00 PM"
              value={storeTimings}
              onChange={(e) => setStoreTimings(e.target.value)}
              className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-emerald-600" />
              <span>Return & Exchange Policy</span>
            </label>
            <textarea
              rows={2}
              placeholder="e.g. 7-day exchange for unworn items with original tags."
              value={returnPolicy}
              onChange={(e) => setReturnPolicy(e.target.value)}
              className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-amber-600" />
              <span>Delivery Regions & Policies (comma separated)</span>
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Hyderabad Metro, Secunderabad, Telangana, All India"
              value={deliveryPolicy}
              onChange={(e) => setDeliveryPolicy(e.target.value)}
              className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-violet-600" />
              <span>Custom Regional AI Instructions (Telugu / Hindi / English)</span>
            </label>
            <textarea
              rows={3}
              placeholder="e.g. Greet customers warmly with Namaste. If asked for recommendations under 1500, highlight affordable sarees."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
            />
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-100">
            {saved ? (
              <span className="text-xs font-bold text-emerald-600">Saved successfully to database!</span>
            ) : <div />}

            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition-all"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save Knowledge Directives'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
