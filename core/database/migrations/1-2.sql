create table if not exists skus (
    id          uuid primary key,
    name        text not null,
    description text not null
);
