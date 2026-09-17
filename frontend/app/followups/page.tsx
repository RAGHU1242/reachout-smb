'use client';

import { useEffect, useState } from 'react';
import { Clock, CheckCircle, Calendar, Plus, MessageSquare, AlertCircle } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { FollowUp } from '@/types';
import { formatDate } from '@/lib/utils';

export default function FollowupsPage() {
  const [followups, setFollowups] = useState<FollowUp[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await apiRequest<FollowUp[]>('/api/v1/followups');
      setFollowups(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Follow-Up Automation Queue</h2>
        <p className="text-xs text-slate-500 mt-1">
          Automated customer re-engagement. AI schedules follow-up messages for abandoned inquiries while respecting customer DND.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-800">Scheduled Follow-Ups</h3>
          <span className="text-xs text-slate-400 font-medium">{followups.length} scheduled</span>
        </div>

        {followups.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {followups.map((item) => (
              <div key={item.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-slate-900">{item.customer_name || 'Customer'}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                      {item.channel}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
                      {item.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 font-medium italic">"{item.message}"</p>
                  <p className="text-[11px] text-slate-400">Reason: {item.reason}</p>
                </div>

                <div className="text-right">
                  <span className="text-xs font-semibold text-slate-800 flex items-center gap-1 justify-end">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{formatDate(item.scheduled_at)}</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-400 space-y-2">
            <Clock className="w-8 h-8 text-slate-300 mx-auto" />
            <p>No follow-ups currently scheduled. AI will automatically queue follow-ups when customers ask about products without completing an order.</p>
          </div>
        )}
      </div>
    </div>
  );
}
