'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Bell, Store, ShieldCheck, LogOut, ChevronDown, UserCircle } from 'lucide-react';

export function Navbar() {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
      {/* Active Business Switcher */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-sm font-semibold text-slate-800">
          <Store className="w-4 h-4 text-indigo-600" />
          <span>Rani Fashions</span>
          <span className="text-[10px] bg-indigo-100 text-indigo-700 font-bold px-1.5 py-0.5 rounded">
            HYDERABAD
          </span>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Meta Verified Cloud API Ready</span>
        </div>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-4">
        {/* Simulator Link */}
        <Link
          href="/dev/simulator"
          className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 rounded-lg transition-colors"
        >
          <span>Dev Simulator</span>
        </Link>

        {/* Notifications */}
        <button
          className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-600" />
        </button>

        {/* User profile dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="flex items-center gap-2.5 p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-left"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white font-bold flex items-center justify-center text-xs shadow-sm">
              RF
            </div>
            <div className="hidden md:block">
              <p className="text-xs font-semibold text-slate-800 leading-tight">Raghu (Owner)</p>
              <p className="text-[11px] text-slate-500">demo@reachoutsmb.com</p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl py-1 z-50">
              <Link
                href="/settings"
                className="flex items-center gap-2 px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                onClick={() => setShowMenu(false)}
              >
                <UserCircle className="w-4 h-4 text-slate-400" />
                <span>Account & Settings</span>
              </Link>
              <Link
                href="/login"
                className="flex items-center gap-2 px-4 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50"
                onClick={() => setShowMenu(false)}
              >
                <LogOut className="w-4 h-4 text-rose-500" />
                <span>Sign Out</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
