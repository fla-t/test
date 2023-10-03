create table if not exists sales (
    id                  uuid                        primary key,
    inventory_log_id    uuid not null               references inventory_logs(id),
    price               int  not null,
    created_at          timestamp with time zone    not null default now()
);
