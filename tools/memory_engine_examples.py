#!/usr/bin/env python3
"""
Example script demonstrating how to initialize and query the vector store (Chroma) using memory_engine.py.
This shows how to index knowledge with vector embeddings.
"""

import os
from typing import List

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings

from tools.memory_engine import initialize_memory, memory


def index_knowledge_with_chroma():
    """
    Example function demonstrating how to index knowledge with vector embeddings using Chroma,
    similar to the system implementation specification.
    """
    print("Index Knowledge with Vector Embeddings")
    print("\nSet Up Vector Store (Chroma)")

    # Path to the document to index
    doc_path = "context-store/db/db-schema-summary.md"

    # Check if the directory and file exist, create if not
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    if not os.path.exists(doc_path):
        print(f"Creating example file: {doc_path}")
        with open(doc_path, "w") as f:
            f.write("""## Tables
- users: id, name, email
- orders: id, user_id, status, created_at

## Relationships
- users 1---* orders

## RLS Policy
- Users can only access their own orders""")

    print(f"Loading document: {doc_path}")
    # Load the document
    try:
        loader = TextLoader(doc_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents")

        # Create embeddings for the documents
        embedding = OpenAIEmbeddings(model="text-embedding-3-small")

        # Create and initialize the vector store
        db = Chroma.from_documents(
            documents=docs,
            embedding=embedding,
            collection_name="project_knowledge",
            persist_directory="./chroma_db"
        )
        print(f"Created Chroma vector store with {len(docs)} documents")

        # Demonstrate a similarity search
        query = "What tables are in the database?"
        print(f"\nQuerying the vector store with: '{query}'")
        similar_docs = db.similarity_search(query, k=2)

        print("\nSearch Results:")
        for i, doc in enumerate(similar_docs):
            print(f"\nDocument {i + 1}:")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")

        # Alternatively, use the memory_engine's interface
        print("\nUsing memory_engine.py to query:")
        context = memory.get_context(query, k=2)
        print(f"Retrieved context: {context[:200]}...")

        return db
    except Exception as e:
        print(f"Error in index_knowledge_with_chroma: {e}")
        raise


def add_document_example():
    """Example showing how to add a document to the memory engine."""
    doc_path = "context-store/examples/example-doc.md"
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)

    # Create an example document if it doesn't exist
    if not os.path.exists(doc_path):
        with open(doc_path, "w") as f:
            f.write("""# Example Document
This is a test document for demonstrating the memory engine.

## Features
- Vector embeddings
- Semantic search
- Document chunking
""")

    # Add the document to memory engine
    print(f"\nAdding document: {doc_path}")
    memory.add_document(doc_path, metadata={
                        "type": "example", "purpose": "demo"})

    # Query the added document
    query = "What are the features of the memory engine?"
    print(f"\nQuerying for: '{query}'")
    context = memory.get_context(query)
    print(f"Retrieved context: {context}")


def initialize_and_search_example():
    """Example showing how to initialize memory and search."""
    print("\nInitializing memory from context-store directory")
    initialize_memory()

    # Query the memory
    query = "What is the database schema?"
    print(f"\nQuerying for: '{query}'")
    context = memory.get_context(query)
    print(f"Retrieved context: {context[:200]}...")


if __name__ == "__main__":
    print("Memory Engine Vector Embeddings Example")
    print("======================================")

    # Example 1: Index knowledge with Chroma
    chroma_db = index_knowledge_with_chroma()

    # Example 2: Add a document through memory engine
    add_document_example()

    # Example 3: Initialize and search
    initialize_and_search_example()

    print("\nExamples completed successfully")
