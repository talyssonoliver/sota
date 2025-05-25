"""
Mock LangChain modules for testing.
"""

import sys
import types
from unittest.mock import MagicMock

def setup_langchain_mocks():
    """
    Set up mocks for LangChain modules.
    """
    # Create mock LangChain modules
    sys.modules["langchain"] = types.ModuleType("langchain")
    sys.modules["langchain.vectorstores"] = types.ModuleType("langchain.vectorstores")
    sys.modules["langchain.embeddings"] = types.ModuleType("langchain.embeddings")
    sys.modules["langchain.chat_models"] = types.ModuleType("langchain.chat_models")
    sys.modules["langchain.document_loaders"] = types.ModuleType("langchain.document_loaders")
    sys.modules["langchain.text_splitter"] = types.ModuleType("langchain.text_splitter")
    sys.modules["langchain.chains"] = types.ModuleType("langchain.chains")
    sys.modules["langchain_core"] = types.ModuleType("langchain_core")
    sys.modules["langchain_core.runnables"] = types.ModuleType("langchain_core.runnables")
    
    # Create mock classes
    class MockChroma:
        def __init__(self, collection_name=None, embedding_function=None, persist_directory=None):
            self.collection_name = collection_name
            self.embedding_function = embedding_function
            self.persist_directory = persist_directory
            self.documents = []
        
        def as_retriever(self, search_type=None, search_kwargs=None):
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_documents.return_value = [
                type('Document', (), {'page_content': 'The orders table has RLS rules that restrict access to a user\'s own orders.'})
            ]
            return mock_retriever
            
        def similarity_search(self, query, k=None, filter=None):
            return [
                type('Document', (), {'page_content': 'The orders table has RLS rules that restrict access to a user\'s own orders.'})
            ]
            
        def add_texts(self, texts, metadatas=None, **kwargs):
            return ["doc1", "doc2", "doc3"][:len(texts)]
            
        def add_documents(self, documents):
            self.documents.extend(documents)
            return ["doc1", "doc2", "doc3"][:len(documents)]

    class MockOpenAIEmbeddings:
        def __init__(self, model=None):
            self.model = model

    class MockChatOpenAI:
        def __init__(self, temperature=0):
            self.temperature = temperature

    class MockTextLoader:
        def __init__(self, file_path):
            self.file_path = file_path
        
        def load(self):
            return [type('Document', (), {'page_content': 'Test document content'})]

    class MockDirectoryLoader:
        def __init__(self, path, glob=None):
            self.path = path
            self.glob = glob
        
        def load(self):
            return [type('Document', (), {'page_content': 'Test directory content'})]

    class MockCharacterTextSplitter:
        def __init__(self, chunk_size=None, chunk_overlap=None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
        
        def split_documents(self, documents):
            return documents

    class MockRetrievalQA:
        @staticmethod
        def from_chain_type(llm=None, chain_type=None, retriever=None, return_source_documents=False):
            mock = MagicMock()
            mock.invoke.return_value = {"result": "Test answer"}
            return mock

    class MockConversationalRetrievalChain:
        @staticmethod
        def from_llm(llm=None, retriever=None, memory=None, return_source_documents=False):
            mock = MagicMock()
            mock.invoke.return_value = {"answer": "Test conversation answer"}
            return mock

    # Mock Runnable classes for LCEL
    class MockRunnable:
        def __init__(self):
            pass
            
        def invoke(self, input_data):
            return {"result": "Test result from runnable"}

    # Assign mock classes to modules
    sys.modules["langchain.vectorstores"].Chroma = MockChroma
    sys.modules["langchain.embeddings"].OpenAIEmbeddings = MockOpenAIEmbeddings
    sys.modules["langchain.chat_models"].ChatOpenAI = MockChatOpenAI
    sys.modules["langchain.document_loaders"].TextLoader = MockTextLoader
    sys.modules["langchain.document_loaders"].DirectoryLoader = MockDirectoryLoader
    sys.modules["langchain.text_splitter"].CharacterTextSplitter = MockCharacterTextSplitter
    sys.modules["langchain.chains"].RetrievalQA = MockRetrievalQA
    sys.modules["langchain.chains"].ConversationalRetrievalChain = MockConversationalRetrievalChain
    sys.modules["langchain_core.runnables"].RunnableParallel = MockRunnable
    sys.modules["langchain_core.runnables"].RunnablePassthrough = MockRunnable

if __name__ == "__main__":
    setup_langchain_mocks()
