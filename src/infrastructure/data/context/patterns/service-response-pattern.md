# Service Response Pattern
**Reviewed: Not yet reviewed**

## Standard Response Structure

All service functions in the Artesanato E-commerce project return a consistent data structure:

```typescript
{
  data: T | null,  // The result data or null if error
  error: {         // null if no error
    message: string,
    code?: string,
    context?: string,
    details?: any
  } | null
}
```

## Implementation

The standard implementation always follows this pattern:

```typescript
export async function functionName(params): Promise {
  try {
    // Business logic implementation
    const result = await supabaseClient.from('table_name').select('*');
      
    if (result.error) {
      return { data: null, error: result.error };
    }
    
    return { data: result.data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.functionName');
  }
}
```

## Benefits

- **Consistency**: All service functions follow the same pattern
- **Error Handling**: Errors are properly captured and formatted
- **Type Safety**: Response structure is consistent across the entire application
- **Client Simplicity**: Frontend code can handle responses uniformly

## Related Patterns
- [Error Handling Pattern](error-handling-pattern.md)
- [Service CRUD Operations](service-crud-operations.md)
- [API Route Integration](api-route-integration.md)

---
*Drafted by doc_agent on May 16, 2025. Backend engineer: please review for accuracy and completeness.*