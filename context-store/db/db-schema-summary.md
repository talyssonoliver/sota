# Database Schema Summary

## Tables
- categories: id, name, description, image_url, created_at, updated_at
- products: id, name, description, price, category_id, image_url, inventory_count, created_at, updated_at
- customers: id, email, name, address, created_at, updated_at
- orders: id, customer_id, status, total, created_at, updated_at
- order_items: id, order_id, product_id, quantity, price, created_at
- carts: id, customer_id, created_at, updated_at
- cart_items: id, cart_id, product_id, quantity, created_at, updated_at
- users: id, email, name, phone_number, role, created_at, updated_at 

## Relationships
- categories 1---* products
- users 1---1 customers
- customers 1---* orders
- customers 1---1 carts
- orders 1---* order_items
- carts 1---* cart_items
- products 1---* order_items
- products 1---* cart_items

## RLS Policies
- Products/Categories: Public read, admin-only write
- Orders/Carts: Users can only access their own data
- Users: Users can only access their own user data
- Admins have full access to all data