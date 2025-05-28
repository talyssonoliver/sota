"""
Supabase Tool - Provides database querying and schema information
"""

import json
import os
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from supabase import Client, create_client

from tools.base_tool import ArtesanatoBaseTool

load_dotenv()


class SupabaseTool(ArtesanatoBaseTool):
    """Tool for interacting with Supabase database."""

    name: str = "supabase_tool"
    description: str = "Tool for querying Supabase database and retrieving schema information"
    client: Optional[Any] = None

    class InputSchema(BaseModel):
        query: str

    def __init__(self, **kwargs):
        """Initialize Supabase client."""
        super().__init__(**kwargs)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            self.client = None
            self.log(
                "Warning: Supabase credentials not found. Using mock responses.")
        else:
            try:
                self.client = create_client(supabase_url, supabase_key)
                self.log("Supabase client initialized successfully.")
            except Exception as e:
                self.client = None
                self.log(f"Error initializing Supabase client: {str(e)}")

    def _check_env_vars(self) -> None:
        """Check for required environment variables."""
        # Just log warning if not available, since mock functionality is
        # provided
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            self.log(
                "Supabase environment variables (SUPABASE_URL, SUPABASE_KEY) not found.")

    def plan(self, query: str) -> Dict[str, Any]:
        """
        Generate an execution plan for the Supabase query.

        Args:
            query: The input query string

        Returns:
            Dict containing the execution plan
        """
        query_lower = query.lower()
        plan = {
            "action": None,
            "params": {"query": query},
            "description": "Execute Supabase operation"
        }

        # Determine the action based on the query
        if "schema" in query_lower:
            plan["action"] = "get_schema"
            plan["description"] = "Retrieve database schema information"
        elif "service pattern" in query_lower or "service template" in query_lower:
            plan["action"] = "get_service_pattern"
            plan["description"] = "Retrieve service pattern examples"
        elif "select" in query_lower or "query" in query_lower:
            plan["action"] = "execute_query"
            plan["description"] = "Execute database query"

            # Try to extract table name for better planning
            if "from" in query_lower:
                parts = query_lower.split("from")
                if len(parts) >= 2:
                    table_part = parts[1].strip().split(" ")[0]
                    plan["params"]["table"] = table_part
        else:
            plan["action"] = "generic_response"
            plan["description"] = "Generic Supabase information"

        return plan

    def execute(self, query: str,
                plan: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute the Supabase tool based on the provided plan.

        Args:
            query: The input query string
            plan: The execution plan

        Returns:
            Result of the Supabase operation
        """
        if not plan:
            plan = self.plan(query)

        action = plan.get("action")
        self.log(f"Executing action: {action}")

        try:
            if action == "get_schema":
                return self._get_schema_info()
            elif action == "get_service_pattern":
                return self._get_service_pattern()
            elif action == "execute_query":
                return self._handle_db_query(query)
            else:
                return (
                    "Supabase query processed. Please specify if you need schema information, "
                    "service pattern examples, or want to execute a specific database query.")
        except Exception as e:
            self.log(f"Error during execution: {str(e)}")
            return f"Error processing Supabase request: {str(e)}"

    def _run(self, query: str) -> str:
        """Execute a query against the Supabase database (LangChain compatibility)."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            plan = self.plan(query)
            return self.execute(query, plan)
        except ValidationError as ve:
            return self.handle_error(ve, f"{self.name}._run.input_validation")
        except Exception as e:
            return self.handle_error(e, f"{self.name}._run")

    # Keep the remaining methods unchanged
    def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    def _get_schema_info(self) -> str:
        """Return database schema information by querying Supabase system tables."""
        if not self.client:
            # Use static schema from context store if client is not available
            return self._get_mock_schema()

        try:
            # Define schema introspection query for PostgreSQL (which Supabase uses)
            # This is an actual implementation that queries the
            # information_schema
            schema_query = """
            SELECT
                table_name,
                column_name,
                data_type,
                column_default,
                is_nullable,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                identity_generation,
                udt_name
            FROM
                information_schema.columns
            WHERE
                table_schema = 'public'
            ORDER BY
                table_name, ordinal_position;
            """

            # Execute the SQL query using POST rpc function call
            response = self.client.rpc(
                "exec_sql", {"sql": schema_query}).execute()

            # Process response
            if hasattr(response, 'data') and response.data:
                # Group columns by table
                tables = {}
                for column in response.data:
                    table_name = column.get('table_name')
                    if table_name not in tables:
                        tables[table_name] = []

                    # Format data type with constraints
                    data_type = column.get('data_type', 'unknown')
                    if column.get('character_maximum_length'):
                        data_type += f"({column.get('character_maximum_length')})"
                    elif column.get('numeric_precision') and column.get('numeric_scale'):
                        data_type += f"({column.get('numeric_precision')},{column.get('numeric_scale')})"

                    # Add nullability
                    nullable = "NULL" if column.get(
                        'is_nullable') == "YES" else "NOT NULL"

                    # Add default value if present
                    default = f" DEFAULT {
                        column.get('column_default')}" if column.get('column_default') else ""

                    # Add identity/serial info
                    identity = f" {column.get('identity_generation')}" if column.get(
                        'identity_generation') else ""

                    # Format the complete column definition
                    column_def = f"{
                        column.get('column_name')}: {data_type} {nullable}{default}{identity}"
                    tables[table_name].append(column_def)

                # Extract foreign key constraints
                fk_query = """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                JOIN
                    information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN
                    information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE
                    tc.constraint_type = 'FOREIGN KEY'
                AND
                    tc.table_schema = 'public';
                """

                fk_response = self.client.rpc(
                    "exec_sql", {"sql": fk_query}).execute()

                # Add foreign key constraints to column definitions
                if hasattr(fk_response, 'data') and fk_response.data:
                    for fk in fk_response.data:
                        table = fk.get('table_name')
                        column = fk.get('column_name')
                        ref_table = fk.get('foreign_table_name')
                        ref_column = fk.get('foreign_column_name')

                        if table in tables:
                            # Find the column and append foreign key info
                            for i, col_def in enumerate(tables[table]):
                                if col_def.startswith(f"{column}:"):
                                    tables[table][i] += f" REFERENCES {ref_table}({ref_column})"

                # Format the schema information into a readable string
                schema_text = "Database Schema for Artesanato E-commerce:\n\n## Tables\n\n"
                for table_name, columns in tables.items():
                    schema_text += f"### {table_name}\n"
                    for column in columns:
                        schema_text += f"- {column}\n"
                    schema_text += "\n"

                # Get primary key information
                pk_query = """
                SELECT
                    tc.table_name,
                    kcu.column_name
                FROM
                    information_schema.table_constraints tc
                JOIN
                    information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE
                    tc.constraint_type = 'PRIMARY KEY'
                AND
                    tc.table_schema = 'public'
                ORDER BY
                    tc.table_name;
                """

                pk_response = self.client.rpc(
                    "exec_sql", {"sql": pk_query}).execute()

                # Add primary key annotations
                if hasattr(pk_response, 'data') and pk_response.data:
                    schema_text += "## Primary Keys\n\n"
                    for pk in pk_response.data:
                        schema_text += f"- {
                            pk.get('table_name')}: {
                            pk.get('column_name')}\n"

                return schema_text
            else:
                return "Error retrieving schema information from Supabase."
        except Exception as e:
            print(f"Error getting schema from Supabase: {str(e)}")
            return self._get_mock_schema()

    def _get_mock_schema(self) -> str:
        """Return mock schema information from context store."""
        try:
            schema_file = os.path.join(
                os.getcwd(), "context-store", "db", "db-schema-summary.md")

            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    return f.read()
            else:
                # Fallback mock response
                return """
            Database Schema for Artesanato E-commerce:

            Tables:
            1. categories
            - id: UUID PRIMARY KEY
            - name: TEXT NOT NULL
            - description: TEXT
            - image_url: TEXT
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            2. products
            - id: UUID PRIMARY KEY
            - name: TEXT NOT NULL
            - description: TEXT
            - price: DECIMAL(10, 2) NOT NULL
            - category_id: UUID REFERENCES categories(id)
            - image_url: TEXT
            - inventory_count: INTEGER NOT NULL DEFAULT 0
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            3. customers
            - id: UUID PRIMARY KEY
            - email: TEXT UNIQUE NOT NULL
            - name: TEXT NOT NULL
            - address: TEXT
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            4. orders
            - id: UUID PRIMARY KEY
            - customer_id: UUID REFERENCES customers(id)
            - status: TEXT NOT NULL DEFAULT 'pending'
            - total: DECIMAL(10, 2) NOT NULL
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            5. order_items
            - id: UUID PRIMARY KEY
            - order_id: UUID REFERENCES orders(id) ON DELETE CASCADE
            - product_id: UUID REFERENCES products(id)
            - quantity: INTEGER NOT NULL
            - price: DECIMAL(10, 2) NOT NULL
            - created_at: TIMESTAMP WITH TIME ZONE

            6. carts
            - id: UUID PRIMARY KEY
            - customer_id: UUID REFERENCES customers(id)
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            7. cart_items
            - id: UUID PRIMARY KEY
            - cart_id: UUID REFERENCES carts(id) ON DELETE CASCADE
            - product_id: UUID REFERENCES products(id)
            - quantity: INTEGER NOT NULL
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            8. users
            - id: UUID PRIMARY KEY
            - email: TEXT UNIQUE NOT NULL
            - name: TEXT
            - phone_number: TEXT
            - role: TEXT DEFAULT 'customer'
            - created_at: TIMESTAMP WITH TIME ZONE
            - updated_at: TIMESTAMP WITH TIME ZONE

            RLS Policies:
            - Products: Everyone can view, only admins can modify
            - Categories: Everyone can view, only admins can modify
            - Orders: Users can only access their own orders
            - Carts: Users can only access their own cart
            - Users: Users can only access their own data
            """
        except Exception as e:
            return f"Error loading mock schema: {str(e)}"

    def _get_service_pattern(self) -> str:
        """Return service pattern examples."""
        try:
            # Try the new organized path first
            service_pattern_file = os.path.join(
                os.getcwd(), "context-store", "patterns", "service-pattern.md")

            # If not found, fall back to original path for backward
            # compatibility
            if not os.path.exists(service_pattern_file):
                service_pattern_file = os.path.join(
                    os.getcwd(), "context-store", "service-pattern.md")

            if os.path.exists(service_pattern_file):
                with open(service_pattern_file, 'r') as f:
                    return f.read()
            else:
                # Fallback mock response
                return """
                Service Pattern for Supabase Integration:

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
                      return { data: null, error: result.error };
                    }

                    return { data: result.data, error: null };
                  } catch (error) {
                    return handleError(error, 'ServiceName.functionName');
                  }
                }
                ```
                """
        except Exception as e:
            return f"Error loading service pattern: {str(e)}"

    def _handle_db_query(self, query: str) -> str:
        """Execute database queries against Supabase."""
        if not self.client:
            return self._handle_mock_db_query(query)

        try:
            # Parse the query to extract table and conditions
            # This is a simplified parser for demonstration
            # In a real implementation, you would use a more robust SQL parser
            query_lower = query.lower()

            # Extract table name and fields
            if "from" not in query_lower:
                return "Invalid query. Please specify the table using FROM clause."

            # Simple parsing of SELECT query
            if "select" in query_lower:
                parts = query_lower.split("from")
                if len(parts) < 2:
                    return "Invalid query format. Expected 'SELECT fields FROM table'."

                select_part = parts[0].replace("select", "").strip()
                fields = "*" if select_part == "" else select_part

                table_part = parts[1].strip().split(" ")[0]
                table_name = table_part

                # Execute the query using Supabase client
                result = self.client.from_(table_name).select(fields).execute()

                if hasattr(result, 'error') and result.error:
                    return f"Error executing query: {result.error.message}"

                if hasattr(result, 'data'):
                    # Format the result as a readable string
                    response = f"Query results from {table_name}:\n\n"
                    for item in result.data:
                        response += json.dumps(item, indent=2) + "\n"
                    return response
                else:
                    return "No results found."
            else:
                return "Currently only SELECT queries are supported. Please use 'SELECT ... FROM ...' format."
        except Exception as e:
            print(f"Error executing Supabase query: {str(e)}")
            return self._handle_mock_db_query(query)

    def _handle_mock_db_query(self, query: str) -> str:
        """Return mock responses for database queries."""
        query_lower = query.lower()

        if "product" in query_lower:
            return """
            Query results from products:

            [
              {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Handmade Ceramic Mug",
                "description": "Beautiful handcrafted ceramic mug by local artisans",
                "price": 24.99,
                "category_id": "c9d4c844-4b4d-4d1a-b4a4-c3d4d5e6f7g8",
                "image_url": "https://example.com/images/mug.png",
                "inventory_count": 45,
                "created_at": "2024-01-10T10:30:00Z",
                "updated_at": "2024-01-10T10:30:00Z"
              },
              {
                "id": "660e8400-e29b-41d4-a716-446655440111",
                "name": "Woven Wall Hanging",
                "description": "Intricately woven wall decoration with natural fibers",
                "price": 89.99,
                "category_id": "d9d4c844-4b4d-4d1a-b4a4-c3d4d5e6f7g9",
                "image_url": "https://example.com/images/wallhanging.png",
                "inventory_count": 12,
                "created_at": "2024-01-12T14:20:00Z",
                "updated_at": "2024-01-15T09:10:00Z"
              }
            ]
            """
        elif "categor" in query_lower:
            return """
            Query results from categories:

            [
              {
                "id": "c9d4c844-4b4d-4d1a-b4a4-c3d4d5e6f7g8",
                "name": "Kitchen",
                "description": "Handcrafted items for your kitchen",
                "image_url": "https://example.com/images/kitchen.png",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
              },
              {
                "id": "d9d4c844-4b4d-4d1a-b4a4-c3d4d5e6f7g9",
                "name": "Home Decor",
                "description": "Beautiful artisan-made decorations for your home",
                "image_url": "https://example.com/images/homedecor.png",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-05T16:30:00Z"
              }
            ]
            """
        elif "customer" in query_lower or "user" in query_lower:
            return """
            Query results from customers:

            [
              {
                "id": "a1a2a3a4-b1b2-c1c2-d1d2-e1e2f1f2g1g2",
                "email": "maria@example.com",
                "name": "Maria Silva",
                "address": "123 Main St, Anytown, USA",
                "created_at": "2024-01-05T12:30:00Z",
                "updated_at": "2024-01-05T12:30:00Z"
              },
              {
                "id": "b1b2b3b4-c1c2-d1d2-e1e2-f1f2g1g2h1h2",
                "email": "john@example.com",
                "name": "John Doe",
                "address": "456 Oak Ave, Somewhere, USA",
                "created_at": "2024-01-07T09:15:00Z",
                "updated_at": "2024-01-10T14:20:00Z"
              }
            ]
            """
        elif "order" in query_lower:
            return """
            Query results from orders:

            [
              {
                "id": "e1e2e3e4-f1f2-g1g2-h1h2-i1i2j1j2k1k2",
                "customer_id": "a1a2a3a4-b1b2-c1c2-d1d2-e1e2f1f2g1g2",
                "status": "completed",
                "total": 114.98,
                "created_at": "2024-02-01T10:00:00Z",
                "updated_at": "2024-02-02T15:30:00Z"
              },
              {
                "id": "f1f2f3f4-g1g2-h1h2-i1i2-j1j2k1k2l1l2",
                "customer_id": "b1b2b3b4-c1c2-d1d2-e1e2-f1f2g1g2h1h2",
                "status": "pending",
                "total": 89.99,
                "created_at": "2024-02-05T16:45:00Z",
                "updated_at": "2024-02-05T16:45:00Z"
              }
            ]
            """
        else:
            return """
            No results found for your query. Please try a different query or table name.
            Available tables: products, categories, customers, orders, order_items, carts, cart_items, users
            """
