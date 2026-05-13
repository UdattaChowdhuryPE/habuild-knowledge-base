const BASE = "/api"
const BACKEND_DIRECT = typeof window !== "undefined"
  ? (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000")
  : "http://localhost:8000"

async function authFetch(url: string, options: RequestInit = {}, token?: string): Promise<Response> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  return fetch(url, { ...options, headers })
}

export async function getMyProfile(token: string) {
  const res = await authFetch(`${BASE}/auth/me`, {}, token)
  if (res.status === 404) return null
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ id: string; name: string; email: string; location: string; role: string }>
}

export async function completeProfile(token: string) {
  const res = await authFetch(
    `${BASE}/auth/complete-profile`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    },
    token
  )
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ id: string; name: string; email: string; location: string; role: string }>
}

export async function startConversation(token: string) {
  const res = await authFetch(`${BASE}/chat/start`, { method: "POST" }, token)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ conversation_id: string }>
}

export async function* streamMessage(question: string, conversationId: string, token: string) {
  const res = await authFetch(
    `${BACKEND_DIRECT}/chat/message`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversation_id: conversationId }),
    },
    token
  )
  if (!res.ok || !res.body) throw new Error("Stream failed")
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() ?? ""
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const raw = line.slice(6)
        if (raw === "[DONE]") return
        if (!raw.startsWith("[ERROR]")) yield raw.replace(/\\n/g, "\n")
      }
    }
  }
}

export async function getDocuments(location?: string, token?: string) {
  const url = location ? `${BASE}/documents?location=${encodeURIComponent(location)}` : `${BASE}/documents`
  const res = await authFetch(url, {}, token)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ documents: Document[] }>
}

export async function uploadDocument(file: File, title: string, category: string, locations: string[], token: string) {
  const form = new FormData()
  form.append("file", file)
  form.append("title", title)
  form.append("category", category)
  locations.forEach((l) => form.append("locations", l))
  const res = await authFetch(`${BASE}/documents/upload`, { method: "POST", body: form }, token)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deleteDocument(id: string, token: string) {
  const res = await authFetch(`${BASE}/documents/${id}`, { method: "DELETE" }, token)
  if (!res.ok) throw new Error(await res.text())
}

export async function uploadEmployees(file: File, token: string) {
  const form = new FormData()
  form.append("file", file)
  const res = await authFetch(`${BASE}/employees/upload`, { method: "POST", body: form }, token)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ status: string; count: number }>
}

export interface Document {
  id: string
  title: string
  category: string
  file_url: string
  file_name: string
  file_size?: string
  locations: string[]
  created_at: string
}
