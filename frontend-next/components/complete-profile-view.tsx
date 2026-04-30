"use client"

import { useState } from "react"
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

const LOCATIONS = ["Bangalore", "Gurgaon", "Nagpur"]

export function CompleteProfileView({ session, onProfileComplete }: CompleteProfileViewProps) {
  const [location, setLocation] = useState(LOCATIONS[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const userName = session.user?.user_metadata?.full_name || session.user?.email?.split("@")[0] || "User"

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const profile = await completeProfile(location, session.access_token)
      onProfileComplete(profile)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to complete profile")
    } finally {
      setLoading(false)
    }
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

        {/* Form */}
        <div className="w-96 flex flex-col justify-center">
          <h2 className="mb-2 text-3xl font-bold text-slate-800">Welcome, {userName}!</h2>
          <p className="mb-8 text-slate-500">Please select your office location to continue</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Office Location</label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              >
                {LOCATIONS.map((loc) => (
                  <option key={loc} value={loc}>
                    {loc}
                  </option>
                ))}
              </select>
            </div>

            {error && <p className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-600 to-teal-500 px-6 py-3.5 font-medium text-white shadow-lg shadow-teal-500/25 transition-all hover:from-teal-700 hover:to-teal-600 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Saving…" : "Continue"}
              {!loading && (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
