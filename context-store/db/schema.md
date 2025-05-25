# Database Schema

## Core Tables

### users
- id: uuid (primary key)
- email: varchar(255) unique
- password_hash: varchar(255)
- name: varchar(100)
- created_at: timestamp
- updated_at: timestamp

### orders  
- id: uuid (primary key)
- user_id: uuid (foreign key -> users.id)
- status: enum ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
- total_amount: decimal(10,2)
- created_at: timestamp
- updated_at: timestamp

### products
- id: uuid (primary key)
- name: varchar(255)
- description: text
- price: decimal(10,2)
- stock_quantity: integer
- category_id: uuid
- created_at: timestamp

## Relationships
- users 1---* orders (one user can have many orders)
- orders *---* products (many-to-many through order_items)

## RLS Policies
- Users can only access their own orders
- Products are publicly readable
- Orders require user authentication

## Indexes
- users.email (unique)
- orders.user_id 
- orders.status
- products.category_id
