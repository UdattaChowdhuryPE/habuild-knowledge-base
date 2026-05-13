"use client"

import { useEffect, useState } from "react"
import { Session } from "@supabase/supabase-js"
import { completeProfile } from "@/lib/api"

interface User {
  id: string
  name: string
  email: string
  location: string
  role: string
}

interface CompleteProfileViewProps {
  session: Session
  onProfileComplete: (user: User) => void
}

export function CompleteProfileView({ session, onProfileComplete }: CompleteProfileViewProps) {
  const [error, setError] = useState("")

  const userName = session.user?.user_metadata?.full_name || session.user?.email?.split("@")[0] || "User"

  useEffect(() => {
    const initializeProfile = async () => {
      setError("")
      try {
        const profile = await completeProfile(session.access_token)
        onProfileComplete(profile)
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to complete profile")
      }
    }
    initializeProfile()
  }, [session.access_token, onProfileComplete])

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <div className="flex w-full max-w-5xl gap-12">
          {/* Hero */}
          <div className="flex-1 overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 via-slate-700 to-teal-800 p-10">
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-6 text-6xl">🏃</div>
              <h1 className="mb-4 text-4xl font-bold text-white">Your HR Companion</h1>
              <p className="mb-8 max-w-md text-lg text-slate-300">
                Get instant answers to all your HR policy questions — leave, benefits, compliance, and more.
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {["Leave Policies", "Benefits", "Compliance", "Onboarding"].map((tag) => (
                  <span key={tag} className="rounded-full bg-white/10 px-5 py-2.5 text-sm font-medium text-white backdrop-blur-sm hover:bg-white/20">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Error */}
          <div className="w-96 flex flex-col justify-center">
            <h2 className="mb-2 text-3xl font-bold text-slate-800">Setup Failed</h2>
            <p className="mb-6 text-red-600 text-sm rounded-lg bg-red-50 border border-red-200 px-4 py-3">{error}</p>
            <p className="text-slate-600">Please refresh the page to try again, or contact HR for assistance.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="flex w-full max-w-5xl gap-12">
        {/* Hero */}
        <div className="flex-1 overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 via-slate-700 to-teal-800 p-10">
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-6 text-6xl">🏃</div>
            <h1 className="mb-4 text-4xl font-bold text-white">Your HR Companion</h1>
            <p className="mb-8 max-w-md text-lg text-slate-300">
              Get instant answers to all your HR policy questions — leave, benefits, compliance, and more.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {["Leave Policies", "Benefits", "Compliance", "Onboarding"].map((tag) => (
                <span key={tag} className="rounded-full bg-white/10 px-5 py-2.5 text-sm font-medium text-white backdrop-blur-sm hover:bg-white/20">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Loading */}
        <div className="w-96 flex flex-col justify-center items-center gap-6">
          <h2 className="text-3xl font-bold text-slate-800">Welcome, {userName}!</h2>
          <div className="flex flex-col items-center gap-3">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-teal-500"></div>
            <p className="text-slate-600">Setting up your profile…</p>
          </div>
        </div>
      </div>
    </div>
  )
}
