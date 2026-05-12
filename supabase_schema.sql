create extension if not exists pgcrypto;

create table if not exists repositories (
    id uuid primary key default gen_random_uuid(),
    full_name text not null unique,
    github_repo_id bigint,
    webhook_id bigint,
    config jsonb not null default '{"strictness":"medium","languages":["python","javascript","typescript"]}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists reviews (
    id uuid primary key default gen_random_uuid(),
    repo_id uuid references repositories(id) on delete cascade,
    repo_full_name text not null,
    pr_number integer not null,
    pr_title text not null default '',
    pr_author text not null default '',
    quality_score integer not null default 80,
    total_comments integer not null default 0,
    bugs_found integer not null default 0,
    security_issues integer not null default 0,
    status text not null default 'completed',
    summary text not null default '',
    duration_seconds integer,
    created_at timestamptz not null default now()
);

create table if not exists review_comments (
    id uuid primary key default gen_random_uuid(),
    review_id uuid not null references reviews(id) on delete cascade,
    file_path text not null,
    line_number integer not null,
    issue_type text not null,
    severity text not null,
    comment_body text not null,
    suggestion text not null default '',
    created_at timestamptz not null default now()
);

alter table repositories enable row level security;
alter table reviews enable row level security;
alter table review_comments enable row level security;

grant usage on schema public to anon, authenticated;
grant select on repositories to anon, authenticated;
grant select on reviews to anon, authenticated;
grant select on review_comments to anon, authenticated;

drop policy if exists "Allow service role repositories" on repositories;
drop policy if exists "Allow service role reviews" on reviews;
drop policy if exists "Allow service role review comments" on review_comments;
drop policy if exists "Allow dashboard read repositories" on repositories;
drop policy if exists "Allow dashboard read reviews" on reviews;
drop policy if exists "Allow dashboard read review comments" on review_comments;

create policy "Allow service role repositories"
on repositories for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "Allow service role reviews"
on reviews for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "Allow service role review comments"
on review_comments for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "Allow dashboard read repositories"
on repositories for select
using (true);

create policy "Allow dashboard read reviews"
on reviews for select
using (true);

create policy "Allow dashboard read review comments"
on review_comments for select
using (true);

notify pgrst, 'reload schema';
