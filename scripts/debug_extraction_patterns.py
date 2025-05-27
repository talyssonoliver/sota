#!/usr/bin/env python3
"""Debug script to test code extraction patterns."""

import os
import re
import sys

from orchestration.extract_code import CodeExtractor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Sample test data from the test file
sample_output_advanced = """# Backend Agent Output for BE-07

## Implementation Summary
Successfully implemented the customer service layer with advanced features.

## Code Implementation

### Customer Service
```typescript
// filename: customerService.ts
export class CustomerService {
    constructor(private supabase: SupabaseClient) {}

    async getCustomer(id: string): Promise<Customer | null> {
        const { data, error } = await this.supabase
            .from('customers')
            .select('*')
            .eq('id', id)
            .single();

        if (error) {
            throw new Error(`Failed to fetch customer: ${error.message}`);
        }

        return data;
    }
}
```

### Order Service
```typescript
// filename: orderService.ts
export class OrderService {
    constructor(private supabase: SupabaseClient) {}

    async createOrder(customerId: string, items: OrderItem[]): Promise<Order> {
        const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        const { data, error } = await this.supabase
            .from('orders')
            .insert({
                customer_id: customerId,
                items,
                total_amount: totalAmount,
                status: 'pending'
            })
            .select()
            .single();

        if (error) {
            throw new Error(`Failed to create order: ${error.message}`);
        }

        return data;
    }
}
```

### Database Migration
```sql
-- filename: migrations/001_add_indexes.sql
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### Configuration Files
```yaml
# filename: config/database.yaml
database:
  host: localhost
  port: 5432
  name: artesanato_db

supabase:
  url: https://your-project.supabase.co
  anon_key: your-anon-key

redis:
  host: localhost
  port: 6379
  db: 0
```

### Python Utility Functions
```python
# filename: utils/validation.py
from typing import Optional, Dict, Any
import re

def validate_email(email: str) -> bool:
    \"\"\"Validate email format.\"\"\"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_order_data(data: Dict[str, Any]) -> Optional[str]:
    \"\"\"Validate order data structure.\"\"\"
    required_fields = ['customer_id', 'total_amount']

    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"

    if not isinstance(data['total_amount'], (int, float)) or data['total_amount'] <= 0:
        return "Total amount must be a positive number"

    return None

class ValidationError(Exception):
    \"\"\"Custom validation error.\"\"\"
    pass
```

### JSON Configuration
```json
{"filename": "config/app.json"}
{
  "app": {
    "name": "Artesanato E-commerce",
    "version": "1.0.0",
    "environment": "development"
  },
  "features": {
    "customer_management": true,
    "order_processing": true,
    "inventory_tracking": false
  },
  "logging": {
    "level": "info",
    "format": "json"
  }
}
```

### Simple Code Block (No Filename)
```bash
npm install
npm run build
npm start
```

## Summary
All service functions implemented successfully with proper error handling and TypeScript types."""


def debug_patterns():
    """Debug the regex patterns to see what's being matched."""

    extractor = CodeExtractor()

    print("=== DEBUGGING CODE EXTRACTION PATTERNS ===\n")

    # Test each pattern individually
    patterns = extractor.code_patterns

    for i, pattern_str in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern_str[:100]}...")
        pattern = re.compile(pattern_str, re.DOTALL)
        matches = list(pattern.finditer(sample_output_advanced))
        print(f"Found {len(matches)} matches")

        for j, match in enumerate(matches, 1):
            groups = match.groups()
            print(f"  Match {j}:")
            print(f"    Full match length: {len(match.group(0))}")
            for k, group in enumerate(groups):
                if group:
                    print(f"    Group {k}: {repr(group[:50])}...")
        print()

    # Test the actual extraction
    print("=== ACTUAL EXTRACTION RESULTS ===")
    result = extractor._extract_code_blocks(sample_output_advanced)
    print(f"Total extracted files: {len(result.extracted_files)}")
    for file_info in result.extracted_files:
        print(
            f"  - {file_info['filename']} ({file_info['language']}, {len(file_info['content'])} chars)")


if __name__ == "__main__":
    debug_patterns()
