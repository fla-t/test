## Test Submission

Thanks for the taking the time to read this, this repo represents all I learned in building systems
in python.

## Main features that set this apart:

### 1. No Mocking in test

The database is real, just like how god intended it to be. For each test there is a database
that is created and dropped.

### 2. Using Unit of Work pattern to inject repository implementations

The repositories in this codebase are passed by UoW abstractions, decoupling services with the
repository logic and easier testing

## How to run?

Just use docker-compose to run the application, everything from the database and creating
seeds for testing will be created automatically

just run:

    docker-compose -up --build

## Endpoints:

### Product:

| Method | Path             | Description                  | Request Body                                                        | Success Response                                        |
| :----: | ---------------- | ---------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------- |
|  GET   | `/products/`     | Fetch all products           | None                                                                | `200` + list of products                                |
|  GET   | `/products/{id}` | Fetch a single product by ID | None                                                                | `200` + product obj<br>`404` if not found               |
|  POST  | `/products/`     | Create a new product         | `ProductSchema`<br> (`name`, `category_id`, `description`, `price`) | `200` + created product                                 |
|  PUT   | `/products/{id}` | Update an existing product   | `ProductSchema`                                                     | `200` + updated product<br>`404` if not found           |
| DELETE | `/products/{id}` | Delete a product by ID       | None                                                                | `200` + `{ "message": "Product deleted successfully" }` |

### Categories:

| Method | Path               | Description                   | Request Body                                        | Success Response                           |
| :----: | ------------------ | ----------------------------- | --------------------------------------------------- | ------------------------------------------ |
|  GET   | `/categories/`     | Fetch all product categories  | None                                                | `200` + list of categories                 |
|  GET   | `/categories/{id}` | Fetch a single category by ID | None                                                | `200` + category obj<br>`404` if not found |
|  POST  | `/categories/`     | Create a new product category | `ProductCategorySchema`<br> (`name`, `description`) | `200` + created category                   |

### Sales:

| Method | Path                   | Description                                                          | Query / Body                                                                                                                                                                                                                                 | Success Response        |
| :----: | ---------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
|  POST  | `/sales/`              | Create a new sale record (just for testing, not for real production) | **Body**: `SaleSchema` `{ product_id, quantity, total_price }`                                                                                                                                                                               | `201` + sale object     |
|  GET   | `/sales/between-dates` | Fetch sales filtered by date, product, or category                   | **Query**:<br>`start_date` (optional, ISO datetime)<br>`end_date` (optional)<br>`product_id` (optional)<br>`category_id` (optional)                                                                                                          | `200` + list of sales   |
|  GET   | `/sales/compare`       | Compare two periods’ sales totals                                    | **Query**:<br>`first_start`, `first_end`, `second_start`, `second_end` (all required ISO datetimes)<br>`product_id` (optional)<br>`category_id` (optional)<br>`granularity` (optional, one of `"day"`, `"week"`, `"month"`, default `"day"`) | `200` + comparison data |

### Inventory:

| Method | Path                              | Description                                       | Query / Body                                                 | Success Response                                             |
| :----: | --------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
|  GET   | `/inventory/current/{product_id}` | Get the latest inventory level for one product    | **Path**: `product_id`                                       | `200` + inventory item<br>`404` if not found                 |
|  GET   | `/inventory/current`              | List the latest inventory levels for all products | None                                                         | `200` + list of inventory items                              |
|  POST  | `/inventory/update`               | Add a new inventory adjustment for a product      | **Body**: `InventoryUpdateSchema` `{ product_id, quantity }` | `200` + updated inventory item<br>`404` if product not found |
|  GET   | `/inventory/low-stock-alerts`     | List items whose quantity ≤ threshold             | **Query**: `threshold` (int, default `10`)                   | `200` + list of low-stock items                              |

## Database Setup:

I am using postgres as my database and using sqlalchemy for ORM. Not really a fan of the orm but
they saved me some time here.

All the migrations are done through alembic, even the seeds.

## Schema:

### 1. product_categories:

Used to list all the categories of items

| Column        | Type    | Constraints          |
| ------------- | ------- | -------------------- |
| `id`          | UUID    | Primary Key, indexed |
| `name`        | VARCHAR | Not nullable, Unique |
| `description` | TEXT    | Nullable             |

### 2. products

Used to list all the products, their details and their category.
(Instead of making a product_categories mapping table I have just added the category here, as its unlikely that one product will have multiple categories)
| Column | Type | Constraints |
| ------------- | ------- | --------------------------------------------------------------------- |
| `id` | UUID | Primary Key, indexed |
| `name` | VARCHAR | Not nullable |
| `category` | UUID | Foreign Key → `product_categories(id)`, indexed, `ON DELETE SET NULL` |
| `description` | TEXT | Nullable |
| `price` | DOUBLE | Not nullable |

### 3. sales

Used to keep sales data, in production would be linked to each item that is sold.
| Column | Type | Constraints |
| ------------- | ------------------------ | ------------------------------------- |
| `id` | UUID | Primary Key |
| `product_id` | UUID | Foreign Key → `products(id)`, indexed |
| `quantity` | INTEGER | Not nullable |
| `total_price` | DOUBLE | Not nullable |
| `created_at` | TIMESTAMP WITH TIME ZONE | Not nullable, defaults to `now()` |

### 4. inventory

Used to keep track of inventory count of items
| Column | Type | Constraints |
| ------------ | ------- | -------------------------------------------------- |
| `product_id` | UUID | Primary Key, Foreign Key → `products(id)`, indexed |
| `quantity` | INTEGER | Not nullable, default = 0 |

### 5. inventory_updates

Used to keep track of all the changes that have been made in the inventory
| Column | Type | Constraints |
| ------------ | ------------------------ | ---------------------------------------------------- |
| `id` | UUID | Primary Key |
| `product_id` | UUID | Foreign Key → `inventory_items(product_id)`, indexed |
| `quantity` | INTEGER | Not nullable (positive or negative, to adjust stock) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Not nullable, defaults to `now()` |

## Whats missing?

1. Auth, A real production applications like this needs both authorization and authentication.
2. Better DB pooling, For the sake of time I have taken some shortcuts in my db setup. wouldnt scale in real world app
3. Logging, again for the sake of time logging and tracing are all skipped
4. Anti corruption layer, the sales service should have ACL to get more information about the product, doing so would have taken a lott of time.
