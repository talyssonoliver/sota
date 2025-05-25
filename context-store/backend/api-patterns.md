# API Design Patterns

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
