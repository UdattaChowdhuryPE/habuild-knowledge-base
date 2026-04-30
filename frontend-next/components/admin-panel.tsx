"use client"

import { useState, useEffect, useRef } from "react"
import { cn } from "@/lib/utils"
import { getPolicies, createPolicy, deletePolicy, getDocuments, uploadDocument, deleteDocument, uploadEmployees, type Policy, type Document } from "@/lib/api"

type AdminTab = "policies" | "employees" | "documents"

const LOCATIONS = ["Bangalore", "Gurgaon", "Nagpur"]
const POLICY_CATEGORIES = ["Leave & Attendance", "Compensation & Benefits", "Compliance & Legal", "Code of Conduct", "Recruitment & Onboarding", "Performance & Development", "Health & Safety", "Remote Work", "Other"]
const DOC_CATEGORIES = ["Health Insurance", "Claims & Reimbursement", "Onboarding", "Payroll & Tax", "Compliance", "General"]

export function AdminPanel() {
  const [activeTab, setActiveTab] = useState<AdminTab>("policies")

  return (
    <div className="p-8">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4 rounded-xl bg-gradient-to-r from-slate-100 to-teal-50 p-6">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-700 text-2xl shadow-lg">⚙️</div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">HR Admin Panel</h1>
            <p className="text-slate-600">Manage policies, employees, and documents</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8 rounded-xl bg-slate-100 p-1.5">
          <div className="flex gap-1">
            {(["policies", "employees", "documents"] as AdminTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "flex-1 rounded-lg px-6 py-3 text-sm font-medium capitalize transition-all",
                  activeTab === tab ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
                )}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab === "policies" && <PoliciesTab />}
        {activeTab === "employees" && <EmployeesTab />}
        {activeTab === "documents" && <DocumentsTab />}
      </div>
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-4 flex items-center gap-3">
      <div className="h-6 w-1 rounded-full bg-teal-500" />
      <h2 className="text-lg font-semibold text-slate-800">{children}</h2>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return <div className="rounded-lg bg-sky-50 px-5 py-4 text-sky-700">{message}</div>
}

function LocationPills({ selected, onChange }: { selected: string[]; onChange: (locs: string[]) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {LOCATIONS.map((loc) => (
        <button
          key={loc}
          type="button"
          onClick={() => onChange(selected.includes(loc) ? selected.filter((l) => l !== loc) : [...selected, loc])}
          className={cn(
            "rounded-full px-4 py-2 text-sm font-medium transition-all",
            selected.includes(loc) ? "bg-teal-500 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          )}
        >
          {loc}
        </button>
      ))}
    </div>
  )
}

function PoliciesTab() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState(POLICY_CATEGORIES[0])
  const [content, setContent] = useState("")
  const [locations, setLocations] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    getPolicies().then((d) => setPolicies(d.policies)).catch(console.error).finally(() => setLoading(false))
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !content || locations.length === 0) { setError("Please fill all fields and select at least one location"); return }
    setError("")
    setSubmitting(true)
    try {
      await createPolicy({ title, category, content, locations })
      const d = await getPolicies()
      setPolicies(d.policies)
      setTitle(""); setContent(""); setLocations([])
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create policy")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deletePolicy(id)
      setPolicies((p) => p.filter((x) => x.id !== id))
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-8">
      <div>
        <SectionTitle>HR Policies</SectionTitle>
        {loading ? <p className="text-slate-500 text-sm">Loading…</p> : policies.length === 0 ? (
          <EmptyState message="No policies yet" />
        ) : (
          <div className="space-y-3">
            {policies.map((p) => (
              <div key={p.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-semibold text-slate-800">{p.title}</p>
                    <p className="text-sm text-slate-500 mt-0.5">{p.category} · {p.locations.join(", ")}</p>
                    <p className="text-sm text-slate-600 mt-2 line-clamp-2">{p.content}</p>
                  </div>
                  <button onClick={() => handleDelete(p.id)} className="text-rose-400 hover:text-rose-600 text-sm font-medium flex-shrink-0">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <SectionTitle>Add New Policy</SectionTitle>
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <form onSubmit={handleCreate} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Policy Title</label>
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter policy title"
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20" />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20">
                {POLICY_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Policy Content</label>
              <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Enter policy details…" rows={6}
                className="w-full resize-none rounded-lg border border-slate-200 px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20" />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Applicable Locations</label>
              <LocationPills selected={locations} onChange={setLocations} />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <button type="submit" disabled={submitting}
              className="flex items-center gap-2 rounded-lg bg-teal-600 px-6 py-3 font-medium text-white transition-colors hover:bg-teal-700 disabled:opacity-60">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {submitting ? "Creating…" : "Create Policy"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

function EmployeesTab() {
  const fileRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [location, setLocation] = useState(LOCATIONS[0])
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState("")

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const res = await uploadEmployees(file, location)
      setResult(`Uploaded ${res.count} employees successfully`)
      setFile(null)
      if (fileRef.current) fileRef.current.value = ""
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <SectionTitle>Employee Management</SectionTitle>
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="mb-2 text-slate-700">Upload an employee list (CSV or Excel) to update employees for specific locations.</p>
          <p className="text-sm text-slate-500"><span className="font-medium">Required columns:</span> Name, Email, Location, Role</p>
        </div>
      </div>

      <div>
        <SectionTitle>Upload Employee List</SectionTitle>
        <label className="block cursor-pointer rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 text-center transition-colors hover:border-teal-300 hover:bg-teal-50/30">
          <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-teal-100">
            <svg className="h-7 w-7 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          {file ? (
            <p className="font-medium text-teal-600">{file.name}</p>
          ) : (
            <>
              <p className="mb-2 text-slate-700"><span className="font-semibold text-teal-600">Click to upload</span> or drag and drop</p>
              <p className="text-sm text-slate-500">CSV, XLSX, XLS (max 200MB)</p>
            </>
          )}
        </label>

        {file && (
          <div className="mt-4 flex items-center gap-4">
            <select value={location} onChange={(e) => setLocation(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-800 focus:border-teal-500 focus:outline-none">
              {LOCATIONS.map((l) => <option key={l}>{l}</option>)}
            </select>
            <button onClick={handleUpload} disabled={uploading}
              className="rounded-lg bg-teal-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-60">
              {uploading ? "Uploading…" : "Upload Employees"}
            </button>
          </div>
        )}
        {result && <p className="mt-3 text-sm text-teal-700 font-medium">{result}</p>}
      </div>
    </div>
  )
}

function DocumentsTab() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [title, setTitle] = useState("")
  const [category, setCategory] = useState(DOC_CATEGORIES[0])
  const [locations, setLocations] = useState<string[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getDocuments().then((d) => setDocuments(d.documents)).catch(console.error).finally(() => setLoading(false))
  }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !file || locations.length === 0) { setError("Please fill all fields and select at least one location"); return }
    setError("")
    setSubmitting(true)
    try {
      await uploadDocument(file, title, category, locations)
      const d = await getDocuments()
      setDocuments(d.documents)
      setTitle(""); setLocations([]); setFile(null)
      if (fileRef.current) fileRef.current.value = ""
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      setDocuments((d) => d.filter((x) => x.id !== id))
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-8">
      <div>
        <SectionTitle>Document Management</SectionTitle>
        {loading ? <p className="text-slate-500 text-sm">Loading…</p> : documents.length === 0 ? (
          <EmptyState message="No documents uploaded yet" />
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
                <div>
                  <p className="font-semibold text-slate-800">📄 {doc.title}</p>
                  <p className="text-sm text-slate-500 mt-0.5">{doc.category} · {doc.locations.join(", ")}</p>
                </div>
                <div className="flex gap-3">
                  <a href={doc.file_url} target="_blank" rel="noreferrer" className="text-teal-600 hover:text-teal-700 text-sm font-medium">Download</a>
                  <button onClick={() => handleDelete(doc.id)} className="text-rose-400 hover:text-rose-600 text-sm font-medium">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <SectionTitle>Upload New Document</SectionTitle>
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <form onSubmit={handleUpload} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Document Title</label>
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter document title"
                className="w-full rounded-lg border border-slate-200 px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20" />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20">
                {DOC_CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Applicable Locations</label>
              <LocationPills selected={locations} onChange={setLocations} />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Choose File</label>
              <label className="block cursor-pointer rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 p-6 text-center transition-colors hover:border-teal-300 hover:bg-teal-50/30">
                <input ref={fileRef} type="file" accept=".pdf,.docx,.doc,.txt" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-teal-100">
                  <svg className="h-6 w-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                {file ? (
                  <p className="text-sm font-medium text-teal-600">{file.name}</p>
                ) : (
                  <>
                    <p className="mb-1 text-sm text-slate-700"><span className="font-semibold text-teal-600">Click to upload</span> or drag and drop</p>
                    <p className="text-xs text-slate-500">PDF, DOCX, DOC, TXT (max 200MB)</p>
                  </>
                )}
              </label>
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <button type="submit" disabled={submitting}
              className="flex items-center gap-2 rounded-lg bg-teal-600 px-6 py-3 font-medium text-white transition-colors hover:bg-teal-700 disabled:opacity-60">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              {submitting ? "Uploading…" : "Upload Document"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
