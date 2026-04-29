-- Enable pgvector extension
create extension if not exists vector;

-- Create profiles table (replaces employees for auth)
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  email text unique,
  location text,  -- "Bangalore" | "Gurgaon" | "Nagpur"
  role text default 'employee' check (role in ('employee', 'hr')),
  created_at timestamptz default now()
);

-- Create chunks table (unified RAG index)
create table if not exists public.chunks (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null,
  source_type text not null check (source_type in ('policy', 'document')),
  source_title text,
  content text not null,
  embedding vector(1024),  -- voyage-3-lite dimension
  locations text[],
  created_at timestamptz default now()
);

-- Create index on embeddings for fast cosine similarity search
create index if not exists chunks_embedding_idx on public.chunks
  using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Create conversations table
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  location text not null,
  created_at timestamptz default now()
);

-- Create messages table
create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

-- Enable Row Level Security
alter table public.profiles enable row level security;
alter table public.chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;

-- RLS Policies for profiles
create policy "profiles_users_can_read_own" on public.profiles
  for select using (auth.uid() = id);

create policy "profiles_service_can_manage" on public.profiles
  for all using (auth.role() = 'service_role');

-- RLS Policies for chunks (readable by all authenticated users, writable by service role)
create policy "chunks_authenticated_can_read" on public.chunks
  for select using (auth.role() = 'authenticated');

create policy "chunks_service_can_manage" on public.chunks
  for all using (auth.role() = 'service_role');

-- RLS Policies for conversations
create policy "conversations_users_can_read_own" on public.conversations
  for select using (auth.uid() = user_id);

create policy "conversations_users_can_create" on public.conversations
  for insert with check (auth.uid() = user_id);

create policy "conversations_service_can_manage" on public.conversations
  for all using (auth.role() = 'service_role');

-- RLS Policies for messages
create policy "messages_users_can_read_own_conversations" on public.messages
  for select using (
    conversation_id in (
      select id from public.conversations where user_id = auth.uid()
    )
  );

create policy "messages_users_can_create_own_conversations" on public.messages
  for insert with check (
    conversation_id in (
      select id from public.conversations where user_id = auth.uid()
    )
  );

create policy "messages_service_can_manage" on public.messages
  for all using (auth.role() = 'service_role');

-- Helper RPC function for vector search with location filtering
create or replace function public.match_chunks_by_location(
  query_embedding vector(1024),
  match_count int,
  location_filter text
)
returns table (
  id uuid,
  source_id uuid,
  source_type text,
  source_title text,
  content text,
  locations text[],
  similarity float
) as $$
  select
    chunks.id,
    chunks.source_id,
    chunks.source_type,
    chunks.source_title,
    chunks.content,
    chunks.locations,
    1 - (chunks.embedding <=> query_embedding) as similarity
  from chunks
  where chunks.locations @> array[location_filter]
  order by chunks.embedding <=> query_embedding
  limit match_count;
$$ language sql stable;
