const BASE = "/api"

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

export async function completeProfile(location: string, token: string) {
  const res = await authFetch(
    `${BASE}/auth/complete-profile`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location }),
    },
    token
  )
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ id: string; name: string; email: string; location: string; role: string }>
}

export async function startConversation(location: string, token: string) {
  const res = await authFetch(`${BASE}/chat/start?location=${encodeURIComponent(location)}`, { method: "POST" }, token)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ conversation_id: string }>
}

export async function* streamMessage(question: string, conversationId: string, location: string, token: string) {
  const res = await authFetch(
    `${BASE}/chat/message`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversation_id: conversationId, location }),
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
        const token = line.slice(6)
        if (token === "[DONE]") return
        if (!token.startsWith("[ERROR]")) yield token
      }
    }
  }
}

export async function getDocuments(location?: string) {
  const url = location ? `${BASE}/documents/?location=${encodeURIComponent(location)}` : `${BASE}/documents/`
  const res = await fetch(url)
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
