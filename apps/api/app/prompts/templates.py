"""
Template rendering utilities using Jinja2.
"""

from typing import Any, Dict

from jinja2 import Template


def render_template(template_str: str, context: Dict[str, Any]) -> str:
    """
    Render a Jinja2 template with context.

    Args:
        template_str: Template string with Jinja2 syntax
        context: Dictionary of variables for template

    Returns:
        Rendered string

    Raises:
        Exception: If template rendering fails
    """
    template = Template(template_str)
    return template.render(**context)


def build_rag_context_prompt(rag_context: str, query: str) -> str:
    """
    Build prompt with RAG context.

    Args:
        rag_context: Retrieved context from RAG
        query: User query

    Returns:
        Formatted prompt string
    """
    template_str = """
RELEVANT INFORMATION:
{{ rag_context }}

USER QUESTION:
{{ query }}

Please answer the user's question using the relevant information provided above. If the information doesn't fully cover the question, you may supplement with your general diving knowledge, but make it clear what comes from the provided information versus general knowledge.
""".strip()

    return render_template(template_str, {"rag_context": rag_context, "query": query})


def build_conversation_context(
    conversation_history: list,
    max_messages: int = 10
) -> str:
    """
    Build conversation context string from history.

    Args:
        conversation_history: List of message dictionaries
        max_messages: Maximum messages to include

    Returns:
        Formatted conversation string
    """
    recent_history = conversation_history[-max_messages:] if conversation_history else []
    
    if not recent_history:
        return ""
    
    lines = ["CONVERSATION HISTORY:"]
    for msg in recent_history:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)
