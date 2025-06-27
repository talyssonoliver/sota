"""LangChain Core compatibility module."""

from .runnables import (
    Runnable, 
    RunnablePassthrough, 
    RunnableLambda, 
    RunnableSequence, 
    RunnableParallel
)

__all__ = ['Runnable', 'RunnablePassthrough', 'RunnableLambda', 'RunnableSequence', 'RunnableParallel']