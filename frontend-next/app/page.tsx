"use client"

import { useState, useRef, useEffect } from "react"
import { Session } from "@supabase/supabase-js"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Sidebar } from "@/components/sidebar"
import { SignInView } from "@/components/sign-in-view"
import { CompleteProfileView } from "@/components/complete-profile-view"
import { AdminPanel } from "@/components/admin-panel"
import { DocumentsView } from "@/components/documents-view"
import { startConversation, streamMessage, getMyProfile } from "@/lib/api"
import { supabase } from "@/lib/supabase"

type AuthState = "loading" | "unauthenticated" | "needs-profile" | "authenticated"

interface User {
  id: string
  name: string
  email: string
  location: string
  role: string
}

interface Message {
  role: "user" | "assistant"
  content: string
}

export default function HabuildHRPortal() {
  const [authState, setAuthState] = useState<AuthState>("loading")
  const [session, setSession] = useState<Session | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [authError, setAuthError] = useState("")

  const [currentPage, setCurrentPage] = useState<"app" | "admin" | "documents">("app")
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    setAuthState("loading")

    const { data: { session: existingSession } } = await supabase.auth.getSession()
    await handleSession(existingSession)

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, newSession) => {
      handleSession(newSession)
    })

    return () => subscription.unsubscribe()
  }

  const handleSession = async (session: Session | null) => {
    if (!session) {
      setAuthState("unauthenticated")
      setSession(null)
      setUser(null)
      return
    }

    const email = session.user?.email ?? ""
    const isAllowed = email.endsWith("@habuild.in") || email.endsWith(".habuild@gmail.com")
    if (!isAllowed) {
      await supabase.auth.signOut()
      setAuthError("Only @habuild.in or .habuild@gmail.com accounts are allowed")
      setAuthState("unauthenticated")
      setSession(null)
      setUser(null)
      return
    }

    setSession(session)
    setAuthError("")

    try {
      const profile = await getMyProfile(session.access_token)

      if (!profile || !profile.location) {
        setAuthState("needs-profile")
        setUser(null)
      } else {
        setUser(profile)
        setAuthState("authenticated")
      }
    } catch (error) {
      console.error("Profile fetch error:", error)
      const errorMsg = error instanceof Error ? error.message : String(error)
      if (errorMsg.includes("Invalid or expired token")) {
        await supabase.auth.signOut()
        setAuthState("unauthenticated")
        setSession(null)
        setUser(null)
      } else {
        setAuthState("needs-profile")
      }
    }
  }

  const handleProfileComplete = (completedUser: User) => {
    setUser(completedUser)
    setAuthState("authenticated")
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setSession(null)
    setAuthState("unauthenticated")
    setConversationId(null)
    setMessages([])
    setCurrentPage("app")
  }

  const ensureConversation = async (): Promise<string> => {
    if (conversationId) return conversationId
    const { conversation_id } = await startConversation(session!.access_token)
    setConversationId(conversation_id)
    return conversation_id
  }

  const handleSend = async () => {
    if (!input.trim() || streaming || !user || !session) return
    const question = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: question }])
    setStreaming(true)

    try {
      const convId = await ensureConversation()
      setMessages((prev) => [...prev, { role: "assistant", content: "" }])
      for await (const token of streamMessage(question, convId, session.access_token)) {
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            role: "assistant",
            content: updated[updated.length - 1].content + token,
          }
          return updated
        })
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${e instanceof Error ? e.message : "Unknown error"}` }])
    } finally {
      setStreaming(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (authState === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 text-5xl">🏃</div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        isSignedIn={authState === "authenticated"}
        user={user}
        onSignOut={handleSignOut}
      />

      <main className="flex-1 overflow-hidden">
        {authState === "unauthenticated" && <SignInView error={authError} />}

        {authState === "needs-profile" && session && <CompleteProfileView session={session} onProfileComplete={handleProfileComplete} />}

        {authState === "authenticated" && user && currentPage === "app" && (
          <div className="flex flex-col h-full p-8">
            <div className="mx-auto w-full max-w-4xl flex flex-col flex-1 min-h-0">
              {/* Welcome card */}
              <div className="rounded-xl bg-gradient-to-br from-slate-800 via-slate-700 to-teal-800 p-8 text-center text-white mb-6">
                <div className="mb-4 text-5xl">🏃</div>
                <h1 className="mb-3 text-3xl font-bold">Welcome back, {user.name}!</h1>
                <p className="text-slate-300">Ask me anything about HR policies, leave, benefits, compliance, and more.</p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {["Leave Policies", "Benefits", "Compliance", "Onboarding"].map((tag) => (
                    <span key={tag} className="rounded-full bg-white/10 px-4 py-2 text-sm backdrop-blur-sm hover:bg-white/20 cursor-default">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Messages */}
              {messages.length > 0 && (
                <div className="flex-1 space-y-4 mb-6 overflow-y-auto min-h-0">
                  {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div
                        className={`max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                          msg.role === "user"
                            ? "bg-teal-600 text-white"
                            : "bg-white border border-slate-200 text-slate-800 shadow-sm"
                        }`}
                      >
                        {msg.role === "assistant" ? (
                          msg.content ? (
                            <div className="prose prose-sm prose-slate max-w-none">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  table: ({ node, ...props }) => (
                                    <div className="overflow-x-auto my-2">
                                      <table className="border-collapse w-full text-xs" {...props} />
                                    </div>
                                  ),
                                  th: ({ node, ...props }) => (
                                    <th className="border border-slate-300 bg-slate-100 px-3 py-1.5 text-left font-semibold" {...props} />
                                  ),
                                  td: ({ node, ...props }) => (
                                    <td className="border border-slate-300 px-3 py-1.5" {...props} />
                                  ),
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          ) : streaming ? (
                            <span className="flex gap-1">
                              <span className="animate-bounce">•</span>
                              <span className="animate-bounce [animation-delay:0.1s]">•</span>
                              <span className="animate-bounce [animation-delay:0.2s]">•</span>
                            </span>
                          ) : ""
                        ) : (
                          msg.content
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}

              {/* Chat input */}
              <div className="relative mt-auto">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question about HR policies..."
                  rows={1}
                  disabled={streaming}
                  className="w-full rounded-xl border border-slate-200 bg-white px-5 py-4 pr-14 text-slate-800 shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 resize-none disabled:opacity-60"
                />
                <button
                  onClick={handleSend}
                  disabled={streaming || !input.trim()}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg bg-teal-600 p-2 text-white transition-colors hover:bg-teal-700 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {authState === "authenticated" && user?.role === "hr" && currentPage === "admin" && <AdminPanel token={session?.access_token} />}
        {authState === "authenticated" && user && currentPage === "documents" && <DocumentsView location={user.location} token={session?.access_token} />}
      </main>
    </div>
  )
}
