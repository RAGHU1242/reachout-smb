'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Store,
  MapPin,
  Languages,
  Truck,
  CreditCard,
  Instagram,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Bot
} from 'lucide-react';
import { apiRequest } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    name: 'Rani Fashions',
    business_type: 'Fashion & Sarees',
    location: 'Hyderabad, Telangana',
    city: 'Hyderabad',
    currency: 'INR',
    languages: ['Telugu', 'English', 'Hindi'],
    delivery_regions: ['Hyderabad Metro', 'Secunderabad'],
    payment_methods: ['UPI', 'Cash on Delivery'],
    return_policy: '7-day easy exchange for unstitched sarees with original tags.',
    description: 'Exclusive handloom sarees, Kanjeevaram silk, Banarasi, and daily-wear ethnic fashion.',
    connect_instagram: true,
    connect_whatsapp: true,
  });

  const toggleLanguage = (lang: string) => {
    if (formData.languages.includes(lang)) {
      if (formData.languages.length > 1) {
        setFormData({ ...formData, languages: formData.languages.filter((l) => l !== lang) });
      }
    } else {
      setFormData({ ...formData, languages: [...formData.languages, lang] });
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      const res = await apiRequest<{ id: string }>('/api/v1/businesses/onboarding', {
        method: 'POST',
        body: JSON.stringify(formData),
      });
      localStorage.setItem('reachout_business_id', res.id);
      router.push('/dashboard');
    } catch (err) {
      // If error or already exists, navigate to dashboard
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-center items-center p-6">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Business Onboarding</h2>
              <p className="text-xs text-slate-400">Step {step} of 3 • ReachOut SMB Setup</p>
            </div>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            {step === 1 ? 'Profile' : step === 2 ? 'Operations' : 'AI & Channels'}
          </span>
        </div>

        {/* Step 1: Business Profile */}
        {step === 1 && (
          <div className="space-y-4 py-6">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Business Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Business Category</label>
                <input
                  type="text"
                  value={formData.business_type}
                  onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">City / State</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value, city: e.target.value.split(',')[0] })}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Description</label>
              <textarea
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        )}

        {/* Step 2: Languages & Delivery */}
        {step === 2 && (
          <div className="space-y-6 py-6">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase">Supported Customer Languages</label>
              <div className="grid grid-cols-3 gap-3">
                {['Telugu', 'English', 'Hindi'].map((lang) => {
                  const active = formData.languages.includes(lang);
                  return (
                    <button
                      key={lang}
                      type="button"
                      onClick={() => toggleLanguage(lang)}
                      className={`p-3 rounded-xl border text-sm font-semibold flex items-center justify-between transition-colors ${
                        active
                          ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300'
                          : 'bg-slate-950 border-slate-800 text-slate-400'
                      }`}
                    >
                      <span>{lang}</span>
                      {active && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Return & Exchange Policy</label>
              <input
                type="text"
                value={formData.return_policy}
                onChange={(e) => setFormData({ ...formData, return_policy: e.target.value })}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Default Currency</label>
                <input
                  type="text"
                  disabled
                  value="INR (₹)"
                  className="w-full px-4 py-3 bg-slate-950/60 border border-slate-800/80 rounded-xl text-sm text-slate-400"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase">Payment Methods</label>
                <div className="px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200">
                  UPI, Cash on Delivery, Cards
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Connect Channels & Activate AI */}
        {step === 3 && (
          <div className="space-y-4 py-6">
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-pink-500 to-purple-600 flex items-center justify-center text-white">
                  <Instagram className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Instagram Professional Account</h4>
                  <p className="text-xs text-slate-400">Handle direct messages and saree recommendations</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.connect_instagram}
                  onChange={(e) => setFormData({ ...formData, connect_instagram: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white">
                  <Truck className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">WhatsApp Business Cloud API</h4>
                  <p className="text-xs text-slate-400">Automated catalogue browsing and order updates</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.connect_whatsapp}
                  onChange={(e) => setFormData({ ...formData, connect_whatsapp: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>

            <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-800/40 flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-indigo-400 shrink-0" />
              <p className="text-xs text-indigo-200">
                Gemini Flash AI sales model is pre-configured with Telugu, Hindi, and English support. Mock Mode is ready out of the box.
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-800">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="px-5 py-2.5 rounded-xl border border-slate-800 text-xs font-semibold text-slate-300 hover:bg-slate-800"
            >
              Back
            </button>
          ) : <div />}

          {step < 3 ? (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold text-white flex items-center gap-2"
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              type="button"
              disabled={loading}
              onClick={handleComplete}
              className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 rounded-xl text-xs font-bold text-white flex items-center gap-2 shadow-lg shadow-indigo-600/30 disabled:opacity-50"
            >
              <span>{loading ? 'Activating Business...' : 'Complete & Launch Dashboard'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
