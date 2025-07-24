-- Artesanato E-commerce Database Schema

-- Categories table
CREATE TABLE categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  price DECIMAL(10, 2) NOT NULL,
  category_id UUID REFERENCES categories(id),
  image_url TEXT,
  inventory_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers table
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  address TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES customers(id),
  status TEXT NOT NULL DEFAULT 'pending',
  total DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INTEGER NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Carts table
CREATE TABLE carts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES customers(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cart items table
CREATE TABLE cart_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  phone_number TEXT,
  role TEXT DEFAULT 'customer',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies setup

-- Products
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
CREATE POLICY product_select_policy ON products FOR SELECT USING (true);
CREATE POLICY product_insert_policy ON products FOR INSERT WITH CHECK (auth.role() = 'admin');
CREATE POLICY product_update_policy ON products FOR UPDATE USING (auth.role() = 'admin');
CREATE POLICY product_delete_policy ON products FOR DELETE USING (auth.role() = 'admin');

-- Categories
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
CREATE POLICY category_select_policy ON categories FOR SELECT USING (true);
CREATE POLICY category_insert_policy ON categories FOR INSERT WITH CHECK (auth.role() = 'admin');
CREATE POLICY category_update_policy ON categories FOR UPDATE USING (auth.role() = 'admin');
CREATE POLICY category_delete_policy ON categories FOR DELETE USING (auth.role() = 'admin');

-- Orders
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY order_select_policy ON orders FOR SELECT 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY order_insert_policy ON orders FOR INSERT WITH CHECK (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY order_update_policy ON orders FOR UPDATE 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY order_delete_policy ON orders FOR DELETE 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');

-- Carts
ALTER TABLE carts ENABLE ROW LEVEL SECURITY;
CREATE POLICY cart_select_policy ON carts FOR SELECT 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY cart_insert_policy ON carts FOR INSERT WITH CHECK (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY cart_update_policy ON carts FOR UPDATE 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');
CREATE POLICY cart_delete_policy ON carts FOR DELETE 
  USING (auth.uid() = customer_id OR auth.role() = 'admin');

-- Users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_select_policy ON users FOR SELECT 
  USING (auth.uid() = id OR auth.role() = 'admin');
CREATE POLICY user_insert_policy ON users FOR INSERT WITH CHECK (auth.uid() = id OR auth.role() = 'admin');
CREATE POLICY user_update_policy ON users FOR UPDATE 
  USING (auth.uid() = id OR auth.role() = 'admin');
CREATE POLICY user_delete_policy ON users FOR DELETE 
  USING (auth.uid() = id OR auth.role() = 'admin');