# Service Layer Pattern

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
