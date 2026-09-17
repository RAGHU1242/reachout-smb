import Link from 'next/link';
import {
  Bot,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  MessageSquare,
  ShoppingBag,
  TrendingUp,
  Languages,
  CheckCircle2,
  PhoneCall
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-indigo-500 selection:text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight text-white">ReachOut</span>
              <span className="ml-1 text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                SMB
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#channels" className="hover:text-white transition-colors">Instagram & WhatsApp</a>
            <a href="#multilingual" className="hover:text-white transition-colors">Multilingual AI</a>
            <Link href="/dev/simulator" className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Try Live Simulator</span>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-semibold text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
            >
              <span>Launch Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/30 via-slate-950 to-slate-950 -z-10" />

        <div className="max-w-5xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-800/60 text-indigo-300 text-xs font-semibold mb-8">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Built for Modern D2C & Retail Businesses in India</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
            AI Sales & Order Assistant for{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400">
              Instagram & WhatsApp
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed mb-10 font-normal">
            Never miss a customer DM again. ReachOut SMB automatically answers enquiries in natural{' '}
            <strong className="text-slate-200">Telugu, Hindi & English</strong>, recommends catalogue products with real images, calculates locality delivery fees, and books verified orders directly into your CRM.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold px-8 py-4 rounded-xl shadow-xl shadow-indigo-600/30 text-base transition-all hover:scale-[1.02]"
            >
              <span>Explore Demo Business (Rani Fashions)</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/dev/simulator"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700 font-semibold px-8 py-4 rounded-xl text-base transition-all"
            >
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Test Live Simulator</span>
            </Link>
          </div>

          {/* Social Proof Badges */}
          <div className="pt-12 flex flex-wrap items-center justify-center gap-8 text-xs text-slate-400 font-medium">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Zero Hallucinated Prices or Stock</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Meta Graph API v21.0+ Architecture</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Instant Human Handoff Control</span>
            </div>
          </div>
        </div>

        {/* Live Conversation Showcase Preview */}
        <div className="max-w-4xl mx-auto px-6 mt-16">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-semibold text-slate-200">Instagram DM • Rani Fashions</span>
              </div>
              <span className="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20 font-mono">
                AI Agent Active
              </span>
            </div>

            <div className="space-y-4 py-4 text-sm">
              <div className="flex justify-end">
                <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-sm">
                  Anna red saree undha? Under 1500 kavali.
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-pink-500 to-rose-500 text-white font-bold flex items-center justify-center text-xs shrink-0">
                  AI
                </div>
                <div className="bg-slate-800 border border-slate-700 text-slate-200 rounded-2xl rounded-tl-sm p-3.5 max-w-md space-y-2">
                  <p>ఉందండి 😊 మా దగ్గర అందమైన Crimson Kanjeevaram Silk Saree రెడీ స్టాక్ ఉంది!</p>
                  <div className="bg-slate-950/80 rounded-lg p-2.5 border border-slate-700/60 flex gap-3 items-center">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src="https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=300&q=80"
                      alt="Saree"
                      className="w-16 h-20 object-cover rounded-md"
                    />
                    <div>
                      <p className="font-bold text-white text-xs">Crimson Kanjeevaram Silk Saree</p>
                      <p className="text-emerald-400 font-extrabold text-sm mt-0.5">₹1,299</p>
                      <p className="text-[11px] text-slate-400">Pure silk with gold zari border</p>
                    </div>
                  </div>
                  <p className="text-xs text-slate-300">మీకు ఈ శారీ నచ్చిందా? డెలివరీ ఏ లొకేషన్ కి కావాలి చెప్పండి (ఉదా: Miyapur, Kukatpally) 🚚</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Pillars Section */}
      <section id="features" className="py-20 border-t border-slate-800 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              Turn Casual DMs into Paid Orders
            </h2>
            <p className="text-slate-400 mt-3 text-base">
              Everything small business owners need to run 24/7 autonomous sales without adding customer support staff.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 hover:border-slate-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Languages className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white">Natural Multilingual AI</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Speaks native Telugu, Hindi, English, and natural conversational blends. Understands regional idioms, budget hints, and delivery requirements seamlessly.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 hover:border-slate-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white">Strict Backend Guardrails</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                The AI never invents prices, inventory, or policies. Every product recommendation, stock check, and delivery fee calculation is strictly backed by your database.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 hover:border-slate-700 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <ShoppingBag className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white">One-Click Human Handoff</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Staff can take over any conversation with a single click. The AI pauses automatically when high-value negotiations, complaints, or custom queries arise.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-10 text-center text-xs text-slate-500">
        <p>© 2026 ReachOut SMB. Built with Next.js, FastAPI, PostgreSQL & Gemini Flash.</p>
      </footer>
    </div>
  );
}
