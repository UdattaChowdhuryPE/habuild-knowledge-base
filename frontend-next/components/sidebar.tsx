"use client"

import { cn } from "@/lib/utils"

interface User {
  id: string
  name: string
  email: string
  location: string
  role: string
}

interface SidebarProps {
  currentPage: "app" | "admin" | "documents"
  onPageChange: (page: "app" | "admin" | "documents") => void
  isSignedIn: boolean
  user: User | null
  onSignOut: () => void
}

const navItems = [
  {
    id: "app" as const,
    label: "App",
    path: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  {
    id: "admin" as const,
    label: "Admin",
    path: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
  },
  {
    id: "documents" as const,
    label: "Documents",
    path: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  },
]

export function Sidebar({ currentPage, onPageChange, isSignedIn, user, onSignOut }: SidebarProps) {
  const initials = user?.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) ?? "?"

  return (
    <aside className="flex w-64 flex-shrink-0 flex-col bg-gradient-to-b from-slate-800 to-slate-900">
      {/* Nav */}
      <nav className="flex-1 p-4 pt-6">
        <div className="space-y-1">
          {navItems
            .filter((item) => item.id !== "admin" || user?.role === "hr")
            .map((item) => (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition-all",
                currentPage === item.id
                  ? "bg-teal-600/20 text-teal-400"
                  : "text-slate-400 hover:bg-slate-700/50 hover:text-slate-200"
              )}
            >
              <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.path} />
              </svg>
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Brand */}
      <div className="border-t border-slate-700/50 p-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏃</span>
          <div>
            <div className="font-semibold text-teal-400">Habuild</div>
            <div className="text-xs text-slate-500 uppercase tracking-wider">HR Portal</div>
          </div>
        </div>
      </div>

      {/* User section */}
      {isSignedIn && user ? (
        <div className="border-t border-slate-700/50 p-4 space-y-2">
          <div className="rounded-lg bg-slate-700/30 p-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-teal-700 text-sm font-bold text-white">
                {initials}
              </div>
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium text-slate-200 text-sm">{user.name}</div>
                <div className="flex items-center gap-1 text-xs text-slate-400">
                  <span className="text-yellow-400">★</span>
                  {user.role.toUpperCase()}
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={onSignOut}
            className="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm text-rose-400 transition-colors hover:bg-rose-500/10"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      ) : (
        <div className="border-t border-slate-700/50 p-4">
          <div className="rounded-lg bg-teal-600/10 p-3 text-center text-sm text-teal-400">
            Sign in to get started
          </div>
        </div>
      )}
    </aside>
  )
}
