create table if not exists categories (
    id              uuid primary key,
    name            text not null,
    created_at      timestamp not null default now()
);

create table if not exists skus (
    id              uuid primary key,
    category_id     uuid not null references categories(id),
    name            text not null,
    description     text not null,
    created_at      timestamp not null default now()
);
