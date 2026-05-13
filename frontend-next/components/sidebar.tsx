"use client"

import { cn } from "@/lib/utils"

interface User {
  id: string
  name: string
  email: string
  location: string
  role: string
}

interface Conversation {
  id: string
  title: string
  created_at: string
}

interface SidebarProps {
  currentPage: "app" | "admin"
  onPageChange: (page: "app" | "admin") => void
  isSignedIn: boolean
  user: User | null
  onSignOut: () => void
  conversations: Conversation[]
  activeConversationId: string | null
  onNewChat: () => void
  onSelectConversation: (id: string) => void
}

export function Sidebar({
  currentPage,
  onPageChange,
  isSignedIn,
  user,
  onSignOut,
  conversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
}: SidebarProps) {
  const initials = user?.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) ?? "?"

  return (
    <aside className="flex w-64 flex-shrink-0 flex-col bg-gradient-to-b from-slate-800 to-slate-900 overflow-hidden">
      {/* Header with brand and new chat button */}
      <div className="border-b border-slate-700/50 p-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🏃</span>
          <div>
            <div className="font-semibold text-teal-400 text-sm">Habuild</div>
            <div className="text-xs text-slate-500 uppercase tracking-wider">HR Portal</div>
          </div>
        </div>
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium bg-teal-600/20 text-teal-400 hover:bg-teal-600/30 transition-colors"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Welcome greeting */}
      {isSignedIn && user && (
        <div className="border-b border-slate-700/50 px-4 py-4">
          <div className="text-sm">
            <p className="text-slate-400">Welcome back,</p>
            <p className="text-lg font-semibold text-white mt-1">{user.name} 👋</p>
          </div>
        </div>
      )}

      {/* Conversations list */}
      {isSignedIn && user && (
        <div className="flex-1 flex flex-col min-h-0 border-b border-slate-700/50 px-2 py-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 mb-2">Recent</h3>
          <div className="flex-1 overflow-y-auto space-y-1 min-h-0">
            {conversations.length > 0 ? (
              conversations.map((convo) => (
                <button
                  key={convo.id}
                  onClick={() => onSelectConversation(convo.id)}
                  className={cn(
                    "flex w-full items-start gap-2 rounded-lg px-3 py-2 text-left text-xs transition-colors group truncate",
                    activeConversationId === convo.id
                      ? "bg-slate-700/50 text-teal-400"
                      : "text-slate-400 hover:bg-slate-700/30 hover:text-slate-200"
                  )}
                  title={convo.title}
                >
                  <span className="flex-shrink-0 mt-0.5">•</span>
                  <span className="truncate text-xs">{convo.title}</span>
                </button>
              ))
            ) : (
              <p className="px-3 py-2 text-xs text-slate-500">No conversations yet</p>
            )}
          </div>
        </div>
      )}

      {/* Admin link (HR only) */}
      {isSignedIn && user?.role === "hr" && (
        <div className="border-b border-slate-700/50 px-2 py-3">
          <button
            onClick={() => onPageChange("admin")}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-all",
              currentPage === "admin"
                ? "bg-teal-600/20 text-teal-400"
                : "text-slate-400 hover:bg-slate-700/50 hover:text-slate-200"
            )}
          >
            <svg className="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Admin
          </button>
        </div>
      )}

      {/* User section footer */}
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
