# API Route Integration
**Reviewed: Not yet reviewed**

## Overview

This document describes how service functions are integrated with Next.js API routes in the Artesanato E-commerce project.

## Basic API Route Pattern

```typescript
// app/api/products/route.ts
import { ProductService } from '@/lib/services/productService';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');
  
  if (id) {
    const result = await ProductService.getById(id);
    
    if (result.error) {
      return NextResponse.json(result, { status: 400 });
    }
    
    return NextResponse.json(result);
  }
  
  // Get all products
  const result = await ProductService.getAll();
  return NextResponse.json(result);
}
```

## HTTP Status Codes

- **200**: Successful operation (default)
- **400**: Client error (validation error, bad request)
- **401**: Unauthorized (missing or invalid authentication)
- **403**: Forbidden (authenticated but insufficient permissions)
- **404**: Not found (resource doesn't exist)
- **500**: Server error (unexpected errors)

## Status Code Mapping

Map service response to appropriate HTTP status code:

```typescript
export async function GET(request: Request) {
  const result = await ProductService.getById(id);
  
  if (result.error) {
    // Map error code to HTTP status
    const statusCode = mapErrorToStatus(result.error.code);
    return NextResponse.json(result, { status: statusCode });
  }
  
  return NextResponse.json(result);
}

// Helper function to map error codes to HTTP status codes
function mapErrorToStatus(errorCode: string): number {
  switch (errorCode) {
    case 'NOT_FOUND':
      return 404;
    case 'VALIDATION_ERROR':
      return 400;
    case 'UNAUTHORIZED':
      return 401;
    case 'FORBIDDEN':
      return 403;
    default:
      return 500;
  }
}
```

## Request Validation

Validate request parameters before calling service functions:

```typescript
export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.name || !body.price) {
      return NextResponse.json({ 
        data: null, 
        error: { message: 'Name and price are required fields' } 
      }, { status: 400 });
    }
    
    const result = await ProductService.create(body);
    return NextResponse.json(result, { 
      status: result.error ? 400 : 201 
    });
  } catch (error) {
    return NextResponse.json({ 
      data: null, 
      error: { message: 'Invalid request body' } 
    }, { status: 400 });
  }
}
```

## Related Patterns
- [Service Response Pattern](service-response-pattern.md)
- [Error Handling Pattern](error-handling-pattern.md)
- [Service CRUD Operations](service-crud-operations.md)

---
*Drafted by doc_agent on May 16, 2025. Backend engineer: please review for accuracy and completeness.*