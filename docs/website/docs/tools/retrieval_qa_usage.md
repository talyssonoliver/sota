# Using RetrievalQA for Context Injection

This guide demonstrates how to use the newly implemented RetrievalQA functionality to dynamically generate answers from your context store and inject them into agent prompts.

## Basic Usage

The `retrieval_qa` method and `get_answer` helper function allow you to ask questions about your knowledge base and receive coherent answers rather than just raw context:

```python
from tools.memory_engine import get_answer

# Get a direct answer to a question
answer = get_answer(
    "What are the Supabase RLS rules for the orders table?",
    temperature=0.0,  # Controls response creativity (0.0-1.0)
    user="developer"  # Provides user context for tracking and permissions
)
print(answer)
# Output: "The orders table has RLS rules that restrict users to only see their own orders."
```

## Context Injection into Agent Prompts

You can inject this context dynamically into an agent's prompt before execution:

```python
from tools.memory_engine import get_answer

def build_backend_agent():
    # Get specific context about database rules
    db_rules = get_answer(
        "What are the Supabase RLS rules for the orders table?",
        temperature=0.0,
        user="system"
    )
    
    # Build the agent with context
    return Agent(
        role="Backend Engineer",
        goal="Implement secure database access",
        system_prompt=f"""You are a backend engineer working on a Supabase project.
        Remember these important security rules:
        
        {db_rules}
        
        Ensure all your implementations follow these security guidelines.
        """
    )
```

## Advanced Features

### Conversation Mode

You can use conversation mode to maintain context across multiple related queries:

```python
from tools.memory_engine import get_answer

# Start a conversation about database security
answer1 = get_answer(
    "What are the Supabase RLS rules for the orders table?", 
    use_conversation=True,
    temperature=0.0,
    user="developer"  # Important to maintain same user for conversation continuity
)

# Follow-up question maintains context
answer2 = get_answer(
    "How would I implement those in code?", 
    use_conversation=True,
    temperature=0.0,
    user="developer"  # Same user maintains conversation context
)
```

### Filtering by Metadata

Target specific domains or document types in your knowledge base:

```python
from tools.memory_engine import get_answer

# Only retrieve information from database documentation
db_answer = get_answer(
    "How is authentication implemented?",
    metadata_filter={"domain": "database"},
    temperature=0.0,
    user="developer"
)

# Only retrieve information from security documentation
security_answer = get_answer(
    "How is authentication implemented?",
    metadata_filter={"domain": "security"},
    temperature=0.0,
    user="developer"
)
```

### Temperature Control

Adjust the creativity level of responses:

```python
from tools.memory_engine import get_answer

# More deterministic answer
precise_answer = get_answer(
    "What are our API routes?",
    temperature=0.0  # Default value
)

# More creative answer
creative_answer = get_answer(
    "What are some ways we could improve our API design?",
    temperature=0.7,
    user="designer"
)
```

## Integration with MCP Context for Agents

Here's how to connect RetrievalQA to your agents:

```python
from tools.memory_engine import get_answer
from agents.coordinator import Agent

def build_agent_with_context(role, goal, question_list):
    # Build context from multiple related questions
    context_parts = []
    
    for question in question_list:
        answer = get_answer(
            question,
            temperature=0.0,
            user="system"
        )
        context_parts.append(f"Q: {question}\nA: {answer}")
    
    # Join all context parts
    full_context = "\n\n".join(context_parts)
    
    # Create agent with dynamically generated context
    return Agent(
        role=role,
        goal=goal,
        system_prompt=f"You are a {role}. Your goal is to {goal}.\n\n" +
                     f"Use this context to inform your decisions:\n{full_context}"
    )

# Example usage
qa_agent = build_agent_with_context(
    "QA Engineer",
    "Ensure all features are well-tested",
    [
        "What are our testing standards?",
        "What code coverage do we require?",
        "What testing frameworks do we use?"
    ]
)
```

## Best Practices

1. **Be specific with questions**: More specific questions yield more targeted answers.
2. **Filter by metadata**: Use metadata filters to narrow down the domain of knowledge.
3. **Batch related questions**: Group related questions to build comprehensive context.
4. **Use conversation mode** for follow-up questions that reference earlier context.
5. **Cache important answers** for frequently used context to reduce API calls.
6. **Adjust temperature** based on your needs - lower for factual responses, higher for creative ones.
7. **Always specify a user context** for tracking, permissions, and maintaining conversation context.

## Implementation Notes

The RetrievalQA functionality is implemented using:
- LangChain's `RetrievalQA` or `ConversationalRetrievalChain` 
- OpenAI's language models via `ChatOpenAI`
- The existing vector store from the Memory Engine

## Parameter Reference

When using `get_answer()`, these parameters control the behavior:

- `question` (required): The query to ask the knowledge base
- `use_conversation` (optional, default=False): Set to True to maintain conversation context
- `metadata_filter` (optional): Dictionary of metadata fields to filter documents
- `temperature` (optional, default=0.0): Controls response creativity (0.0-1.0)
- `user` (optional, default=None): User identifier for tracking and permissions
