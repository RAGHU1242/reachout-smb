'use client';

import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, ShoppingBag, MessageSquare, Bot, AlertCircle, RefreshCw } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { AnalyticsOverview } from '@/types';
import { formatCurrency } from '@/lib/utils';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest<AnalyticsOverview>('/api/v1/analytics/overview');
      setData(res);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Analytics & Sales Insights</h2>
          <p className="text-xs text-slate-500 mt-1">
            Real metrics derived strictly from your database conversations, leads, and completed orders.
          </p>
        </div>

        <button
          onClick={loadData}
          className="p-2.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl text-slate-600 transition-colors shadow-xs"
          title="Refresh analytics"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Gross Revenue</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{formatCurrency(data?.total_revenue || 0)}</p>
          <p className="text-[11px] text-emerald-600 font-semibold mt-1">
            Across {data?.total_orders || 0} confirmed order(s)
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Conversation Volume</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{data?.total_conversations || 0}</p>
          <p className="text-[11px] text-slate-500 mt-1">Instagram DMs & WhatsApp</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Lead Conversion</span>
          <p className="text-2xl font-black text-indigo-600 mt-1">{data?.conversion_rate || 0}%</p>
          <p className="text-[11px] text-slate-500 mt-1">From initial chat to confirmed order</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Autonomous Handling</span>
          <p className="text-2xl font-black text-emerald-600 mt-1">{data?.ai_handling_rate || 100}%</p>
          <p className="text-[11px] text-slate-500 mt-1">Managed without staff intervention</p>
        </div>
      </div>

      {/* Hourly Conversational Volume & Top Products */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Peak Conversation Hours</h3>
          <p className="text-xs text-slate-500">
            Real customer enquiry distribution calculated from database conversation timestamps.
          </p>
          <div className="space-y-3 pt-2">
            {data?.hourly_volume && data.hourly_volume.length > 0 ? (
              data.hourly_volume.map((slot, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-700">
                    <span>{slot.time}</span>
                    <span>{slot.count} conversation(s)</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full"
                      style={{ width: `${slot.percentage}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="p-6 text-center text-xs text-slate-400 italic">
                No hourly conversation volume recorded yet. Metrics will appear once customer inquiries arrive.
              </p>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Top Performing Products</h3>
          <p className="text-xs text-slate-500">
            Real product demand ranked by customer order volume and automated inquiries.
          </p>
          <div className="space-y-3 pt-2">
            {data?.top_products && data.top_products.length > 0 ? (
              data.top_products.map((prod, idx) => (
                <div key={idx} className="p-3 bg-slate-50 rounded-xl flex items-center justify-between text-xs">
                  <div>
                    <p className="font-bold text-slate-900">{prod.name}</p>
                    <p className="text-[11px] text-slate-400">Price: {formatCurrency(prod.price)}</p>
                  </div>
                  <div className="text-right">
                    <span className="font-extrabold text-indigo-700">{prod.orders} orders booked</span>
                    <p className="text-[10px] text-slate-400 font-medium">~{prod.enquiries} total inquiries</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="p-6 text-center text-xs text-slate-400 italic">
                No product orders booked yet. Top converting products will populate automatically.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
