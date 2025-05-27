#!/usr/bin/env python3
"""
Context Store Setup for Step 3.5 & 3.6 Testing

This script populates the context store with documents that match
the context topics used in tasks, enabling proper testing of the
Step 3.5 and 3.6 implementations.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_context_documents():
    """Create context documents for testing Step 3.5 & 3.6"""

    context_store = project_root / "context-store"

    # Ensure subdirectories exist
    subdirs = ["db", "patterns", "infra", "backend", "frontend"]
    for subdir in subdirs:
        (context_store / subdir).mkdir(parents=True, exist_ok=True)

    # Database schema context (db-schema topic)
    db_schema_content = """# Database Schema

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
"""

    with open(context_store / "db" / "schema.md", 'w') as f:
        f.write(db_schema_content)

    # Service layer pattern context
    service_pattern_content = """# Service Layer Pattern

## Overview
The service layer pattern encapsulates business logic and provides a clean API for controllers to interact with data models.

## Structure

### Base Service Class
```typescript
abstract class BaseService<T> {
  protected supabase: SupabaseClient;

  constructor() {
    this.supabase = createClient(url, key);
  }

  abstract findById(id: string): Promise<T | null>;
  abstract create(data: Partial<T>): Promise<T>;
  abstract update(id: string, data: Partial<T>): Promise<T>;
  abstract delete(id: string): Promise<boolean>;
}
```

### Implementation Example
```typescript
export class CustomerService extends BaseService<Customer> {
  async findById(id: string): Promise<Customer | null> {
    const { data, error } = await this.supabase
      .from('users')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw new Error(error.message);
    return data;
  }

  async create(customerData: Partial<Customer>): Promise<Customer> {
    // Validation logic
    if (!customerData.email) {
      throw new Error('Email is required');
    }

    const { data, error } = await this.supabase
      .from('users')
      .insert([customerData])
      .select()
      .single();

    if (error) throw new Error(error.message);
    return data;
  }
}
```

## Best Practices
1. Keep services focused on single responsibility
2. Use dependency injection for testability
3. Implement proper error handling
4. Add validation at service layer
5. Use transactions for complex operations
"""

    with open(context_store / "patterns" / "service-layer.md", 'w') as f:
        f.write(service_pattern_content)

    # Supabase setup context
    supabase_setup_content = """# Supabase Setup Guide

## Environment Configuration

### Environment Variables
```bash
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Client Initialization
```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);
```

## Database Setup

### Row Level Security (RLS)
Enable RLS on all tables:
```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
```

### Policies
```sql
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

-- Users can only see their own orders
CREATE POLICY "Users can view own orders" ON orders
  FOR SELECT USING (auth.uid() = user_id);
```

## Authentication Setup

### Enable Auth Providers
1. Email/Password authentication
2. OAuth providers (Google, GitHub)
3. Magic link authentication

### Auth Configuration
```typescript
export const signUp = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });

  if (error) throw error;
  return data;
};

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) throw error;
  return data;
};
```

## Real-time Setup
```typescript
// Subscribe to changes
const subscription = supabase
  .channel('orders')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'orders'
  }, (payload) => {
    console.log('Order changed:', payload);
  })
  .subscribe();
```
"""

    with open(context_store / "infra" / "supabase-setup.md", 'w') as f:
        f.write(supabase_setup_content)

    # Additional context for testing
    api_patterns_content = """# API Design Patterns

## RESTful Endpoints

### Standard CRUD Operations
- GET /api/customers - List customers
- GET /api/customers/:id - Get customer by ID
- POST /api/customers - Create customer
- PUT /api/customers/:id - Update customer
- DELETE /api/customers/:id - Delete customer

### Error Handling
```typescript
export interface APIResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}
```

## Request Validation
```typescript
import { z } from 'zod';

const CustomerSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  phone: z.string().optional(),
});

export const validateCustomerInput = (data: unknown) => {
  return CustomerSchema.parse(data);
};
```
"""

    with open(context_store / "backend" / "api-patterns.md", 'w') as f:
        f.write(api_patterns_content)

    print("✅ Context documents created successfully!")
    print("📁 Documents created in context-store/:")
    print("   - db/schema.md")
    print("   - patterns/service-layer.md")
    print("   - infra/supabase-setup.md")
    print("   - backend/api-patterns.md")


def populate_memory_engine():
    """Populate the memory engine with context documents"""
    from tools.memory_engine import (add_document_with_enhanced_chunking,
                                     get_memory_engine)

    try:
        print("\n🔧 Initializing memory engine...")
        # Initialize memory engine
        memory_engine = get_memory_engine()

        print("📚 Adding context documents to memory engine...")

        context_files = [
            ("context-store/db/schema.md",
             {"topic": "db-schema", "category": "database"}),
            ("context-store/patterns/service-layer.md",
             {"topic": "service-layer-pattern", "category": "patterns"}),
            ("context-store/infra/supabase-setup.md",
             {"topic": "supabase-setup", "category": "infrastructure"}),
            ("context-store/backend/api-patterns.md",
             {"topic": "api-patterns", "category": "backend"}),
        ]

        for file_path, metadata in context_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"   Adding {file_path}...")
                add_document_with_enhanced_chunking(
                    str(full_path),
                    metadata=metadata,
                    chunk_size=500,
                    chunk_overlap=50,
                    user="system"  # Use system user for proper permissions
                )
            else:
                print(f"   ⚠️  File not found: {file_path}")

        print("✅ Memory engine populated successfully!")

    except Exception as e:
        print(f"❌ Error populating memory engine: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Setting up context store for Step 3.5 & 3.6 testing")
    print("=" * 55)

    create_context_documents()
    populate_memory_engine()

    print("\n🎉 Setup complete! You can now run the demo:")
    print("   python examples/step_3_5_3_6_demo.py")
