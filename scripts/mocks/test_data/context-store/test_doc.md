# Test Document

This is a test document used for testing the memory engine and retrieval QA functionality.

## Supabase RLS Rules

The orders table has RLS rules that restrict users to only see their own orders.
These rules are implemented using row-level security policies.

## Authentication

Authentication is handled via JWT tokens. When a user logs in, a JWT token is generated
that contains the user's ID and role. This token is then used for all subsequent requests.

## Security

The system uses several security measures:
- Row-level security (RLS) in Supabase
- JWT token authentication
- HTTPS for all communications
- Input sanitization to prevent SQL injection
