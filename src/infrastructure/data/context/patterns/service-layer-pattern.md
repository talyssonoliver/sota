# Service Layer Pattern

## Overview

The Artesanato E-commerce project follows a consistent service layer pattern for all backend interactions. This document outlines the standard patterns to use when implementing service functions.

## Basic Service Pattern

All service functions return a consistent data structure with the following format:

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

The standard implementation looks like:

```typescript
export async function functionName(params): Promise {
  try {
    // Supabase interaction
    const result = await supabaseClient
      .from('table_name')
      .select('*')
      .eq('field', value);
      
    if (result.error) {
      return { data: null, error: result.error };
    }
    
    return { data: result.data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.functionName');
  }
}
```

## Error Handling

Use the handleError utility function for consistent error handling:

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

## CRUD Operation Patterns

### Get One Record

```typescript
export async function getById(id: string): Promise {
  try {
    const { data, error } = await supabaseClient
      .from('table_name')
      .select('*')
      .eq('id', id)
      .single();
      
    if (error) {
      return { data: null, error };
    }
    
    return { data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.getById');
  }
}
```

### Get Multiple Records

```typescript
export async function getAll(options?: QueryOptions): Promise {
  try {
    let query = supabaseClient.from('table_name').select('*');
    
    // Apply filters if provided
    if (options?.filters) {
      for (const [field, value] of Object.entries(options.filters)) {
        query = query.eq(field, value);
      }
    }
    
    // Apply pagination
    if (options?.page && options?.pageSize) {
      const start = (options.page - 1) * options.pageSize;
      const end = start + options.pageSize - 1;
      query = query.range(start, end);
    }
    
    const { data, error } = await query;
    
    if (error) {
      return { data: null, error };
    }
    
    return { data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.getAll');
  }
}
```

### Create Record

```typescript
export async function create(item: NewItem): Promise {
  try {
    const { data, error } = await supabaseClient
      .from('table_name')
      .insert(item)
      .select()
      .single();
      
    if (error) {
      return { data: null, error };
    }
    
    return { data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.create');
  }
}
```

### Update Record

```typescript
export async function update(id: string, updates: Partial): Promise {
  try {
    const { data, error } = await supabaseClient
      .from('table_name')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
      
    if (error) {
      return { data: null, error };
    }
    
    return { data, error: null };
  } catch (error) {
    return handleError(error, 'ServiceName.update');
  }
}
```

### Delete Record

```typescript
export async function remove(id: string): Promise {
  try {
    const { error } = await supabaseClient
      .from('table_name')
      .delete()
      .eq('id', id);
      
    if (error) {
      return { success: false, error };
    }
    
    return { success: true, error: null };
  } catch (error) {
    const processedError = handleError(error, 'ServiceName.remove');
    return { success: false, error: processedError.error };
  }
}
```

## Usage In API Routes

Services are used in API routes like this:

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