'use client';

import { useEffect, useState } from 'react';
import { ClipboardList, Search, Eye, CheckCircle2, Truck, RefreshCw, ChevronRight } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Order } from '@/types';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadOrders = async () => {
    try {
      const data = await apiRequest<Order[]>('/api/v1/orders');
      setOrders(data);
      if (data.length > 0 && !selectedOrder) {
        setSelectedOrder(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const updateStatus = async (orderId: string, newStatus: string) => {
    try {
      const updated = await apiRequest<Order>(`/api/v1/orders/${orderId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      });
      setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
      setSelectedOrder(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = orders.filter(
    (o) =>
      o.order_number.toLowerCase().includes(search.toLowerCase()) ||
      (o.customer_name || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">Customer Orders</h2>
        <p className="text-xs text-slate-500 mt-1">
          Deterministic order lifecycle. Status transitions are strictly enforced by backend business rules.
        </p>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left: Orders List */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="relative w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by order # or customer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none"
              />
            </div>
            <span className="text-xs text-slate-400 font-medium">{filtered.length} orders</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="p-4">Order #</th>
                  <th className="p-4">Customer</th>
                  <th className="p-4">Items / Total</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Payment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {filtered.map((order) => {
                  const isSel = selectedOrder?.id === order.id;
                  return (
                    <tr
                      key={order.id}
                      onClick={() => setSelectedOrder(order)}
                      className={`cursor-pointer transition-colors ${
                        isSel ? 'bg-indigo-50/70' : 'hover:bg-slate-50/60'
                      }`}
                    >
                      <td className="p-4 font-mono font-bold text-slate-900">{order.order_number}</td>
                      <td className="p-4">
                        <p className="font-semibold text-slate-800">{order.customer_name}</p>
                        <p className="text-[10px] text-slate-400">{formatDate(order.created_at)}</p>
                      </td>
                      <td className="p-4">
                        <p className="font-bold text-slate-900">{formatCurrency(order.total)}</p>
                        <p className="text-[10px] text-slate-400">
                          {order.items.length} item(s) • Del: ₹{order.delivery_fee}
                        </p>
                      </td>
                      <td className="p-4">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            order.status === 'CONFIRMED'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : order.status === 'SHIPPED'
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : order.status === 'DELIVERED'
                              ? 'bg-purple-50 text-purple-700 border border-purple-200'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {order.status}
                        </span>
                      </td>
                      <td className="p-4">
                        <span
                          className={`text-[10px] font-semibold ${
                            order.payment_status === 'PAID' ? 'text-emerald-600' : 'text-amber-600'
                          }`}
                        >
                          {order.payment_status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Selected Order Inspector & Status Transition */}
        {selectedOrder && (
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-semibold uppercase text-slate-400">Order Details</span>
                <h4 className="font-bold text-base text-slate-900 font-mono">{selectedOrder.order_number}</h4>
              </div>
              <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
                {selectedOrder.status}
              </span>
            </div>

            {/* Customer & Address */}
            <div className="text-xs space-y-1 bg-slate-50 p-3.5 rounded-xl">
              <p className="text-slate-500 font-medium">Customer: <strong className="text-slate-900">{selectedOrder.customer_name}</strong></p>
              <p className="text-slate-500 font-medium">Delivery Address:</p>
              <p className="text-slate-800 font-medium leading-relaxed">{selectedOrder.delivery_address || 'Standard Hyderabad Metro'}</p>
            </div>

            {/* Line Items */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold text-slate-700 uppercase">Items in this order</span>
              <div className="divide-y divide-slate-100 border border-slate-100 rounded-xl overflow-hidden">
                {selectedOrder.items.map((item) => (
                  <div key={item.id} className="p-2.5 text-xs flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-slate-800">{item.product_name}</p>
                      <p className="text-[10px] text-slate-400">Qty: {item.quantity} × {formatCurrency(item.unit_price)}</p>
                    </div>
                    <span className="font-bold text-slate-900">{formatCurrency(item.total_price)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Financial Summary */}
            <div className="text-xs space-y-1 pt-2 border-t border-slate-100">
              <div className="flex justify-between text-slate-500">
                <span>Subtotal</span>
                <span>{formatCurrency(selectedOrder.subtotal)}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Delivery Charge</span>
                <span>{formatCurrency(selectedOrder.delivery_fee)}</span>
              </div>
              <div className="flex justify-between text-sm font-bold text-slate-900 pt-1 border-t border-slate-100">
                <span>Total Amount</span>
                <span>{formatCurrency(selectedOrder.total)}</span>
              </div>
            </div>

            {/* Transition Controls */}
            <div className="pt-3 border-t border-slate-100 space-y-2">
              <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Update Order State</span>
              <div className="grid grid-cols-3 gap-2">
                {['PROCESSING', 'SHIPPED', 'DELIVERED'].map((st) => (
                  <button
                    key={st}
                    onClick={() => updateStatus(selectedOrder.id, st)}
                    disabled={selectedOrder.status === st}
                    className={`py-2 rounded-xl text-xs font-bold transition-colors ${
                      selectedOrder.status === st
                        ? 'bg-slate-900 text-white'
                        : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
