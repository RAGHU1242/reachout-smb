'use client';

import { useEffect, useState } from 'react';
import { Settings, Truck, Bot, Save, Plus, MapPin } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { DeliveryZone } from '@/types';
import { formatCurrency } from '@/lib/utils';

export default function SettingsPage() {
  const [zones, setZones] = useState<DeliveryZone[]>([]);
  const [newLocality, setNewLocality] = useState('');
  const [newFee, setNewFee] = useState(50);
  const [newPincode, setNewPincode] = useState('');
  const [saved, setSaved] = useState(false);

  const loadZones = async () => {
    try {
      const data = await apiRequest<DeliveryZone[]>('/api/v1/delivery-zones');
      setZones(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadZones();
  }, []);

  const handleAddZone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLocality.trim()) return;

    try {
      await apiRequest('/api/v1/delivery-zones', {
        method: 'POST',
        body: JSON.stringify({
          city: 'Hyderabad',
          locality: newLocality,
          delivery_fee: Number(newFee),
          pincode: newPincode,
          active: true,
        }),
      });
      setNewLocality('');
      setNewPincode('');
      loadZones();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Store Settings & Delivery Zones</h2>
        <p className="text-xs text-slate-500 mt-1">
          Configure regional delivery fees. The AI will strictly compute these fees whenever customers ask about locality delivery.
        </p>
      </div>

      {/* Delivery Zones Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
            <Truck className="w-4 h-4 text-indigo-600" />
            <span>Configured Delivery Zones (Hyderabad Metro)</span>
          </div>
          <span className="text-xs text-slate-400 font-medium">{zones.length} active zones</span>
        </div>

        {/* Existing Zones */}
        <div className="grid sm:grid-cols-2 gap-3">
          {zones.map((zone) => (
            <div key={zone.id} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2.5">
                <MapPin className="w-4 h-4 text-slate-400" />
                <div>
                  <p className="font-bold text-slate-900">{zone.locality}</p>
                  <p className="text-[10px] text-slate-400 font-mono">Pin: {zone.pincode || 'Metro'}</p>
                </div>
              </div>
              <span className="font-extrabold text-indigo-600 text-sm">
                {formatCurrency(zone.delivery_fee)}
              </span>
            </div>
          ))}
        </div>

        {/* Add Zone Form */}
        <form onSubmit={handleAddZone} className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row gap-3 items-end">
          <div className="flex-1 w-full">
            <label className="text-[10px] font-bold text-slate-500 uppercase">Locality / Area</label>
            <input
              type="text"
              required
              placeholder="e.g. Madhapur"
              value={newLocality}
              onChange={(e) => setNewLocality(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
            />
          </div>

          <div className="w-full sm:w-32">
            <label className="text-[10px] font-bold text-slate-500 uppercase">Delivery Fee (₹)</label>
            <input
              type="number"
              required
              value={newFee}
              onChange={(e) => setNewFee(Number(e.target.value))}
              className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
            />
          </div>

          <div className="w-full sm:w-32">
            <label className="text-[10px] font-bold text-slate-500 uppercase">Pincode</label>
            <input
              type="text"
              placeholder="500081"
              value={newPincode}
              onChange={(e) => setNewPincode(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium font-mono"
            />
          </div>

          <button
            type="submit"
            className="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shrink-0 transition-colors"
          >
            Add Zone
          </button>
        </form>
      </div>

      {/* AI Safeguards & Rules */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
          <Bot className="w-4 h-4 text-violet-600" />
          <span>AI Model & Escalation Rules</span>
        </div>

        <div className="space-y-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl flex items-center justify-between">
            <div>
              <p className="font-bold text-slate-800">Primary AI Model</p>
              <p className="text-[11px] text-slate-500">Configured model for low-latency conversational tool use</p>
            </div>
            <span className="font-mono font-semibold px-2 py-1 bg-indigo-50 text-indigo-700 rounded border border-indigo-200">
              gemini-2.5-flash
            </span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl flex items-center justify-between">
            <div>
              <p className="font-bold text-slate-800">Free Delivery Threshold</p>
              <p className="text-[11px] text-slate-500">Orders above this subtotal automatically receive zero delivery fee</p>
            </div>
            <span className="font-bold text-emerald-700 px-2 py-1 bg-emerald-50 rounded border border-emerald-200">
              ₹2,500
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
