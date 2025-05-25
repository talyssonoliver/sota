# Error Handling Pattern
**Reviewed: Not yet reviewed**

## Overview

This document describes the standard error handling approach for services in the Artesanato E-commerce project.

## Error Handler Function

All services use the `handleError` utility function for consistent error handling:

```typescript
function handleError(error: any, context: string): { data: null, error: any } {
  console.error(`Error in ${context}:`, error);
  
  return {
    data: null,
    error: {
      message: error?.message || 'An unexpected error occurred',
      code: error?.code || 'UNKNOWN_ERROR',
      context,
      details: error
    }
  };
}
```

## Error Object Structure

The error object follows a consistent structure:

- **message**: Human-readable error description
- **code**: Error code for programmatic handling (e.g., 'VALIDATION_ERROR')
- **context**: Location where the error occurred (e.g., 'ProductService.getById')
- **details**: Original error object or additional error information

## Usage Pattern

```typescript
export async function serviceFunction(): Promise {
  try {
    // Attempt operation
    // ...
  } catch (error) {
    return handleError(error, 'ServiceName.functionName');
  }
}
```

## Error Handling Best Practices

1. **Always provide context** when calling handleError
2. **Never throw errors** from service functions, always return them
3. **Log all errors** at their source
4. **Use specific error codes** when possible
5. **Include relevant details** without exposing sensitive information

## Related Patterns
- [Service Response Pattern](service-response-pattern.md)
- [Service CRUD Operations](service-crud-operations.md)
- [API Route Integration](api-route-integration.md)

---
*Drafted by doc_agent on May 16, 2025. Backend engineer: please review for accuracy and completeness.*