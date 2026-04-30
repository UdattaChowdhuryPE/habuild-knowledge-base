"use client"

import { useState, useEffect } from "react"
import { getDocuments, type Document } from "@/lib/api"

const CATEGORIES = ["All", "Health Insurance", "Leave Policy", "Employee Handbook", "Benefits Guide", "Compliance", "General", "Claims & Reimbursement", "Onboarding", "Payroll & Tax"]

const fileIcon = (fileName: string) => {
  if (fileName.endsWith(".pdf")) return "📕"
  if (fileName.endsWith(".docx") || fileName.endsWith(".doc")) return "📗"
  if (fileName.endsWith(".xlsx") || fileName.endsWith(".xls")) return "📙"
  return "📄"
}

interface DocumentsViewProps {
  location: string
}

export function DocumentsView({ location }: DocumentsViewProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")

  useEffect(() => {
    getDocuments(location)
      .then((d) => setDocuments(d.documents))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [location])

  const filtered = documents.filter((doc) => {
    const matchSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || doc.category.toLowerCase().includes(searchQuery.toLowerCase())
    const matchCat = selectedCategory === "All" || doc.category === selectedCategory
    return matchSearch && matchCat
  })

  return (
    <div className="p-8">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4 rounded-xl bg-gradient-to-r from-slate-100 to-teal-50 p-6">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-700 text-2xl shadow-lg">📄</div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">HR Documents</h1>
            <p className="text-slate-600">Browse and download company HR documents</p>
          </div>
        </div>

        {/* Search + Filter */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row">
          <div className="relative flex-1">
            <svg className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
              className="w-full rounded-lg border border-slate-200 bg-white py-3 pl-12 pr-4 text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 sm:w-56"
          >
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Content */}
        {loading ? (
          <p className="text-slate-500 text-sm">Loading documents…</p>
        ) : filtered.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
              <svg className="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-semibold text-slate-800">No documents found</h3>
            <p className="text-slate-500">Try adjusting your search or filter</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {filtered.map((doc) => (
              <div key={doc.id} className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-teal-200 hover:shadow-md">
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-teal-50 text-teal-600 transition-colors group-hover:bg-teal-100">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{doc.category}</span>
                </div>
                <h3 className="mb-2 font-semibold text-slate-800 group-hover:text-teal-700">{doc.title}</h3>
                <div className="mb-4 flex items-center gap-4 text-sm text-slate-500">
                  <span className="flex items-center gap-1">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {doc.created_at.split("T")[0]}
                  </span>
                  {doc.file_size && <span>{doc.file_size}</span>}
                </div>
                <a
                  href={doc.file_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-50 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-teal-50 hover:border-teal-200 hover:text-teal-700"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
