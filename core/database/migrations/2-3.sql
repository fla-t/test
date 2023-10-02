create table if not exists inventory_logs (
    id                  uuid                        primary key,
    sku_id              uuid not null               references skus(id),
    quantity_changed    int not null,
    created_at          timestamp with time zone    not null default now()
);
