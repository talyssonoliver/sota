# Service Layer Pattern Summary

## Key Principles
- Consistent return format for all services 
- Centralized error handling
- Separation of data access from business logic
- Strong TypeScript typing

## Standard Response
```ts
{
  data: T | null,
  error: {
    message: string,
    code?: string,
    context?: string,
    details?: any
  } | null
}
```

## Common Operations
- getById(id): Get single record by ID
- getAll(options): List with filters, pagination, sorting
- create(item): Create new record
- update(id, updates): Update existing record
- remove(id): Delete record

## Error Handling
- All services use handleError utility
- Errors include context, code, and details
- Consistent format for API responses