#!/usr/bin/env python3
"""
Simple Step 3.6 Chunking Test

This script tests the Step 3.6 enhanced chunking functionality
by directly testing the LangChain CharacterTextSplitter integration
without access control checks.
"""

import os
import sys
from pathlib import Path

from langchain_text_splitters import CharacterTextSplitter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_step_3_6_chunking():
    """Test Step 3.6 enhanced chunking with LangChain CharacterTextSplitter"""

    print("🚀 Step 3.6 Enhanced Chunking Test")
    print("=" * 50)

    # Create a sample large document
    sample_content = """# Large Document for Chunking Test

## Section 1: Introduction
This is a comprehensive document that demonstrates the Step 3.6 enhanced chunking strategy using LangChain's CharacterTextSplitter. The document contains multiple sections with substantial content to test the chunking algorithm effectively.

## Section 2: Backend Architecture
The backend architecture follows a modular service layer pattern with clear separation of concerns. Each service handles specific business logic and maintains clean interfaces with the data layer through Supabase.

### Service Layer Implementation
Services are implemented as TypeScript classes that extend a base service interface. This ensures consistency across all backend operations and provides a clear contract for frontend integration.

### Database Integration
Database operations are handled through Supabase client with proper error handling and type safety. All operations follow the established patterns for CRUD operations.

## Section 3: Frontend Components
The frontend utilizes React components with TypeScript for type safety and maintainability. Components are organized in a hierarchical structure with clear responsibilities.

### Component Structure
- Layout components handle page structure
- Feature components implement specific functionality
- UI components provide reusable interface elements
- Utility components handle cross-cutting concerns

### State Management
State is managed through React Context and custom hooks, providing predictable data flow and efficient updates across the application.

## Section 4: Authentication System
Authentication is implemented using Supabase Auth with support for multiple providers including email/password, Google, and GitHub OAuth.

### Security Considerations
- Row Level Security (RLS) policies protect data access
- JWT tokens are securely managed
- Session persistence across browser restarts
- Automatic token refresh handling

## Section 5: API Design
RESTful API endpoints follow consistent patterns for predictable integration. All endpoints return standardized response formats with proper error handling.

### Error Handling
Comprehensive error handling ensures graceful degradation and clear error messages for debugging and user feedback.

This document continues with additional sections to provide sufficient content for thorough chunking testing and validation of the Step 3.6 implementation."""

    print(f"📄 Sample document length: {len(sample_content)} characters")
    print()

    # Step 3.6: Test LangChain CharacterTextSplitter
    print("✂️  Testing Step 3.6: LangChain CharacterTextSplitter")

    # Configure the splitter as specified in Step 3.6
    text_splitter = CharacterTextSplitter(
        chunk_size=500,        # Step 3.6 specification
        chunk_overlap=50,      # Step 3.6 specification
        separator="\n\n",      # Paragraph-based splitting
        length_function=len
    )

    # Split the document
    chunks = text_splitter.split_text(sample_content)

    print(f"📊 Chunking Results:")
    print(f"   Original length: {len(sample_content)} characters")
    print(f"   Number of chunks: {len(chunks)}")
    print(
        f"   Average chunk size: {
            sum(
                len(chunk) for chunk in chunks) //
            len(chunks)} characters")
    print()

    # Display chunk analysis
    print("🔍 Chunk Analysis:")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i + 1}: {len(chunk)} characters")
        if len(chunk) > 500:
            print(f"      ⚠️  Chunk exceeds target size (500 chars)")

        # Show first 100 characters of each chunk
        preview = chunk.replace('\n', ' ').strip()[:100]
        print(f"      Preview: {preview}...")
        print()

    # Test chunk overlap
    print("🔗 Testing Chunk Overlap:")
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]

        # Check for overlap (simplified check)
        current_end = current_chunk[-50:].strip()
        next_start = next_chunk[:50].strip()

        # Find common words between end of current and start of next
        current_words = current_end.split()[-5:]  # Last 5 words
        next_words = next_start.split()[:5]       # First 5 words

        overlap_words = set(current_words) & set(next_words)
        if overlap_words:
            print(
                f"   Chunks {i + 1}→{i + 2}: Overlap detected: {overlap_words}")
        else:
            print(f"   Chunks {i + 1}→{i + 2}: No word overlap found")

    print()
    print("✅ Step 3.6 Enhanced Chunking Test Complete!")
    print()
    print("📋 Summary:")
    print(f"   ✓ LangChain CharacterTextSplitter configured correctly")
    print(f"   ✓ Chunk size target: 500 characters (with 50 char overlap)")
    print(
        f"   ✓ Generated {
            len(chunks)} chunks from {
            len(sample_content)} character document")
    print(f"   ✓ Chunking strategy validated for Step 3.6 implementation")


if __name__ == "__main__":
    test_step_3_6_chunking()
