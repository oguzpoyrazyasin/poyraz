create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
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
  billing_interval text not null default 'monthly' check (billing_interval in ('monthly','annual')),
  status text not null check (status in ('trialing','active','past_due','cancelled','expired')),
  trial_started_at timestamptz,
  trial_ends_at timestamptz,
  current_period_end timestamptz,
  provider text not null default 'paytr',
  provider_customer_token text,
  provider_card_token text,
  provider_order_id text unique,
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

create table if not exists public.payment_events (
  id bigint generated always as identity primary key,
  merchant_oid text not null,
  parent_id uuid references public.profiles(id) on delete set null,
  status text not null,
  amount_minor bigint,
  provider text not null default 'paytr',
  raw_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(provider, merchant_oid, status)
);

alter table public.profiles enable row level security;
alter table public.child_profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.activity_events enable row level security;
alter table public.payment_events enable row level security;

create policy "parents read own profile" on public.profiles for select using (auth.uid() = id);
create policy "parents update own profile" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);
create policy "parents manage own children" on public.child_profiles for all using (auth.uid() = parent_id) with check (auth.uid() = parent_id);
create policy "parents read own subscription" on public.subscriptions for select using (auth.uid() = parent_id);
create policy "parents manage own activity events" on public.activity_events for all using (auth.uid() = parent_id) with check (auth.uid() = parent_id);

create or replace function public.handle_new_parent()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
declare
  selected_plan text;
begin
  selected_plan := case
    when new.raw_user_meta_data ->> 'plan_id' in ('starter','family','premium')
      then new.raw_user_meta_data ->> 'plan_id'
    else 'family'
  end;

  insert into public.profiles (id, email, full_name, role)
  values (
    new.id,
    coalesce(new.email, ''),
    nullif(new.raw_user_meta_data ->> 'full_name', ''),
    'parent'
  );

  insert into public.subscriptions (
    parent_id, plan_id, status, trial_started_at, trial_ends_at
  )
  values (
    new.id, selected_plan, 'trialing', now(), now() + interval '3 days'
  );

  return new;
end;
$$;

drop trigger if exists on_auth_parent_created on auth.users;
create trigger on_auth_parent_created
  after insert on auth.users
  for each row execute procedure public.handle_new_parent();
