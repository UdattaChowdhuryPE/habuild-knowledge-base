"use client"

import { useState } from "react"
import { supabase } from "@/lib/supabase"

interface SignInViewProps {
  error?: string
}

export function SignInView({ error }: SignInViewProps) {
  const [loading, setLoading] = useState(false)

  const handleSignInWithGoogle = async () => {
    setLoading(true)
    try {
      await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: window.location.origin,
          queryParams: {
            hd: "habuild.in",
          },
        },
      })
    } catch (e) {
      console.error("OAuth error:", e)
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

        {/* Sign-in */}
        <div className="w-96 flex flex-col justify-center">
          <h2 className="mb-2 text-3xl font-bold text-slate-800">Sign In</h2>
          <p className="mb-8 text-slate-500">Use your Habuild Google account to access HR resources</p>

          <div className="space-y-5">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">{error}</div>
            )}

            <button
              onClick={handleSignInWithGoogle}
              disabled={loading}
              className="flex w-full items-center justify-center gap-3 rounded-lg border-2 border-slate-300 bg-white px-6 py-3.5 font-medium text-slate-700 shadow-sm transition-all hover:border-slate-400 hover:bg-slate-50 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path fill="#1f2937" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#1f2937" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#1f2937" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="#1f2937" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              {loading ? "Signing in…" : "Continue with Google"}
            </button>

            <p className="text-center text-xs text-slate-500 mt-6">
              You will be asked to sign in with your Habuild Google Workspace account
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
