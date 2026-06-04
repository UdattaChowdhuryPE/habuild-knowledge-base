'use client'
import React from 'react'

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  State
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Log error info to console with structured format
    console.error('[ErrorBoundary]', {
      error: error.message,
      stack: error.stack,
      componentStack: info.componentStack,
    })
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="p-8 text-center text-gray-600">
          <p className="text-lg font-medium">Something went wrong.</p>
          <p className="text-sm mt-2">Please refresh the page or contact support.</p>
        </div>
      )
    }
    return this.props.children
  }
}
