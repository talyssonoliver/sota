# Artesanato E-commerce Database Schema
**Reviewed: Not yet reviewed**


## Tables

### categories
- `id` UUID PRIMARY KEY
- `name` TEXT NOT NULL
- `description` TEXT
- `image_url` TEXT
- `created_at` TIMESTAMP WITH TIME ZONE 
- `updated_at` TIMESTAMP WITH TIME ZONE

### products
- `id` UUID PRIMARY KEY
- `name` TEXT NOT NULL
- `description` TEXT
- `price` DECIMAL(10, 2) NOT NULL
- `category_id` UUID REFERENCES categories(id)
- `image_url` TEXT
- `inventory_count` INTEGER NOT NULL DEFAULT 0
- `created_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

### customers
- `id` UUID PRIMARY KEY
- `email` TEXT UNIQUE NOT NULL
- `name` TEXT NOT NULL
- `address` TEXT
- `created_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

### orders
- `id` UUID PRIMARY KEY
- `customer_id` UUID REFERENCES customers(id)
- `status` TEXT NOT NULL DEFAULT 'pending'
- `total` DECIMAL(10, 2) NOT NULL
- `created_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

### order_items
- `id` UUI
...
TAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

### users
- `id` UUID PRIMARY KEY
- `email` TEXT UNIQUE NOT NULL
- `name` TEXT
- `phone_number` TEXT
- `role` TEXT DEFAULT 'customer'
- `created_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

## Relationships
- `users` 1---1 `customers`
- `customers` 1---* `orders`
- `customers` 1---1 `carts`
- `orders` 1---* `order_items`
- `carts` 1---* `cart_items`
- `products` 1---* `order_items`
- `products` 1---* `cart_items`
- `categories` 1---* `products`

## RLS Policies

### Products
- Everyone can view products
- Only admins can create, update or delete products

### Categories
- Everyone can view categories
- Only admins can create, update or delete categories

### Orders
- Users can only access their own orders
- Admins can access all orders

### Carts
- Users can only access their own cart
- Admins can access all carts

### Users
- Users can only access their own user data
- Admins can access all user data

---
*Drafted by doc_agent on May 16, 2025. Appropriate domain expert: please review for accuracy and completeness.*