"""
Memory Engine for MCP (Model Context Protocol)
Provides context storage and retrieval for agents.
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MemoryEngine:
    def __init__(
        self,
        collection_name: str = "agent_memory",
        knowledge_base_path: str = "context-store/",
        embedding_model: str = "text-embedding-3-small"
    ):
        """Initialize the memory engine with configurable paths and embedding model."""
        self.knowledge_base_path = knowledge_base_path
        self.embedding_model = embedding_model
        self.embedding_function = OpenAIEmbeddings(model=embedding_model)
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_function,
            persist_directory="./chroma_db"
        )
        self.text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def add_document(self, file_path: str, metadata: Optional[dict] = None) -> None:
        """Add a single document to the vector store, with optional metadata."""
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            split_docs = self.text_splitter.split_documents(documents)
            # Attach metadata if provided
            if metadata:
                for doc in split_docs:
                    doc.metadata = metadata
            self.vector_store.add_documents(split_docs)
            print(f"Added document: {file_path}")
        except Exception as e:
            print(f"Error adding document {file_path}: {str(e)}")

    def add_directory(self, directory_path: str, glob: str = "**/*.md", metadata: Optional[dict] = None) -> None:
        """Add all documents in a directory to the vector store, with optional metadata."""
        try:
            loader = DirectoryLoader(directory_path, glob=glob)
            documents = loader.load()
            split_docs = self.text_splitter.split_documents(documents)
            if metadata:
                for doc in split_docs:
                    doc.metadata = metadata
            self.vector_store.add_documents(split_docs)
            print(f"Added {len(documents)} documents from {directory_path}")
        except Exception as e:
            print(f"Error adding directory {directory_path}: {str(e)}")

    def scan_and_summarize(self, source_dirs: List[str] = None, summary_dir: str = "context-store/") -> None:
        """
        Generate summaries from source documents and store them in summary_dir.
        
        Args:
            source_dirs: List of directories to scan for source documents (defaults to context-source/)
            summary_dir: Directory to store the generated summaries
        """
        if source_dirs is None:
            # Default to the context-source directory
            source_dirs = ["context-source/"]
            
        for source_dir in source_dirs:
            if not os.path.exists(source_dir):
                print(f"Source directory {source_dir} not found. Skipping.")
                continue
                
            print(f"Processing source directory: {source_dir}")
            for root, _, files in os.walk(source_dir):
                for fname in files:
                    if fname.endswith('.md') or fname.endswith('.txt') or fname.endswith('.yaml'):
                        # Determine the appropriate target location in context-store
                        src_path = os.path.join(root, fname)
                        
                        # Skip if this is already in the context-store directory
                        if summary_dir in src_path:
                            continue
                        
                        # Determine the domain/category based on the source directory or file type
                        rel_dir = os.path.relpath(root, source_dir)
                        if rel_dir == ".":
                            # File is in the root of source_dir
                            domain = self._determine_domain_from_filename(fname)
                        else:
                            # Use the subdirectory name as domain
                            domain = rel_dir.split(os.sep)[0]
                        
                        # Generate the summary
                        try:
                            with open(src_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            summary = self.summarize_document(content)
                            
                            # Create a meaningful name for the summary
                            base_name = os.path.splitext(fname)[0]
                            summary_filename = f"{base_name}-summary.md"
                            summary_path = os.path.join(summary_dir, domain, summary_filename)
                            
                            # Ensure the directory exists
                            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
                            
                            # Add "Not yet reviewed" marker at the top
                            if not summary.startswith("# "):
                                title = base_name.replace("-", " ").title()
                                summary = f"# {title} Summary\n**Reviewed: Not yet reviewed**\n\n{summary}"
                            else:
                                # Insert the review status after the title
                                lines = summary.split("\n", 1)
                                summary = f"{lines[0]}\n**Reviewed: Not yet reviewed**\n\n{lines[1] if len(lines) > 1 else ''}"
                            
                            # Add attribution at the bottom
                            if not "Drafted by doc_agent" in summary:
                                current_date = os.getenv('CURRENT_DATE', 'May 16, 2025')
                                summary += f"\n\n---\n*Drafted by doc_agent on {current_date}. Appropriate domain expert: please review for accuracy and completeness.*"
                            
                            # Save the summary
                            with open(summary_path, 'w', encoding='utf-8') as f:
                                f.write(summary)
                                
                            print(f"Summarized {src_path} -> {summary_path}")
                        except Exception as e:
                            print(f"Error processing {src_path}: {str(e)}")
        
        # Index the generated summaries
        self.index_summaries(summary_dir)

    def _determine_domain_from_filename(self, filename: str) -> str:
        """Helper method to determine the domain based on filename patterns."""
        filename = filename.lower()
        if any(term in filename for term in ['db', 'schema', 'database']):
            return 'db'
        elif any(term in filename for term in ['service', 'api', 'pattern']):
            return 'patterns'
        elif any(term in filename for term in ['architecture', 'system', 'design']):
            return 'technical'
        elif any(term in filename for term in ['sprint', 'plan', 'roadmap']):
            return 'sprint'
        elif any(term in filename for term in ['ui', 'ux', 'interface']):
            return 'design'
        elif any(term in filename for term in ['infra', 'deploy', 'cloud']):
            return 'infra'
        else:
            return 'general'

    def summarize_document(self, content: str, max_length: int = 2000) -> str:
        """Summarize a document if it's too large. (Stub: replace with LLM call if needed)"""
        if len(content) > max_length:
            # Simple extractive summary: take first and last N chars
            return content[:max_length//2] + '\n...\n' + content[-max_length//2:]
        return content

    def index_summaries(self, summary_dir: str = "context-store/") -> None:
        """Index all summaries in summary_dir into the vector store."""
        self.add_directory(summary_dir)

    def get_filtered_context(self, query: str, filters: List[str], k: int = 5, use_metadata: bool = True, use_mmr: bool = False) -> str:
        """Get context filtered by metadata or content, with optional MMR."""
        if use_metadata:
            # Example: filter by metadata (stub, depends on Chroma's API)
            docs = self.vector_store.similarity_search_with_score(query, k=k*2)
            filtered_docs = [doc for doc, score in docs if any(
                filter_term.lower() in str(getattr(doc, 'metadata', {})).lower() for filter_term in filters
            )]
        else:
            docs = self.vector_store.similarity_search(query, k=k*2)
            filtered_docs = [doc for doc in docs if any(
                filter_term.lower() in doc.page_content.lower() for filter_term in filters
            )]
        if use_mmr:
            # Stub: implement MMR reranking here
            filtered_docs = self.maximal_marginal_relevance(query, filtered_docs, k)
        context = "\n\n".join([doc.page_content for doc in filtered_docs[:k]])
        return context

    def maximal_marginal_relevance(self, query: str, docs: List, k: int) -> List:
        """Stub for MMR reranking (replace with real implementation as needed)."""
        # For now, just return the first k docs
        return docs[:k]

    def summarize_context(self, context: str, max_length: int = 1500) -> str:
        """Summarize retrieved context chunks (stub: replace with LLM call if needed)."""
        if len(context) > max_length:
            return context[:max_length//2] + '\n...\n' + context[-max_length//2:]
        return context

    def get_context(self, query: str, k: int = 5) -> str:
        """Retrieve relevant context for a query."""
        docs = self.vector_store.similarity_search(query, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    
    def get_context_for_task(self, task_id: str, task_description: str, k: int = 5) -> str:
        """Get context specific for a task."""
        query = f"Task {task_id}: {task_description}"
        return self.get_context(query, k)
    
    def get_context_by_keys(self, keys: List[str]) -> str:
        """
        Get context directly from specific memory documents by their keys.
        This is a more direct approach without vector search when you know what documents you need.
        
        Args:
            keys: List of document keys (filenames without extension)
            
        Returns:
            Combined content from all specified documents
        """
        context_parts = []
        context_dir = os.getenv("CONTEXT_STORE_DIR", "context-store/")
        
        for key in keys:
            filepath = os.path.join(context_dir, f"{key}.md")
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        context_parts.append(f.read())
                except Exception as e:
                    print(f"Error reading {filepath}: {str(e)}")
                    context_parts.append(f"[Memory missing for {key}: {str(e)}]")
            else:
                print(f"Warning: Memory file for '{key}' not found at {filepath}")
                context_parts.append(f"[Memory missing for {key}]")
                
        return "\n\n" + "-" * 40 + "\n\n".join(context_parts) + "\n\n" + "-" * 40 + "\n\n"

# Create a singleton instance
memory = MemoryEngine()

# Helper functions
def initialize_memory():
    """Initialize memory with existing documents."""
    context_dir = os.getenv("CONTEXT_STORE_DIR", "context-store/")
    if os.path.exists(context_dir):
        memory.add_directory(context_dir)
    else:
        print(f"Context directory {context_dir} not found. Creating it...")
        os.makedirs(context_dir, exist_ok=True)
    
def get_relevant_context(query: str, k: int = 5) -> str:
    """Get relevant context for a query."""
    return memory.get_context(query, k)

def get_context_by_keys(keys: List[str]) -> str:
    """Get context directly from specific memory documents by their keys."""
    return memory.get_context_by_keys(keys)