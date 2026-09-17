'use client';

import { useEffect, useState } from 'react';
import { Users, Search, Phone, Mail, Instagram, MessageCircle, ArrowUpRight } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Customer } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadCustomers = async () => {
    try {
      const data = await apiRequest<Customer[]>('/api/v1/customers');
      setCustomers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.phone && c.phone.includes(search)) ||
      (c.email && c.email.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Customer CRM Directory</h2>
        <p className="text-xs text-slate-500 mt-1">
          Unified customer profiles from Instagram, WhatsApp, and in-store orders with full lifetime spend.
        </p>
      </div>

      {/* Customer List Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="relative w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by name, phone or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none"
            />
          </div>
          <span className="text-xs text-slate-400 font-medium">{filtered.length} customers</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="p-4">Customer</th>
                <th className="p-4">Contact</th>
                <th className="p-4">Language</th>
                <th className="p-4">Source</th>
                <th className="p-4">Orders / Spend</th>
                <th className="p-4">Last Contact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-4">
                    <p className="font-bold text-slate-900">{c.name}</p>
                    <div className="flex gap-1 mt-1">
                      {c.tags?.map((t, idx) => (
                        <span key={idx} className="text-[9px] font-semibold bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-4">
                    <p className="font-mono text-slate-800">{c.phone || '—'}</p>
                    <p className="text-[11px] text-slate-400">{c.email || '—'}</p>
                  </td>
                  <td className="p-4">
                    <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200/50 px-2 py-0.5 rounded">
                      {c.preferred_language || 'Telugu'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-xs font-medium text-slate-700">{c.source}</span>
                  </td>
                  <td className="p-4">
                    <p className="font-bold text-slate-900">{formatCurrency(c.total_spending)}</p>
                    <p className="text-[10px] text-slate-400">{c.order_count} order(s)</p>
                  </td>
                  <td className="p-4 text-[11px] text-slate-400">{formatDate(c.last_interaction)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
