'use client';

import { useState, useEffect } from 'react';
import { Users2, Shield, UserPlus, Mail, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { TeamMember } from '@/types';

export default function TeamPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Invite state
  const [invite, setInvite] = useState({
    full_name: '',
    email: '',
    role: 'STAFF',
  });

  const loadMembers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<TeamMember[]>('/api/v1/businesses/current/members');
      setMembers(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load team members');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiRequest('/api/v1/businesses/current/members', {
        method: 'POST',
        body: JSON.stringify(invite),
      });
      setShowModal(false);
      setInvite({ full_name: '', email: '', role: 'STAFF' });
      loadMembers();
    } catch (err: any) {
      alert(err.message || 'Failed to invite team member');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Team & Role-Based Access</h2>
          <p className="text-xs text-slate-500 mt-1">
            Manage staff members who can take over conversations from AI and manage orders.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadMembers}
            className="p-2.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl text-slate-600 transition-colors shadow-xs"
            title="Refresh members"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-xs"
          >
            <UserPlus className="w-4 h-4" />
            <span>Invite Member</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadMembers}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading team members...</div>
        ) : members.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">No active team members registered yet.</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {members.map((m) => (
              <div key={m.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 font-bold flex items-center justify-center text-xs">
                    {(m.full_name || m.email).slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-slate-900">{m.full_name || 'Staff Member'}</h4>
                    <p className="text-[11px] text-slate-400">{m.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span
                    className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full ${
                      m.role === 'OWNER'
                        ? 'bg-purple-50 text-purple-700 border border-purple-200'
                        : m.role === 'ADMIN'
                        ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {m.role}
                  </span>
                  <span className="text-[10px] text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{m.status || 'Active'}</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Invite Member Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Invite Team Member</h3>
            <form onSubmit={handleInvite} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Srinivas Rao"
                  value={invite.full_name}
                  onChange={(e) => setInvite({ ...invite, full_name: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="colleague@business.com"
                  value={invite.email}
                  onChange={(e) => setInvite({ ...invite, email: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Access Role</label>
                <select
                  value={invite.role}
                  onChange={(e) => setInvite({ ...invite, role: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                >
                  <option value="STAFF">STAFF (Can reply to customer chats)</option>
                  <option value="ADMIN">ADMIN (Can manage products, orders & team)</option>
                  <option value="VIEWER">VIEWER (Read-only analytics)</option>
                </select>
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
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
