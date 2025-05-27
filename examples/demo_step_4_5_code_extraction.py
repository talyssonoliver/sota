#!/usr/bin/env python3
"""
Demo script for Step 4.5 — Code Extraction functionality
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

from orchestration.extract_code import CodeExtractor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_code_extraction():
    """Demonstrate the code extraction functionality."""
    print("🔧 Step 4.5 — Code Extraction Demo")
    print("=" * 50)

    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    task_dir = Path(test_dir) / "BE-07"
    task_dir.mkdir()

    # Sample agent output with code blocks
    sample_output = """# Backend Agent Output for BE-07

## Implementation Summary
Successfully implemented the customer service layer.

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

### Database Migration
```sql
-- filename: migrations/001_add_indexes.sql
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### Configuration
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
    "order_processing": true
  }
}
```

### Python Utilities
```python
# filename: utils/validation.py
def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```
"""

    try:
        # Create output file
        output_file = task_dir / "output_backend.md"
        output_file.write_text(sample_output)

        # Initialize extractor
        extractor = CodeExtractor(base_outputs_dir=test_dir)

        print(f"📁 Created test task: {task_dir}")
        print(f"📄 Agent output file: {output_file}")
        print()

        # Extract code
        print("🔍 Extracting code blocks...")
        result = extractor.extract_from_task_agent("BE-07", "backend")

        print(f"✅ Extraction completed successfully!")
        print(f"   📊 Total code blocks: {result.total_code_blocks}")
        print(f"   📂 Extracted files: {len(result.extracted_files)}")
        print(
            f"   🔤 Languages detected: {', '.join(result.languages_detected)}")
        print()

        # Show extracted files
        code_dir = task_dir / "code"
        if code_dir.exists():
            print("📁 Extracted Files:")
            for file_path in sorted(code_dir.iterdir()):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    print(f"   📄 {file_path.name} ({size} bytes)")

        # Show metadata
        metadata_file = task_dir / "code_extraction_metadata.json"
        if metadata_file.exists():
            print(f"\\n📋 Metadata saved: {metadata_file.name}")

        print(f"\\n🗂️  Files extracted to: {code_dir}")

        # Test batch extraction
        print(f"\\n🔄 Testing batch extraction...")
        results = extractor.extract_from_all_agents("BE-07")
        print(f"✅ Batch extraction completed for {len(results)} agents")

        # Cleanup
        shutil.rmtree(test_dir)

        print(f"\\n🎉 Step 4.5 — Code Extraction is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        shutil.rmtree(test_dir)
        return False


if __name__ == "__main__":
    success = demo_code_extraction()
    sys.exit(0 if success else 1)
