"use client"

import { useState } from "react"
import { verifyEmployee } from "@/lib/api"

interface User {
  id: string
  name: string
  email: string
  location: string
  role: string
}

interface SignInViewProps {
  onSignIn: (user: User) => void
}

const LOCATIONS = ["Bangalore", "Gurgaon", "Nagpur"]

export function SignInView({ onSignIn }: SignInViewProps) {
  const [email, setEmail] = useState("")
  const [location, setLocation] = useState(LOCATIONS[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.includes("@habuild.in")) {
      setError("Please enter a valid @habuild.in email address")
      return
    }
    setError("")
    setLoading(true)
    try {
      const profile = await verifyEmployee(email)
      onSignIn({ ...profile, location })
    } catch {
      setError("Sign in failed. Please check your email and try again.")
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
          <h2 className="mb-2 text-3xl font-bold text-slate-800">Sign In</h2>
          <p className="mb-8 text-slate-500">Use your Habuild email address to access HR resources</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@habuild.in"
                required
                className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Office Location</label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              >
                {LOCATIONS.map((loc) => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            {error && (
              <p className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-600 to-teal-500 px-6 py-3.5 font-medium text-white shadow-lg shadow-teal-500/25 transition-all hover:from-teal-700 hover:to-teal-600 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in…" : "Sign In"}
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
