create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key,
  email text not null,
  full_name text,
  role text not null default 'parent' check (role in ('parent','admin')),
  created_at timestamptz not null default now()
);

create table if not exists public.child_profiles (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid not null references public.profiles(id) on delete cascade,
  nickname text not null,
  age smallint not null check (age between 2 and 6),
  goals text[] not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid not null references public.profiles(id) on delete cascade,
  plan_id text not null check (plan_id in ('starter','family','premium')),
  status text not null check (status in ('trialing','active','past_due','cancelled','expired')),
  trial_started_at timestamptz,
  trial_ends_at timestamptz,
  current_period_end timestamptz,
  provider text not null default 'paytr',
  provider_customer_token text,
  provider_card_token text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.activity_events (
  id bigint generated always as identity primary key,
  parent_id uuid not null references public.profiles(id) on delete cascade,
  child_id uuid not null references public.child_profiles(id) on delete cascade,
  activity_key text not null,
  category text not null,
  completed_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.child_profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.activity_events enable row level security;

create policy "parents read own profile" on public.profiles for select using (auth.uid() = id);
create policy "parents manage own children" on public.child_profiles for all using (auth.uid() = parent_id) with check (auth.uid() = parent_id);
create policy "parents read own subscription" on public.subscriptions for select using (auth.uid() = parent_id);
create policy "parents manage own activity events" on public.activity_events for all using (auth.uid() = parent_id) with check (auth.uid() = parent_id);
