'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  ShoppingBag,
  Flame,
  MessageSquare,
  Bot,
  UserCheck,
  ArrowUpRight,
  Sparkles,
  Clock,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { AnalyticsOverview } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function DashboardPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest<AnalyticsOverview>('/api/v1/analytics/overview');
      setData(res);
      if (res.business_name && typeof window !== 'undefined') {
        localStorage.setItem('reachout_business_name', res.business_name);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load live analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <span>{error}</span>
          <button
            onClick={loadData}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Top Banner with Quick Actions */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-2xl p-6 text-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Live & Autonomous
            </span>
            <span className="text-xs text-slate-400">• {data?.city || 'Active Business'} Hub</span>
          </div>
          <h2 className="text-2xl font-bold mt-1 tracking-tight">{data?.business_name || 'ReachOut SMB'} — AI Sales Hub</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            AI Assistant is handling customer inquiries in Telugu, Hindi, and English across Instagram DM and WhatsApp.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={loadData}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            href="/dev/simulator"
            className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-md shadow-emerald-700/30 transition-all hover:scale-[1.02]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Launch Live Simulator</span>
          </Link>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Revenue */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 tracking-tight">
            {formatCurrency(data?.total_revenue || 0)}
          </p>
          <p className="text-[11px] text-slate-500 font-medium mt-1">
            Confirmed from {data?.total_orders || 0} order(s)
          </p>
        </div>

        {/* Total Orders */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Confirmed Orders</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <ShoppingBag className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 tracking-tight">
            {data?.total_orders || 0}
          </p>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            Conv. Rate: <strong className="text-slate-800">{data?.conversion_rate || 0}%</strong>
          </p>
        </div>

        {/* Hot Leads */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Hot Leads</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 tracking-tight">
            {data?.hot_leads || 0}
          </p>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            {data?.new_leads || 0} new lead(s) qualified by AI
          </p>
        </div>

        {/* AI Handling Rate */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">AI Handling Rate</span>
            <div className="w-8 h-8 rounded-lg bg-violet-50 flex items-center justify-center text-violet-600">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 tracking-tight">
            {data?.ai_handling_rate || 100}%
          </p>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            {data?.human_handoff_count || 0} staff takeover(s)
          </p>
        </div>
      </div>

      {/* AI Business Insights Card */}
      <div className="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-5 flex items-start gap-4">
        <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm">
          <Sparkles className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900">AI Business Intelligence & Insights</h4>
          {data?.insights && data.insights.length > 0 ? (
            data.insights.map((insight, idx) => (
              <p key={idx} className="text-xs text-indigo-800 leading-relaxed">
                • {insight}
              </p>
            ))
          ) : (
            <p className="text-xs text-indigo-700/80 italic leading-relaxed">
              No business insights generated yet. Automated intelligence will emerge once live customer conversations and product orders are recorded.
            </p>
          )}
        </div>
      </div>

      {/* 2-Column Split: Recent Orders & Hot Leads */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-900">Recent Customer Orders</h3>
            </div>
            <Link href="/orders" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {data?.recent_orders && data.recent_orders.length > 0 ? (
              data.recent_orders.map((order) => (
                <div key={order.id} className="p-4 hover:bg-slate-50/70 transition-colors flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-slate-900">{order.order_number}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        order.status === 'CONFIRMED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                        order.status === 'SHIPPED' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {order.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Customer: {order.customer_name || 'Walk-in'}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm text-slate-900">{formatCurrency(order.total)}</p>
                    <p className="text-[11px] text-slate-400">{formatDate(order.created_at)}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="p-6 text-center text-xs text-slate-400">No recent orders yet</p>
            )}
          </div>
        </div>

        {/* Hot Leads */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-rose-500" />
              <h3 className="font-bold text-sm text-slate-900">AI-Qualified Hot Leads</h3>
            </div>
            <Link href="/leads" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              <span>View Pipeline</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {data?.hot_leads_list && data.hot_leads_list.length > 0 ? (
              data.hot_leads_list.map((lead) => (
                <div key={lead.id} className="p-4 hover:bg-slate-50/70 transition-colors flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900">{lead.customer_name}</span>
                      <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                        SCORE {lead.score}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">Interest: {lead.product_interest}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-emerald-600">
                      Budget: {lead.budget ? formatCurrency(lead.budget) : 'Flexible'}
                    </span>
                    <p className="text-[11px] text-slate-400">{formatDate(lead.created_at)}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="p-6 text-center text-xs text-slate-400">No active leads</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
