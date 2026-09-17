'use client';

import { useState } from 'react';
import { BookOpen, Save, Plus, HelpCircle, Shield, Clock } from 'lucide-react';

export default function KnowledgePage() {
  const [storeTimings, setStoreTimings] = useState('Mon-Sat: 10:00 AM - 9:00 PM, Sun: 11:00 AM - 7:00 PM');
  const [returnPolicy, setReturnPolicy] = useState('7-day exchange for unworn sarees with original tags and packaging.');
  const [deliveryPolicy, setDeliveryPolicy] = useState('Same-day & next-day delivery across Hyderabad Metro. Free delivery on orders above ₹2,500.');
  const [customPrompt, setCustomPrompt] = useState('Always greet politely with Namaste. Address customers warmly. If asked for recommendations under 1500, highlight the Crimson Kanjeevaram and Pochampally Ikkat.');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Knowledge Base & AI Directives</h2>
        <p className="text-xs text-slate-500 mt-1">
          Store facts, store timings, and business policies that the AI sales assistant references during customer conversations.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-indigo-600" />
            <span>Store Working Hours</span>
          </label>
          <input
            type="text"
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
            value={returnPolicy}
            onChange={(e) => setReturnPolicy(e.target.value)}
            className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
          />
        </div>

        <div>
          <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
            <HelpCircle className="w-4 h-4 text-amber-600" />
            <span>Delivery Policy & Timelines</span>
          </label>
          <textarea
            rows={2}
            value={deliveryPolicy}
            onChange={(e) => setDeliveryPolicy(e.target.value)}
            className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
          />
        </div>

        <div>
          <label className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-violet-600" />
            <span>Custom Regional AI Instructions (Telugu / Hindi)</span>
          </label>
          <textarea
            rows={3}
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            className="w-full mt-1.5 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
          />
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          {saved ? (
            <span className="text-xs font-bold text-emerald-600">Saved successfully!</span>
          ) : <div />}

          <button
            type="submit"
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition-all"
          >
            <Save className="w-4 h-4" />
            <span>Save Knowledge Directives</span>
          </button>
        </div>
      </form>
    </div>
  );
}
