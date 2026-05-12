-- Create employees table for HR-uploaded employee directory
-- No FK to auth.users so bulk CSV imports work without Supabase Auth accounts
create table if not exists public.employees (
  id uuid primary key default gen_random_uuid(),
  name text,
  email text,
  location text,
  role text default 'employee',
  created_at timestamptz default now()
);

-- Enable Row Level Security
alter table public.employees enable row level security;

-- RLS Policies for employees (service role manages, authenticated users can read)
-- Drop first so migration is idempotent (safe to re-run)
drop policy if exists "employees_authenticated_can_read" on public.employees;
drop policy if exists "employees_service_can_manage" on public.employees;

create policy "employees_authenticated_can_read" on public.employees
  for select using (auth.role() = 'authenticated');

create policy "employees_service_can_manage" on public.employees
  for all using (auth.role() = 'service_role');
