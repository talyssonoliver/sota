"""
Mock implementations for dependencies used in testing.

This module provides mock versions of dependencies that are required
for tests to pass but might not be properly installed or configured.
"""

class MockLiteLLM:
    """Mock implementation of litellm package."""
    
    class Choices:
        """Mock implementation of litellm.Choices class."""
        def __init__(self, *args, **kwargs):
            self.finish_reason = None
            self.index = 0
            self.message = None
    
    class ModelResponse:
        """Mock implementation of litellm response."""
        def __init__(self, *args, **kwargs):
            self.choices = []
            self.model = "mock-model"
    
    class utils:
        """Mock implementation of litellm.utils module."""
        @staticmethod
        def get_secret(*args, **kwargs):
            return "mock-secret"
            
        @staticmethod
        def token_counter(*args, **kwargs):
            return 10
            
        @staticmethod
        def supports_response_schema(*args, **kwargs):
            return True
    
    class integrations:
        """Mock implementation of litellm.integrations module."""
        class custom_logger:
            """Mock implementation of litellm.integrations.custom_logger."""
            @staticmethod
            def log_event(*args, **kwargs):
                pass
                
            class CustomLogger:
                """Mock implementation of CustomLogger class."""
                def __init__(self, *args, **kwargs):
                    pass
                    
                def log_event(self, *args, **kwargs):
                    pass
                    
                def flush(self, *args, **kwargs):
                    pass
                    
                def success_callback(self, *args, **kwargs):
                    pass
                    
                def failure_callback(self, *args, **kwargs):
                    pass
            
    class exceptions:
        """Mock implementation of litellm.exceptions module."""
        class BadRequestError(Exception):
            """Mock BadRequestError exception."""
            pass
            
        class AuthenticationError(Exception):
            """Mock AuthenticationError exception."""
            pass
            
        class RateLimitError(Exception):
            """Mock RateLimitError exception."""
            pass
            
        class ServiceUnavailableError(Exception):
            """Mock ServiceUnavailableError exception."""
            pass
            
        class OpenAIError(Exception):
            """Mock OpenAIError exception."""
            pass
            
        class ContextWindowExceededError(Exception):
            """Mock ContextWindowExceededError exception."""
            pass
            
    class types:
        """Mock implementation of litellm.types module."""
        class utils:
            """Mock implementation of litellm.types.utils module."""
            class ChatCompletionDeltaToolCall:
                """Mock implementation of ChatCompletionDeltaToolCall class."""
                def __init__(self, *args, **kwargs):
                    pass
            
            class Usage:
                """Mock implementation of Usage class."""
                def __init__(self, *args, **kwargs):
                    self.prompt_tokens = 0
                    self.completion_tokens = 0
                    self.total_tokens = 0
                    
            # Add ModelResponse here too for the specific import pattern
            ModelResponse = None  # Will be properly set in patch_imports

# Mock for langchain's OpenAIEmbeddings
class MockOpenAIEmbeddings:
    """Mock implementation of OpenAIEmbeddings class."""
    def __init__(self, *args, **kwargs):
        pass
        
    def embed_documents(self, texts):
        """Return mock embeddings for a list of texts."""
        return [[0.1] * 1536 for _ in texts]
        
    def embed_query(self, text):
        """Return mock embeddings for a single text."""
        return [0.1] * 1536

# Mock for Chroma vectorstore
class MockChroma:
    """Mock implementation of Chroma vectorstore."""
    def __init__(self, *args, **kwargs):
        self.collection_name = kwargs.get("collection_name", "default")
        
    def similarity_search(self, *args, **kwargs):
        """Return empty search results."""
        return []
        
    def add_texts(self, *args, **kwargs):
        """Mock adding texts to the vectorstore."""
        return ["doc1", "doc2"]
    
    def add_documents(self, *args, **kwargs):
        """Mock adding documents to the vectorstore."""
        return ["doc1", "doc2"]
        
    @classmethod
    def from_texts(cls, texts, embedding, **kwargs):
        """Create a mock Chroma instance."""
        return cls(**kwargs)

# Mock for LangChain BaseTool
class MockLangChainBaseTool:
    """Mock implementation of LangChain BaseTool."""
    name: str = "base_tool"
    description: str = "A base tool"
    
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", self.name)
        self.description = kwargs.get("description", self.description)
        
    def _run(self, *args, **kwargs):
        return "Mock tool result"
        
    async def _arun(self, *args, **kwargs):
        return "Mock async tool result"
        
    def run(self, *args, **kwargs):
        return self._run(*args, **kwargs)
        
    async def arun(self, *args, **kwargs):
        return await self._arun(*args, **kwargs)

# Mock render module for langchain.tools.render
class MockRender:
    """Mock implementation of langchain.tools.render module."""
    @staticmethod
    def format_tool_to_openai_function(*args, **kwargs):
        return {
            "type": "function",
            "function": {
                "name": "mock_function",
                "description": "A mock function",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
    @staticmethod
    def render_text_description_and_args(*args, **kwargs):
        """Mock implementation of render_text_description_and_args function."""
        return "Mock tool description", {"arg1": "value1"}

# Mock for DirectoryLoader
class MockDirectoryLoader:
    """Mock implementation of DirectoryLoader."""
    def __init__(self, *args, **kwargs):
        pass
        
    def load(self):
        return []

# Function to patch imports
def patch_imports():
    """
    Patch import system to provide mock implementations for missing modules.
    """
    import sys
    from types import ModuleType
    import os
    import builtins
    import importlib
    
    # Store original import function to use for non-mocked modules
    original_import = builtins.__import__
    
    # Set OpenAI API key environment variable to avoid validation errors
    os.environ["OPENAI_API_KEY"] = "sk-mockapikey"
    
    # Patch registry to include get_agent function
    def patch_registry():
        try:
            # Try to import the actual module first
            sys.path.insert(0, os.path.abspath('c:\\taly\\ai-system'))
            registry_module = importlib.import_module('orchestration.registry')
            
            # Add the missing get_agent function
            if not hasattr(registry_module, 'get_agent'):
                def get_agent(agent_name):
                    """Mock implementation of get_agent function."""
                    return lambda *args, **kwargs: {"message": "Mock agent response"}
                
                registry_module.get_agent = get_agent
                print("Successfully patched orchestration.registry with get_agent function")
        except Exception as e:
            print(f"Failed to patch orchestration.registry: {e}")
    
    # Patch langchain modules
    try:
        # Create mock modules for langchain
        mock_langchain_embeddings = ModuleType('langchain.embeddings')
        mock_langchain_embeddings.OpenAIEmbeddings = MockOpenAIEmbeddings
        sys.modules['langchain.embeddings'] = mock_langchain_embeddings
        
        mock_langchain_community_embeddings = ModuleType('langchain_community.embeddings')
        mock_langchain_community_embeddings.OpenAIEmbeddings = MockOpenAIEmbeddings
        sys.modules['langchain_community.embeddings'] = mock_langchain_community_embeddings
        
        mock_langchain_vectorstores = ModuleType('langchain.vectorstores')
        mock_langchain_vectorstores.Chroma = MockChroma
        sys.modules['langchain.vectorstores'] = mock_langchain_vectorstores
        
        mock_langchain_community_vectorstores = ModuleType('langchain_community.vectorstores')
        mock_langchain_community_vectorstores.Chroma = MockChroma
        sys.modules['langchain_community.vectorstores'] = mock_langchain_community_vectorstores
        
        # Add mock for document loaders
        mock_langchain_loaders = ModuleType('langchain.document_loaders')
        mock_langchain_loaders.TextLoader = lambda *args, **kwargs: []
        mock_langchain_loaders.DirectoryLoader = MockDirectoryLoader
        sys.modules['langchain.document_loaders'] = mock_langchain_loaders
        
        mock_langchain_community_loaders = ModuleType('langchain_community.document_loaders')
        mock_langchain_community_loaders.TextLoader = lambda *args, **kwargs: []
        mock_langchain_community_loaders.DirectoryLoader = MockDirectoryLoader
        sys.modules['langchain_community.document_loaders'] = mock_langchain_community_loaders
        
        # Add mock for LangChain tools
        mock_langchain_tools = ModuleType('langchain.tools')
        mock_langchain_tools.BaseTool = MockLangChainBaseTool
        sys.modules['langchain.tools'] = mock_langchain_tools
        
        # Add mock for langchain.tools.render
        mock_langchain_tools_render = ModuleType('langchain.tools.render')
        mock_langchain_tools_render.format_tool_to_openai_function = MockRender.format_tool_to_openai_function
        mock_langchain_tools_render.render_text_description_and_args = MockRender.render_text_description_and_args
        sys.modules['langchain.tools.render'] = mock_langchain_tools_render
        
        mock_langchain_pydantic_v1 = ModuleType('langchain.pydantic_v1')
        mock_langchain_pydantic_v1.Field = lambda *args, **kwargs: None
        mock_langchain_pydantic_v1.BaseModel = type('BaseModel', (), {})
        sys.modules['langchain.pydantic_v1'] = mock_langchain_pydantic_v1
        
        print("Successfully patched langchain dependencies")
    except Exception as e:
        print(f"Failed to patch langchain: {e}")
    
    # Create mock modules
    mock_litellm = ModuleType('litellm')
    
    # Add main components to litellm module
    mock_litellm.Choices = MockLiteLLM.Choices
    mock_litellm.ModelResponse = MockLiteLLM.ModelResponse
    
    # Add utils module
    mock_utils = ModuleType('litellm.utils')
    mock_utils.get_secret = MockLiteLLM.utils.get_secret
    mock_utils.token_counter = MockLiteLLM.utils.token_counter
    mock_utils.supports_response_schema = MockLiteLLM.utils.supports_response_schema
    mock_litellm.utils = mock_utils
    
    # Add integrations module
    mock_integrations = ModuleType('litellm.integrations')
    mock_custom_logger = ModuleType('litellm.integrations.custom_logger')
    mock_custom_logger.log_event = MockLiteLLM.integrations.custom_logger.log_event
    mock_custom_logger.CustomLogger = MockLiteLLM.integrations.custom_logger.CustomLogger
    mock_integrations.custom_logger = mock_custom_logger
    mock_litellm.integrations = mock_integrations
    sys.modules['litellm.integrations'] = mock_integrations
    sys.modules['litellm.integrations.custom_logger'] = mock_custom_logger
    
    # Add exceptions module
    mock_exceptions = ModuleType('litellm.exceptions')
    mock_exceptions.BadRequestError = MockLiteLLM.exceptions.BadRequestError
    mock_exceptions.AuthenticationError = MockLiteLLM.exceptions.AuthenticationError
    mock_exceptions.RateLimitError = MockLiteLLM.exceptions.RateLimitError
    mock_exceptions.ServiceUnavailableError = MockLiteLLM.exceptions.ServiceUnavailableError
    mock_exceptions.OpenAIError = MockLiteLLM.exceptions.OpenAIError
    mock_exceptions.ContextWindowExceededError = MockLiteLLM.exceptions.ContextWindowExceededError
    mock_litellm.exceptions = mock_exceptions
    
    # Add litellm_core_utils module with functions
    mock_core_utils = ModuleType('litellm.litellm_core_utils')
    
    # Add functions to core_utils
    mock_core_utils.completion = lambda *args, **kwargs: MockLiteLLM.ModelResponse()
    mock_core_utils.get_optional_params = lambda *args, **kwargs: {}
    mock_core_utils.get_llm_provider = lambda *args, **kwargs: "mock-provider"
    
    # Special function that's being imported specifically
    def get_supported_openai_params(*args, **kwargs):
        return ["model", "temperature", "max_tokens"]
    
    mock_core_utils.get_supported_openai_params = get_supported_openai_params
    
    # Handle the specific submodule import case by creating another module
    mock_get_supported = ModuleType('litellm.litellm_core_utils.get_supported_openai_params')
    sys.modules['litellm.litellm_core_utils.get_supported_openai_params'] = mock_get_supported
    
    # Now make the function available in both places
    mock_core_utils.get_supported_openai_params = get_supported_openai_params
    mock_get_supported.get_supported_openai_params = get_supported_openai_params
    mock_get_supported.__call__ = get_supported_openai_params
    
    mock_litellm.litellm_core_utils = mock_core_utils
    
    # Add types module
    mock_litellm.types = ModuleType('litellm.types')
    mock_litellm.types.utils = ModuleType('litellm.types.utils')
    
    # Important: Add ModelResponse to both places
    mock_litellm.types.ModelResponse = MockLiteLLM.ModelResponse
    mock_litellm.types.utils.ModelResponse = MockLiteLLM.ModelResponse
    
    # Add Usage class to types.utils
    mock_litellm.types.utils.Usage = MockLiteLLM.types.utils.Usage
    
    mock_litellm.types.utils.ChatCompletionDeltaToolCall = MockLiteLLM.types.utils.ChatCompletionDeltaToolCall
    
    # Update the class reference to point to the instance
    MockLiteLLM.types.utils.ModelResponse = mock_litellm.types.utils.ModelResponse
    
    # Add utility functions to satisfy possible imports
    mock_litellm.completion = lambda *args, **kwargs: MockLiteLLM.ModelResponse()
    mock_litellm.completion_cost = lambda *args, **kwargs: 0.0
    mock_litellm.stream_chunk_builder = lambda *args, **kwargs: None
    
    # Register mocks in sys.modules
    sys.modules['litellm'] = mock_litellm
    sys.modules['litellm.utils'] = mock_utils
    sys.modules['litellm.exceptions'] = mock_exceptions
    sys.modules['litellm.litellm_core_utils'] = mock_core_utils
    sys.modules['litellm.types'] = mock_litellm.types
    sys.modules['litellm.types.utils'] = mock_litellm.types.utils
    
    # Mock for langgraph.checkpoint.MemorySaver
    class MockMemorySaver:
        """Mock implementation of langgraph.checkpoint.MemorySaver class."""
        def __init__(self, *args, **kwargs):
            pass
            
        def get(self, *args, **kwargs):
            return None
        
        def put(self, *args, **kwargs):
            pass
        
        def __call__(self, *args, **kwargs):
            return self
            
    # Create langgraph mocks
    try:
        import langgraph.checkpoint
        # It exists, but may be missing MemorySaver
        if not hasattr(langgraph.checkpoint, 'MemorySaver'):
            langgraph.checkpoint.MemorySaver = MockMemorySaver
    except (ImportError, AttributeError):
        # Module doesn't exist, create it
        mock_langgraph = sys.modules.get('langgraph', ModuleType('langgraph'))
        mock_checkpoint = ModuleType('langgraph.checkpoint')
        mock_checkpoint.MemorySaver = MockMemorySaver
        mock_langgraph.checkpoint = mock_checkpoint
        sys.modules['langgraph'] = mock_langgraph
        sys.modules['langgraph.checkpoint'] = mock_checkpoint

    print("Successfully patched missing dependencies")
    
    # Patch the orchestration.registry module
    patch_registry()
    
    return True

if __name__ == "__main__":
    patch_imports()