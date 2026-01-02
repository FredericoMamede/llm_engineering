# System Prompts - Dynamic expertise-based prompt generation
#
# Pattern: Base prompt + level-specific additions
# Reused: Week 1 Exercise system prompt structure
# Extended: Expertise level adaptation for different audiences

from typing import Literal

# Type hint for IDE support and self-documenting code
ExpertiseLevel = Literal["beginner", "intermediate", "advanced"]

# Maps Gradio slider values to expertise names
# Used by UI components to convert numeric slider to string level
EXPERTISE_LEVELS = {
    1: "beginner",
    2: "intermediate", 
    3: "advanced"
}


def create_system_prompt(expertise_level: ExpertiseLevel = "intermediate") -> str:
    """
    Create a system prompt adapted to the user's expertise level.
    
    The same technical question requires different depth and terminology
    depending on who's asking. A beginner needs analogies and definitions;
    an expert wants concise, nuanced answers.
    
    Args:
        expertise_level: "beginner", "intermediate", or "advanced"
    
    Returns:
        System prompt string tailored to the expertise level
    """
    # Base prompt establishes the mentor personality
    # This is the foundation that works for all levels
    base_prompt = """You are a patient, educational coding mentor helping someone learn programming.
Your goal is to explain code in a way that helps them understand not just what
the code does, but how to recognize and apply similar patterns in the future.

Always:
- Break things down step-by-step
- Explain the "why" behind approaches, not just the "what"
- Compare to similar patterns when relevant
"""
    
    # Level-specific instructions modify the base behavior
    # Each level has different assumptions about prior knowledge
    level_additions = {
        "beginner": """
For this learner (BEGINNER level):
- Use simple, everyday analogies to explain concepts
- Avoid jargon - if you must use technical terms, define them immediately
- Break everything into very small steps
- Provide lots of examples with explanations
- Assume they may not know basic concepts - explain them
- Be encouraging and patient
- Use phrases like "Think of it like..." and "Imagine..."
""",
        "intermediate": """
For this learner (INTERMEDIATE level):
- Assume they know basic programming concepts (variables, functions, loops)
- Focus on explaining the "why" and tradeoffs
- You can use standard programming terminology without defining it
- Point out best practices and common patterns
- Compare to alternative approaches when relevant
- Balance clarity with depth
""",
        "advanced": """
For this learner (ADVANCED level):
- Be concise and efficient - don't over-explain basics
- Focus on nuances, edge cases, and performance considerations
- Discuss tradeoffs and when to use which approach
- Reference advanced patterns and principles (SOLID, design patterns, etc.)
- Point out subtle bugs or issues they might encounter
- Assume familiarity with the language and common libraries
- Challenge them to think deeper about the problem
"""
    }
    
    return base_prompt + level_additions.get(expertise_level, level_additions["intermediate"])


def create_user_prompt(question: str) -> str:
    """
    Create a structured user prompt for technical questions.
    
    Provides a consistent format that guides the LLM to give
    comprehensive, educational responses.
    
    Args:
        question: The user's technical question or code to explain
    
    Returns:
        Formatted user prompt with structure guidelines
    """
    return f"""Please help me understand this:

{question}

Structure your explanation as:
1. **High-level overview**: What problem does this solve? What does it do?
2. **Step-by-step breakdown**: Walk through each part
3. **Key concepts**: What programming patterns/techniques are used here?
4. **Why this approach**: What are the tradeoffs vs alternative approaches?
5. **Practical application**: When would I use similar patterns?
6. **Watch out for**: Any potential gotchas or edge cases?

Make it educational - help me understand how to recognize and apply similar patterns in future code.
"""
