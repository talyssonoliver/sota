#!/usr/bin/env python3
"""
Step 4.4 — Register Agent Output Demo

This demo showcases the complete agent output registration system,
demonstrating how agent outputs are stored, tracked, and prepared
for downstream processing by QA and Documentation agents.

Demo Scenarios:
1. Backend agent output registration with code extraction
2. QA agent output registration
3. Status tracking and metadata management
4. QA input preparation for downstream agents
5. Multi-agent workflow demonstration
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from orchestration.register_output import AgentOutputRegistry

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"📋 {title}")
    print('=' * 60)


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def create_realistic_backend_output() -> str:
    """Create a realistic backend agent output for demonstration."""
    return """# Backend Agent Output for BE-07: Implement Missing Service Functions

## Task Summary
Successfully implemented comprehensive CRUD operations for the Supabase service layer, including customer management and order processing capabilities. All functions include proper error handling, type safety, and follow established service patterns.

## Implementation Details

### 1. Customer Service Implementation

```typescript
// filename: lib/services/customerService.ts
import { supabase } from '../supabase/client';
import { Customer, CreateCustomerData, UpdateCustomerData } from '../types/customer';

export class CustomerService {
  /**
   * Create a new customer with validation
   */
  async createCustomer(data: CreateCustomerData): Promise<Customer> {
    const { data: customer, error } = await supabase
      .from('customers')
      .insert([{
        ...data,
        created_at: new Date().toISOString(),
        status: 'active'
      }])
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to create customer: ${error.message}`);
    }

    return customer;
  }

  /**
   * Get customer by ID with error handling
   */
  async getCustomerById(id: string): Promise<Customer | null> {
    const { data: customer, error } = await supabase
      .from('customers')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') return null;
      throw new Error(`Failed to get customer: ${error.message}`);
    }

    return customer;
  }

  /**
   * Update customer with optimistic concurrency
   */
  async updateCustomer(id: string, data: UpdateCustomerData): Promise<Customer> {
    const { data: customer, error } = await supabase
      .from('customers')
      .update({
        ...data,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to update customer: ${error.message}`);
    }

    return customer;
  }
}

export const customerService = new CustomerService();
```

### 2. Order Service Implementation

```typescript
// filename: lib/services/orderService.ts
import { supabase } from '../supabase/client';
import { Order, CreateOrderData, OrderStatus } from '../types/order';

export class OrderService {
  /**
   * Create new order with items
   */
  async createOrder(data: CreateOrderData): Promise<Order> {
    const { data: order, error } = await supabase
      .from('orders')
      .insert([{
        ...data,
        status: 'pending',
        created_at: new Date().toISOString(),
        total_amount: this.calculateTotal(data.items)
      }])
      .select(`
        *,
        customer:customers(id, name, email),
        order_items:order_items(
          id, quantity, unit_price,
          product:products(id, name, price)
        )
      `)
      .single();

    if (error) {
      throw new Error(`Failed to create order: ${error.message}`);
    }

    return order;
  }

  /**
   * Get orders with advanced filtering
   */
  async getOrders(filters?: {
    status?: OrderStatus;
    customerId?: string;
    dateRange?: { from: string; to: string };
    page?: number;
    limit?: number;
  }): Promise<{ orders: Order[]; total: number }> {
    let query = supabase
      .from('orders')
      .select('*, customer:customers(name, email)', { count: 'exact' });

    // Apply filters
    if (filters?.status) {
      query = query.eq('status', filters.status);
    }

    if (filters?.customerId) {
      query = query.eq('customer_id', filters.customerId);
    }

    if (filters?.dateRange) {
      query = query
        .gte('created_at', filters.dateRange.from)
        .lte('created_at', filters.dateRange.to);
    }

    // Apply pagination
    const page = filters?.page || 1;
    const limit = filters?.limit || 20;
    const from = (page - 1) * limit;

    query = query.range(from, from + limit - 1);

    const { data: orders, error, count } = await query;

    if (error) {
      throw new Error(`Failed to get orders: ${error.message}`);
    }

    return { orders: orders || [], total: count || 0 };
  }

  private calculateTotal(items: any[]): number {
    return items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  }
}

export const orderService = new OrderService();
```

### 3. Database Schema

```sql
-- filename: schema/service_layer_schema.sql
-- Enhanced schema for service layer support

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Add RLS policies for security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Customer access policy
CREATE POLICY "Users can access own customer record"
ON customers FOR ALL
USING (auth.uid() = id);

-- Order access policy
CREATE POLICY "Users can access own orders"
ON orders FOR ALL
USING (customer_id = auth.uid());

-- Admin access policy
CREATE POLICY "Admins can access all records"
ON customers FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can access all orders"
ON orders FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');
```

### 4. Type Definitions

```typescript
// filename: lib/types/service.ts
export interface ServiceResponse<T> {
  data: T | null;
  error: string | null;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface FilterOptions {
  search?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
```

## Quality Assurance

### Error Handling
- ✅ Comprehensive error handling for all database operations
- ✅ Proper error messages with context
- ✅ Graceful handling of not-found scenarios

### Type Safety
- ✅ Full TypeScript integration
- ✅ Proper type definitions for all interfaces
- ✅ Type-safe database queries

### Performance
- ✅ Optimized queries with proper indexes
- ✅ Pagination support for large datasets
- ✅ Efficient relationship loading

### Security
- ✅ RLS policies implemented
- ✅ Input validation and sanitization
- ✅ Authentication checks

## Integration Notes

The implemented service functions are ready for integration with:
- Frontend React components via custom hooks
- API endpoints for external integrations
- Background job processing
- Admin dashboard functionality

## Testing Requirements

1. **Unit Tests**: Test each service method individually
2. **Integration Tests**: Test with actual Supabase instance
3. **Performance Tests**: Validate query performance with large datasets
4. **Security Tests**: Verify RLS policy enforcement

## Deployment Checklist

- [ ] Apply database schema updates
- [ ] Deploy service layer code
- [ ] Update frontend to use new services
- [ ] Run integration tests in staging
- [ ] Monitor performance metrics

**Task BE-07 implementation complete and ready for QA review.**"""


def create_realistic_qa_report() -> dict:
    """Create a realistic QA report for demonstration."""
    return {"task_id": "BE-07",
            "agent_id": "qa",
            "qa_session_id": "qa_BE-07_20250525_143000",
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": {"overall_status": "PASSED_WITH_RECOMMENDATIONS",
                                 "confidence_score": 94,
                                 "critical_issues": 0,
                                 "warnings": 3,
                                 "recommendations": 5,
                                 "code_quality_score": 92},
            "code_analysis": {"files_analyzed": ["lib/services/customerService.ts",
                                                 "lib/services/orderService.ts",
                                                 "schema/service_layer_schema.sql",
                                                 "lib/types/service.ts"],
                              "total_lines": 425,
                              "complexity_score": "MEDIUM",
                              "maintainability_index": 88,
                              "test_coverage_estimate": "87%"},
            "security_analysis": {"rls_compliance": "EXCELLENT",
                                  "input_validation": "GOOD",
                                  "sql_injection_protection": "SUPABASE_HANDLED",
                                  "authentication_required": True,
                                  "data_encryption": "TRANSPORT_LAYER"},
            "performance_analysis": {"query_efficiency": "EXCELLENT",
                                     "indexing_strategy": "WELL_IMPLEMENTED",
                                     "pagination_support": True,
                                     "caching_opportunities": ["Customer lookup caching",
                                                               "Order status aggregations"]},
            "detailed_findings": [{"type": "WARNING",
                                   "severity": "LOW",
                                   "location": "customerService.ts:createCustomer",
                                   "issue": "Email validation not implemented",
                                   "recommendation": "Add email format validation before database insert"},
                                  {"type": "WARNING",
                                   "severity": "LOW",
                                   "location": "orderService.ts:calculateTotal",
                                   "issue": "Private method lacks input validation",
                                   "recommendation": "Add validation for item structure and numeric values"},
                                  {"type": "WARNING",
                                   "severity": "MEDIUM",
                                   "location": "Both services",
                                   "issue": "Audit logging not implemented",
                                   "recommendation": "Consider adding audit trails for compliance"},
                                  {"type": "RECOMMENDATION",
                                   "severity": "INFO",
                                   "location": "customerService.ts",
                                   "issue": "Cache opportunities for customer lookups",
                                   "recommendation": "Implement Redis caching for frequently accessed customers"},
                                  {"type": "RECOMMENDATION",
                                   "severity": "INFO",
                                   "location": "orderService.ts",
                                   "issue": "Batch operations support",
                                   "recommendation": "Add bulk order creation for better performance"}],
            "test_recommendations": [{"type": "UNIT_TEST",
                                      "priority": "HIGH",
                                      "description": "Test all CRUD operations with valid and invalid data",
                                      "estimated_effort": "4 hours"},
                                     {"type": "INTEGRATION_TEST",
                                      "priority": "HIGH",
                                      "description": "Test RLS policies and authentication flows",
                                      "estimated_effort": "3 hours"},
                                     {"type": "PERFORMANCE_TEST",
                                      "priority": "MEDIUM",
                                      "description": "Load test with realistic data volumes",
                                      "estimated_effort": "2 hours"}],
            "approval_status": "APPROVED_WITH_MINOR_FIXES",
            "next_actions": ["Implement email validation in customer service",
                             "Add input validation to private methods",
                             "Create comprehensive test suite",
                             "Document API usage examples"]}


def demo_step_4_4():
    """Main demo function for Step 4.4 functionality."""
    print("🚀 Step 4.4 — Register Agent Output Demo")
    print("=" * 60)
    print("This demo showcases the complete agent output registration system")
    print("for storing, tracking, and preparing agent outputs for downstream processing.")

    # Create temporary demo environment
    demo_dir = tempfile.mkdtemp(prefix="step_4_4_demo_")
    print(f"\n📁 Demo environment: {demo_dir}")

    try:
        # Initialize registry
        registry = AgentOutputRegistry(base_outputs_dir=demo_dir)
        print_success("Agent output registry initialized")

        # Demo 1: Register Backend Agent Output
        print_section(
            "Demo 1: Backend Agent Output Registration with Code Extraction")

        # Create backend output file
        backend_content = create_realistic_backend_output()
        backend_file = Path(demo_dir) / "backend_output_BE-07.md"
        backend_file.write_text(backend_content, encoding='utf-8')

        print_info(f"Created backend output file: {backend_file.name}")
        print_info(f"File size: {len(backend_content):,} characters")

        # Register with code extraction
        backend_registration = registry.register_output(
            task_id="BE-07",
            agent_id="backend",
            source_path=str(backend_file),
            output_type="markdown",
            extract_code=True,
            metadata={
                "execution_time": 125.4,
                "model": "gpt-4",
                "tokens_used": 2847,
                "agent_version": "1.2.0"
            }
        )

        print_success(f"Backend output registered successfully")
        print_info(f"  📄 Output file: {backend_registration.output_path}")
        print_info(
            f"  📦 Extracted {len(backend_registration.extracted_artifacts)} code artifacts")
        print_info(
            f"  ⏰ Registration time: {backend_registration.registration_time}")

        # Show extracted artifacts
        if backend_registration.extracted_artifacts:
            print_info("  🔧 Extracted code files:")
            for artifact in backend_registration.extracted_artifacts:
                artifact_name = Path(artifact).name
                artifact_size = Path(artifact).stat().st_size
                print(f"     - {artifact_name} ({artifact_size} bytes)")

        # Demo 2: Register QA Agent Output
        print_section("Demo 2: QA Agent Output Registration")

        # Create QA report
        qa_data = create_realistic_qa_report()
        qa_file = Path(demo_dir) / "qa_report_BE-07.json"
        qa_file.write_text(json.dumps(qa_data, indent=2), encoding='utf-8')

        print_info(f"Created QA report file: {qa_file.name}")
        print_info(
            f"QA Status: {qa_data['analysis_summary']['overall_status']}")
        print_info(
            f"Quality Score: {
                qa_data['analysis_summary']['code_quality_score']}/100")

        # Register QA output
        qa_registration = registry.register_output(
            task_id="BE-07",
            agent_id="qa",
            source_path=str(qa_file),
            output_type="json",
            metadata={
                "analysis_duration": 45.2,
                "qa_agent_version": "2.1.0",
                "checks_performed": 23
            }
        )

        print_success("QA output registered successfully")
        print_info(f"  📊 Report file: {qa_registration.output_path}")
        print_info(
            f"  🔍 Analysis complete with {
                qa_data['analysis_summary']['warnings']} warnings")

        # Demo 3: Status Tracking
        print_section("Demo 3: Task Status Tracking")

        task_status = registry.get_task_status("BE-07")
        print_info(f"Task ID: {task_status['task_id']}")
        print_info(f"Last Updated: {task_status['last_updated']}")
        print_info(f"Agent Outputs: {len(task_status['agent_outputs'])}")

        for agent_id, agent_info in task_status['agent_outputs'].items():
            print(f"  🤖 {agent_id.upper()} Agent:")
            print(f"     Status: {agent_info['status']}")
            print(f"     File: {agent_info['output_file']}")
            print(f"     Size: {agent_info['file_size']:,} bytes")
            if agent_info['extracted_artifacts'] > 0:
                print(
                    f"     Artifacts: {
                        agent_info['extracted_artifacts']} files")

        # Demo 4: QA Input Preparation
        print_section("Demo 4: QA Input Preparation for Downstream Agents")

        qa_input = registry.prepare_qa_input("BE-07")
        print_info(f"Prepared QA input for task: {qa_input['task_id']}")
        print_info(
            f"Primary outputs: {len(qa_input['primary_outputs'])} files")
        print_info(f"Code artifacts: {len(qa_input['code_artifacts'])} files")

        print_info("📄 Primary Outputs:")
        for output in qa_input['primary_outputs']:
            output_file = Path(output['file']).name
            content_preview = output['content'][:100] + \
                "..." if len(output['content']) > 100 else output['content']
            print(f"   - {output_file}")
            print(f"     Preview: {content_preview}")

        print_info("🔧 Code Artifacts:")
        for artifact in qa_input['code_artifacts']:
            artifact_file = Path(artifact['file']).name
            print(f"   - {artifact_file} ({artifact['language']})")
            print(f"     Size: {len(artifact['content'])} characters")

        # Demo 5: Output Listing
        print_section("Demo 5: Output File Management")

        outputs = registry.list_task_outputs("BE-07")
        print_info(f"Total output files for BE-07: {len(outputs)}")

        for output_path in outputs:
            file_path = Path(output_path)
            file_size = file_path.stat().st_size
            print(f"  📁 {file_path.name} ({file_size:,} bytes)")

        # Demo 6: Integration Example
        print_section("Demo 6: Integration with Downstream Agents")

        print_info("🔄 Workflow Integration Points:")
        print("  1. ✅ Backend Agent → Output Registered → Code Extracted")
        print("  2. ✅ QA Agent → Analysis Complete → Report Generated")
        print("  3. 🔄 Next: Documentation Agent (ready for input)")
        print("  4. 🔄 Next: Code Review Agent (code artifacts available)")
        print("  5. 🔄 Next: Integration Testing (artifacts ready)")

        # Show integration readiness
        integration_readiness = {
            "backend_output": "✅ Available",
            "qa_analysis": "✅ Complete",
            "code_artifacts": f"✅ {len(qa_input['code_artifacts'])} files ready",
            "status_tracking": "✅ Active",
            "downstream_ready": "✅ All inputs prepared"
        }

        print_info("🎯 Integration Readiness:")
        for component, status in integration_readiness.items():
            print(f"   {component.replace('_', ' ').title()}: {status}")

        # Final Summary
        print_section("Demo Summary: Step 4.4 Implementation Complete")

        summary_stats = {
            "Total Outputs Registered": len(
                task_status['agent_outputs']),
            "Code Artifacts Extracted": len(
                backend_registration.extracted_artifacts),
            "QA Analysis Complete": "✅ PASSED_WITH_RECOMMENDATIONS",
            "Status Tracking": "✅ Active",
            "Downstream Integration": "✅ Ready",
            "File Management": "✅ Organized",
            "Metadata Tracking": "✅ Complete"}

        print_success(
            "Step 4.4 — Register Agent Output implementation validated successfully!")
        print_info("📊 Demo Results:")
        for metric, value in summary_stats.items():
            print(f"   {metric}: {value}")

        print_info("🔄 Ready for Phase 5: Reporting, QA & Completion")

        return {
            "success": True,
            "demo_dir": demo_dir,
            "backend_registration": backend_registration,
            "qa_registration": qa_registration,
            "task_status": task_status,
            "qa_input": qa_input,
            "summary_stats": summary_stats
        }

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        # Clean up demo environment
        print(f"\n🧹 Cleaning up demo environment: {demo_dir}")
        try:
            shutil.rmtree(demo_dir)
            print_success("Demo environment cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up demo directory: {e}")


if __name__ == "__main__":
    print("🎬 Starting Step 4.4 — Register Agent Output Demo")
    print("This demo will showcase the complete agent output registration system.\n")

    # Run the demo
    demo_results = demo_step_4_4()

    # Exit with appropriate code
    if demo_results.get("success", False):
        print("\n🎉 Demo completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Demo failed: {demo_results.get('error', 'Unknown error')}")
        sys.exit(1)
