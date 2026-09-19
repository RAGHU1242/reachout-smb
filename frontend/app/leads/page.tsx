'use client';

import { useEffect, useState } from 'react';
import { Flame, Search, Filter, ArrowRight, User } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Lead } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadLeads = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<Lead[]>('/api/v1/leads');
      setLeads(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load leads pipeline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  const updateLeadStatus = async (leadId: string, newStatus: string) => {
    try {
      const updated = await apiRequest<Lead>(`/api/v1/leads/${leadId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });
      setLeads((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = leads.filter((l) => {
    const matchStatus = statusFilter === 'ALL' || l.status === statusFilter;
    const matchSearch =
      (l.customer_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (l.product_interest || '').toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Leads & Deal Pipeline</h2>
        <p className="text-xs text-slate-500 mt-1">
          AI continuously scores incoming customer purchase intent from Instagram DMs and WhatsApp chats.
        </p>
      </div>

      {/* Filter Chips */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-1.5 text-xs font-semibold">
          {['ALL', 'HOT', 'WARM', 'COLD', 'CONVERTED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                statusFilter === st
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="relative w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search lead or product interest..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none"
          />
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <span>{error}</span>
          <button
            onClick={loadLeads}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Leads Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="p-4">Customer</th>
                <th className="p-4">Product Interest</th>
                <th className="p-4">Budget</th>
                <th className="p-4">AI Score</th>
                <th className="p-4">Status</th>
                <th className="p-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-xs text-slate-400">Loading leads...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-xs text-slate-400">No leads found in pipeline.</td>
                </tr>
              ) : (
                filtered.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="p-4">
                      <p className="font-bold text-slate-900">{lead.customer_name || 'Customer'}</p>
                      <p className="text-[10px] text-slate-400">{formatDate(lead.created_at)}</p>
                    </td>
                    <td className="p-4">
                      <p className="font-semibold text-slate-800">{lead.product_interest || 'General Enquiry'}</p>
                      <p className="text-[10px] text-slate-400 line-clamp-1">{lead.notes}</p>
                    </td>
                  <td className="p-4 font-semibold">
                    {lead.budget ? formatCurrency(lead.budget) : 'Not specified'}
                  </td>
                  <td className="p-4">
                    <span
                      className={`text-xs font-black px-2.5 py-1 rounded-full ${
                        lead.score >= 80
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : lead.score >= 60
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {lead.score} / 100
                    </span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        lead.status === 'HOT'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : lead.status === 'CONVERTED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {lead.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-1.5">
                      {lead.status !== 'CONVERTED' && (
                        <button
                          onClick={() => updateLeadStatus(lead.id, 'CONVERTED')}
                          className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-lg text-[10px] font-bold"
                        >
                          Mark Converted
                        </button>
                      )}
                      {lead.status !== 'HOT' && (
                        <button
                          onClick={() => updateLeadStatus(lead.id, 'HOT')}
                          className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-lg text-[10px] font-bold"
                        >
                          Mark Hot
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
