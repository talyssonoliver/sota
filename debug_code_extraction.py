#!/usr/bin/env python3
"""
Quick test to debug code extraction
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.register_output import AgentOutputRegistry

def test_code_extraction():
    # Create temp directory
    test_dir = tempfile.mkdtemp()
    registry = AgentOutputRegistry(base_outputs_dir=test_dir)
    
    # Sample content with code blocks
    sample_output = """# Test Output

```typescript
// filename: customerService.ts
export class CustomerService {
    async getCustomer() { return null; }
}
```

```typescript
// filename: orderService.ts
export class OrderService {
    async createOrder() { return null; }
}
```

```sql
-- filename: customer_schema.sql
CREATE TABLE customers (id UUID PRIMARY KEY);
```
"""
    
    # Create sample file
    source_file = Path(test_dir) / "sample.md"
    source_file.write_text(sample_output)
    
    # Register with code extraction
    registration = registry.register_output(
        task_id="TEST-01",
        agent_id="backend",
        source_path=str(source_file),
        extract_code=True
    )
    
    print(f"Extracted artifacts: {registration.extracted_artifacts}")
    
    # List actual files in code directory
    code_dir = Path(test_dir) / "TEST-01" / "code"
    if code_dir.exists():
        print(f"Files in code directory:")
        for file in code_dir.iterdir():
            print(f"  - {file.name}")
    else:
        print("Code directory does not exist")
    
    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_code_extraction()
