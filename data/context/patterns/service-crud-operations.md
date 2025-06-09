# Service CRUD Operations
**Reviewed: Not yet reviewed**

## Overview

This document describes the standard CRUD (Create, Read, Update, Delete) operation patterns for service functions in the Artesanato E-commerce project.

## Read Operations

### Get One Record (getById)

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

### Get Multiple Records (getAll)

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

## Create Operations

### Create Record (create)

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

## Update Operations

### Update Record (update)

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

## Delete Operations

### Delete Record (remove)

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

## Naming Conventions

- **Single record retrieval**: `getById`, `getByEmail`, etc.
- **Multiple record retrieval**: `getAll`, `getAllByCategory`, etc.
- **Creating records**: `create`
- **Updating records**: `update`
- **Deleting records**: `remove` (not "delete" to avoid keyword conflicts)

## Related Patterns
- [Service Response Pattern](service-response-pattern.md)
- [Error Handling Pattern](error-handling-pattern.md)
- [API Route Integration](api-route-integration.md)

---
*Drafted by doc_agent on May 16, 2025. Backend engineer: please review for accuracy and completeness.*