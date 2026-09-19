'use client';

import { useEffect, useState } from 'react';
import { Users, Search, Phone, Mail, Plus, Trash2, Edit2, AlertCircle } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Customer } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  // New customer state
  const [newCust, setNewCust] = useState({
    name: '',
    phone: '',
    email: '',
    preferred_language: 'Telugu',
    source: 'INSTAGRAM',
    notes: '',
  });

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<Customer[]>('/api/v1/customers');
      setCustomers(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load customers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiRequest('/api/v1/customers', {
        method: 'POST',
        body: JSON.stringify(newCust),
      });
      setShowModal(false);
      setNewCust({
        name: '',
        phone: '',
        email: '',
        preferred_language: 'Telugu',
        source: 'INSTAGRAM',
        notes: '',
      });
      loadCustomers();
    } catch (err: any) {
      alert(err.message || 'Failed to create customer');
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete customer "${name}"?`)) return;
    try {
      await apiRequest(`/api/v1/customers/${id}`, {
        method: 'DELETE',
      });
      setCustomers((prev) => prev.filter((c) => c.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete customer');
    }
  };

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.phone && c.phone.includes(search)) ||
      (c.email && c.email.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Customer CRM Directory</h2>
          <p className="text-xs text-slate-500 mt-1">
            Unified customer profiles from Instagram, WhatsApp, and in-store orders with full lifetime spend.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add Customer</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadCustomers}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

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
          <span className="text-xs text-slate-400 font-medium">{filtered.length} customer(s)</span>
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
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-xs text-slate-400">
                    Loading customer directory...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-xs text-slate-400">
                    No customers found matching your search.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => (
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
                        {c.preferred_language || '—'}
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
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleDelete(c.id, c.name)}
                        className="p-1.5 hover:bg-rose-50 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
                        title="Delete customer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Customer Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Add New Customer</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Customer Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ananya Rao"
                  value={newCust.name}
                  onChange={(e) => setNewCust({ ...newCust, name: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Phone Number</label>
                <input
                  type="tel"
                  placeholder="+919876543210"
                  value={newCust.phone}
                  onChange={(e) => setNewCust({ ...newCust, phone: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Email Address</label>
                <input
                  type="email"
                  placeholder="customer@example.com"
                  value={newCust.email}
                  onChange={(e) => setNewCust({ ...newCust, email: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Preferred Language</label>
                  <select
                    value={newCust.preferred_language}
                    onChange={(e) => setNewCust({ ...newCust, preferred_language: e.target.value })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  >
                    <option value="Telugu">Telugu</option>
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Channel Source</label>
                  <select
                    value={newCust.source}
                    onChange={(e) => setNewCust({ ...newCust, source: e.target.value })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  >
                    <option value="INSTAGRAM">Instagram</option>
                    <option value="WHATSAPP">WhatsApp</option>
                    <option value="WALK_IN">In-Store / Direct</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Notes / Preferences</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Prefers silk sarees, delivery to Gachibowli"
                  value={newCust.notes}
                  onChange={(e) => setNewCust({ ...newCust, notes: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-sm"
                >
                  Save Customer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
