-- Phiversity schema for Supabase (Postgres).
-- Run once in the Supabase SQL editor (Dashboard -> SQL -> New query).
-- The backend talks to these tables with the service-role key, which
-- bypasses Row Level Security; the policies below protect any direct
-- client access (the frontend should only ever use the anon key for
-- Supabase Auth itself, never for data).

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- users
-- Mirror of auth.users (Supabase Auth owns credentials and passwords;
-- this table only carries the id/email pair the app needs).
create table if not exists public.users (
    id          uuid primary key,
    email       text not null default '',
    created_at  timestamptz not null default now()
);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.users (id, email, created_at)
    values (new.id, new.email, new.created_at)
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- ----------------------------------------------------------------- jobs
-- Spec columns (id, user_id, status, question, created_at, updated_at,
-- error_message) plus the render progress fields the app streams.
create table if not exists public.jobs (
    id            text primary key,
    user_id       uuid references public.users(id) on delete set null,
    status        text not null default 'queued'
                  check (status in ('queued', 'running', 'done', 'error')),
    stage         text not null default '-',
    progress      integer not null default 0 check (progress between 0 and 100),
    title         text not null default '',
    question      text not null default '',
    topic         text not null default '',
    video         text not null default '',
    error_message text not null default '',
    logs          jsonb not null default '[]',
    payload       jsonb not null default '{}',
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists jobs_touch_updated_at on public.jobs;
create trigger jobs_touch_updated_at
    before update on public.jobs
    for each row execute function public.touch_updated_at();

create index if not exists jobs_user_idx     on public.jobs (user_id);
create index if not exists jobs_created_idx  on public.jobs (created_at desc);
create index if not exists jobs_status_idx   on public.jobs (status);

-- --------------------------------------------------------------- videos
create table if not exists public.videos (
    id            uuid primary key default gen_random_uuid(),
    job_id        text not null references public.jobs(id) on delete cascade,
    video_url     text not null default '',
    thumbnail_url text not null default '',
    duration      real not null default 0,
    created_at    timestamptz not null default now()
);

create index if not exists videos_job_idx     on public.videos (job_id);
create index if not exists videos_created_idx on public.videos (created_at desc);

-- ---------------------------------------------------------------- chats
-- Saved chat threads (backend-only access via the service key).
create table if not exists public.chats (
    id       text primary key,
    title    text not null default '',
    modified timestamptz not null default now(),
    messages jsonb not null default '[]'
);

-- ------------------------------------------------------------- lectures
-- Index of generated lectures; video points at the Cloudinary copy.
create table if not exists public.lectures (
    slug              text primary key,
    title             text not null default '',
    question          text,
    format            text,
    preset            text,
    segments          integer not null default 0,
    narration_seconds real not null default 0,
    modified          timestamptz not null default now(),
    video             text not null default ''
);

create index if not exists lectures_modified_idx on public.lectures (modified desc);

-- ------------------------------------------------------------------ rls
alter table public.users    enable row level security;
alter table public.jobs     enable row level security;
alter table public.videos   enable row level security;
alter table public.chats    enable row level security;
alter table public.lectures enable row level security;

-- users: read your own row
drop policy if exists "users_select_own" on public.users;
create policy "users_select_own" on public.users
    for select using (auth.uid() = id);

-- jobs: users see and manage their own jobs
drop policy if exists "jobs_select_own" on public.jobs;
create policy "jobs_select_own" on public.jobs
    for select using (auth.uid() = user_id);
drop policy if exists "jobs_insert_own" on public.jobs;
create policy "jobs_insert_own" on public.jobs
    for insert with check (user_id is null or auth.uid() = user_id);
drop policy if exists "jobs_update_own" on public.jobs;
create policy "jobs_update_own" on public.jobs
    for update using (auth.uid() = user_id);

-- videos: visible through the owning job
drop policy if exists "videos_select_own" on public.videos;
create policy "videos_select_own" on public.videos
    for select using (
        exists (select 1 from public.jobs j
                where j.id = videos.job_id and j.user_id = auth.uid()));

-- chats / lectures: no client policies on purpose - every read and write
-- goes through the backend API (service key bypasses RLS entirely).
