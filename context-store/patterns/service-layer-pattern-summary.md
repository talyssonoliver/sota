# Service Layer Pattern
**Reviewed: Not yet reviewed**


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
    return handleError(error, 
...
able_name')
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

---
*Drafted by doc_agent on May 16, 2025. Appropriate domain expert: please review for accuracy and completeness.*