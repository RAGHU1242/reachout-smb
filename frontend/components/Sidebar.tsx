'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  MessageSquare,
  Flame,
  Users,
  ShoppingBag,
  Boxes,
  ClipboardList,
  Clock,
  BarChart3,
  BookOpen,
  Share2,
  Users2,
  Settings,
  Sparkles,
  Bot
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/conversations', label: 'Inbox', icon: MessageSquare, badge: 'Live' },
  { href: '/leads', label: 'Leads Pipeline', icon: Flame },
  { href: '/customers', label: 'Customers CRM', icon: Users },
  { href: '/products', label: 'Products', icon: ShoppingBag },
  { href: '/inventory', label: 'Inventory', icon: Boxes },
  { href: '/orders', label: 'Orders', icon: ClipboardList },
  { href: '/followups', label: 'Follow-ups', icon: Clock },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/knowledge', label: 'Knowledge Base', icon: BookOpen },
  { href: '/integrations', label: 'Integrations', icon: Share2 },
  { href: '/team', label: 'Team', icon: Users2 },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
          <Bot className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-tight leading-none flex items-center gap-1.5">
            ReachOut <span className="text-xs bg-indigo-500/20 text-indigo-400 font-semibold px-1.5 py-0.5 rounded">SMB</span>
          </h1>
          <p className="text-[11px] text-slate-400 mt-1 font-medium">AI Sales & Assistant</p>
        </div>
      </div>

      {/* Simulator Quick Action Banner */}
      <div className="px-3 pt-3">
        <Link
          href="/dev/simulator"
          className={cn(
            "flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 border",
            pathname === '/dev/simulator'
              ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white border-emerald-400/50 shadow-md shadow-emerald-900/30"
              : "bg-emerald-950/40 text-emerald-300 border-emerald-800/40 hover:bg-emerald-900/40"
          )}
        >
          <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span>Interactive Simulator</span>
        </Link>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              )}
            >
              <div className="flex items-center gap-3">
                <Icon className={cn("w-4 h-4", isActive ? "text-white" : "text-slate-400")} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Business Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs text-slate-300 font-medium">AI Active (Telugu, Hindi, EN)</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">Rani Fashions (Hyderabad)</p>
      </div>
    </aside>
  );
}
