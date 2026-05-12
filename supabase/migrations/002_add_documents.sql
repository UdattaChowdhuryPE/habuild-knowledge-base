-- Create documents table
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  category text,
  file_name text,
  file_url text,
  locations text[],
  created_at timestamptz default now()
);

-- Enable Row Level Security
alter table public.documents enable row level security;

-- RLS Policies for documents (service role manages, authenticated users can read)
create policy "documents_authenticated_can_read" on public.documents
  for select using (auth.role() = 'authenticated');

create policy "documents_service_can_manage" on public.documents
  for all using (auth.role() = 'service_role');
