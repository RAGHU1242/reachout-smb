'use client';

import { useEffect, useState } from 'react';
import { ShoppingBag, Plus, Search, Trash2, Edit3, AlertCircle } from 'lucide-react';
import { apiRequest } from '@/lib/api';
import { Product } from '@/types';
import { formatCurrency } from '@/lib/utils';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // New product state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 999,
    sku: '',
    stock: 10,
    color: 'Red',
    image: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
  });

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<Product[]>('/api/v1/products');
      setProducts(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        // Update product
        await apiRequest(`/api/v1/products/${editingProduct.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            name: formData.name,
            description: formData.description,
            price: Number(formData.price),
            stock: Number(formData.stock),
            color: formData.color,
          }),
        });
      } else {
        // Create product
        await apiRequest('/api/v1/products', {
          method: 'POST',
          body: JSON.stringify({
            name: formData.name,
            description: formData.description,
            price: Number(formData.price),
            sku: formData.sku || `RF-SKU-${Math.floor(1000 + Math.random() * 9000)}`,
            stock: Number(formData.stock),
            color: formData.color,
            images: [formData.image],
          }),
        });
      }
      setShowModal(false);
      setEditingProduct(null);
      resetForm();
      loadProducts();
    } catch (err: any) {
      alert(err.message || 'Failed to save product');
    }
  };

  const handleDelete = async (prod: Product) => {
    if (!confirm(`Are you sure you want to delete "${prod.name}"?`)) return;
    try {
      await apiRequest(`/api/v1/products/${prod.id}`, {
        method: 'DELETE',
      });
      setProducts((prev) => prev.filter((p) => p.id !== prod.id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete product');
    }
  };

  const openEdit = (prod: Product) => {
    setEditingProduct(prod);
    setFormData({
      name: prod.name,
      description: prod.description || '',
      price: prod.price,
      sku: prod.sku,
      stock: prod.stock,
      color: prod.color || 'Red',
      image: prod.images?.[0]?.image_url || '',
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price: 999,
      sku: '',
      stock: 10,
      color: 'Red',
      image: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
    });
  };

  const filtered = products.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.sku.toLowerCase().includes(search.toLowerCase()) ||
      (p.color && p.color.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Product Catalogue</h2>
          <p className="text-xs text-slate-500 mt-1">
            Authoritative source of items, prices, and stock for the AI sales agent.
          </p>
        </div>

        <button
          onClick={() => {
            setEditingProduct(null);
            resetForm();
            setShowModal(true);
          }}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Product</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between text-xs text-rose-700">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadProducts}
            className="px-3 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-500 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by name, SKU, or color..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Showing {filtered.length} products
        </span>
      </div>

      {/* Loading & Empty States */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading catalog items...</div>
      ) : filtered.length === 0 ? (
        <div className="p-12 bg-white rounded-2xl border border-slate-200 text-center text-xs text-slate-400 space-y-2">
          <ShoppingBag className="w-8 h-8 text-slate-300 mx-auto" />
          <p>No products match your search query.</p>
        </div>
      ) : (
        /* Product Grid */
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {filtered.map((prod) => (
            <div
              key={prod.id}
              className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs hover:shadow-md transition-shadow flex flex-col"
            >
              {/* Image */}
              <div className="relative h-48 bg-slate-100 overflow-hidden">
                {prod.images && prod.images.length > 0 ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={prod.images[0].image_url}
                    alt={prod.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-400">
                    <ShoppingBag className="w-8 h-8" />
                  </div>
                )}
                <span
                  className={`absolute top-2 right-2 text-[10px] font-extrabold px-2 py-0.5 rounded-full ${
                    prod.stock > 0
                      ? 'bg-emerald-500/90 text-white'
                      : 'bg-rose-500/90 text-white'
                  }`}
                >
                  {prod.stock > 0 ? `${prod.stock} in stock` : 'Out of stock'}
                </span>
              </div>

              {/* Details */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-2">
                <div>
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">{prod.sku}</span>
                  <h4 className="font-bold text-sm text-slate-900 line-clamp-1">{prod.name}</h4>
                  <p className="text-xs text-slate-500 line-clamp-2 mt-1">{prod.description || 'No description provided'}</p>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-base font-extrabold text-slate-900">{formatCurrency(prod.price)}</span>
                    {prod.compare_at_price && (
                      <span className="text-xs text-slate-400 line-through ml-2">
                        {formatCurrency(prod.compare_at_price)}
                      </span>
                    )}
                  </div>
                  {prod.color && (
                    <span className="text-[10px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      {prod.color}
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="pt-2 border-t border-slate-100 flex items-center justify-end gap-2">
                  <button
                    onClick={() => openEdit(prod)}
                    className="p-1.5 hover:bg-slate-100 text-slate-500 hover:text-indigo-600 rounded-lg transition-colors text-xs font-medium flex items-center gap-1"
                    title="Edit product"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>
                  <button
                    onClick={() => handleDelete(prod)}
                    className="p-1.5 hover:bg-rose-50 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
                    title="Delete product"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add / Edit Product Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">
              {editingProduct ? 'Edit Catalogue Item' : 'Add New Catalogue Item'}
            </h3>
            <form onSubmit={handleSave} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Product Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Royal Silk Saree"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Price (₹)</label>
                  <input
                    type="number"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Stock Quantity</label>
                  <input
                    type="number"
                    required
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Color / Variant</label>
                  <input
                    type="text"
                    placeholder="e.g. Crimson Red"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  />
                </div>
                {!editingProduct && (
                  <div>
                    <label className="text-xs font-semibold text-slate-700 uppercase">SKU (Optional)</label>
                    <input
                      type="text"
                      placeholder="Leave blank to auto-generate"
                      value={formData.sku}
                      onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                      className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                    />
                  </div>
                )}
              </div>

              {!editingProduct && (
                <div>
                  <label className="text-xs font-semibold text-slate-700 uppercase">Product Image URL</label>
                  <input
                    type="url"
                    value={formData.image}
                    onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                    className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
                  />
                </div>
              )}

              <div>
                <label className="text-xs font-semibold text-slate-700 uppercase">Description</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
                  {editingProduct ? 'Update Product' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
