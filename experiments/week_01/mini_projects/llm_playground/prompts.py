from typing import Dict, Tuple

def get_analysis_prompt(content: str) -> Tuple[str, str]:
    """
    Return (system, user) prompts for content analysis.
    
    Multi-step LLM workflows start with analysis.
    This identifies key topics, tone, and structure to guide the transformation step.
    Uses structured prompting to get actionable insights.
    
    Args:
        content: Text content to analyze
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = """You are an expert content analyzer.
Your task is to analyze the provided content and identify key characteristics that will guide content transformation.

Analyze the content and identify:
- Key topics and main themes
- Overall tone (professional, casual, technical, humorous, etc.)
- Content length and structure
- Primary audience or purpose

Respond in a clear, structured format that can be used to guide content transformation.
Focus on actionable insights that will help improve the content."""


    
    # Week 1 learning: Truncate content to manage costs (3000 chars is usually enough for analysis)
    # Always be aware of token costs when building prompts
    user = f"""Analyze this content and provide insights about its topics, tone, and structure:

{content[:3000]}

Provide a clear analysis that identifies:
1. Main topics and themes
2. Detected tone
3. Content structure and length
4. Key insights for transformation"""
    
    return system, user


def get_transform_prompt(content: str, analysis: Dict, tone: str) -> Tuple[str, str]:
    """
    Return prompts for content transformation.
    
    Generates summary, bullet points, and rewritten version using the specified tone.
    Uses analysis results to guide the transformation process.
    
    Args:
        content: Original text content
        analysis: Analysis results from previous step (may contain insights)
        tone: Desired tone for rewritten content (professional, casual, technical, humorous)
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    
    # Week 1 Day 5 learning: System prompt controls output tone/personality
    # By changing the system prompt, we can easily switch between professional, casual, etc.
    # This is a powerful pattern - same content, different style, just by changing the prompt
    tone_prompts = {
        'professional': """You are an assistant that transforms content into a professional format.
Write in a clear, formal, and business-appropriate tone.
Maintain accuracy and clarity while ensuring the content is suitable for professional audiences.""",
        
        'casual': """You are an assistant that transforms content into a friendly, approachable format.
Write in a conversational, casual tone as if talking to a friend.
Keep it engaging and easy to read while maintaining the core information.""",
        
        'technical': """You are an assistant that transforms content into a detailed, technical format.
Focus on technical accuracy, precision, and implementation details.
Use appropriate technical terminology and maintain a formal, precise tone.""",
        
        'humorous': """You are an assistant that transforms content into an entertaining, witty format.
Write in a humorous, engaging tone while still being informative.
Make it fun to read while preserving the essential information."""
    }
    
    system = tone_prompts.get(tone.lower(), tone_prompts['professional'])
    system += """

Your task is to transform the provided content into three formats:
1. A concise summary (2-3 sentences)
2. Key bullet points (3-5 main points)
3. A rewritten version in the specified tone

Respond in markdown format with clear sections:
- Summary: [concise summary]
- Key Points: [bullet points]
- Rewritten: [rewritten content in specified tone]"""
    
    # Build user prompt with content and analysis context
    # Week 1 learning: Use analysis results to guide transformation (agentic pattern)
    # The analysis from the previous step helps the LLM make better transformation decisions
    user_parts = [f"Transform this content using a {tone} tone:\n\n{content[:4000]}"]
    
    # Include analysis insights if available (this is the "multi-step workflow" pattern)
    # The analysis step informs the transformation step, making it more effective
    if analysis and isinstance(analysis, dict):
        if 'content' in analysis:
            # If analysis is a dict with 'content' key (from model response)
            analysis_text = str(analysis.get('content', ''))[:500]
            if analysis_text:
                user_parts.append(f"\n\nPrevious analysis insights:\n{analysis_text}")
    
    user = "\n".join(user_parts)
    
    return system, user


def get_translation_prompt(text: str, target_lang: str) -> Tuple[str, str]:
    """
    Return prompts for text translation.
    
    Week 1 Day 5 learning: Additional LLM call for translation (optional extension).
    This demonstrates how easy it is to add more steps to a multi-step workflow.
    Translates while preserving meaning and tone.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'nl' for Dutch, 'es' for Spanish)
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Language name mapping: convert codes to full names for better prompts
    # "nl" -> "Dutch" makes the prompt clearer for the LLM
    lang_names = {
        'nl': 'Dutch',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'ko': 'Korean',
        'ru': 'Russian'
    }
    
    lang_name = lang_names.get(target_lang.lower(), target_lang.upper())
    
    system = f"""You are an expert translator.
Your task is to translate text from English to {lang_name} while:
- Preserving the original meaning and tone
- Maintaining natural, fluent {lang_name} phrasing
- Keeping the same structure and formatting when appropriate

Translate accurately and naturally, as if written originally in {lang_name}."""
    
    # Week 1 learning: Truncate to manage costs (3000 chars is usually enough for translation)
    # Always be cost-aware when building prompts
    user = f"""Translate the following text to {lang_name}:

{text[:3000]}

Provide only the translation, without additional commentary or explanations."""
    
    return system, user