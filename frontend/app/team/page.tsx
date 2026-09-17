'use client';

import { useState } from 'react';
import { Users2, Shield, UserPlus, Mail, CheckCircle2 } from 'lucide-react';

export default function TeamPage() {
  const [members, setMembers] = useState([
    { name: 'Raghavendra Sharma', email: 'demo@reachoutsmb.com', role: 'OWNER', status: 'Active' },
    { name: 'Srinivas Varma', email: 'srinivas@ranifashions.com', role: 'ADMIN', status: 'Active' },
    { name: 'Meenakshi Kumari', email: 'meenakshi@ranifashions.com', role: 'STAFF', status: 'Active' },
    { name: 'Kavita Rao', email: 'kavita@ranifashions.com', role: 'VIEWER', status: 'Active' },
  ]);

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Team & Role-Based Access</h2>
          <p className="text-xs text-slate-500 mt-1">
            Manage staff members who can take over conversations from AI and manage orders.
          </p>
        </div>

        <button className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-xs">
          <UserPlus className="w-4 h-4" />
          <span>Invite Member</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="divide-y divide-slate-100">
          {members.map((m, idx) => (
            <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 font-bold flex items-center justify-center text-xs">
                  {m.name.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <h4 className="font-bold text-xs text-slate-900">{m.name}</h4>
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
                  <span>{m.status}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
