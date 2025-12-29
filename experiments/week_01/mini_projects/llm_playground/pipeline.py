from typing import Dict, Optional, Any
import re
from models import ModelClient
from prompts import get_analysis_prompt, get_transform_prompt, get_translation_prompt
from logger import logger
from tqdm import tqdm

# Week 1 Day 5 learning: Multi-step LLM workflows orchestrate multiple calls
# This is the "agentic-lite" pattern - explicit steps, clear flow, no complex frameworks


def analyze_content(content: str, model_client: ModelClient, stream: bool) -> Dict[str, Any]:
    """
    Step 1: Analyze content to identify topics, tone, and structure.
    
    Analysis step guides the transformation step.
    This is the first LLM call in the multi-step workflow.
    
    Args:
        content: Text content to analyze
        model_client: Model client instance
        stream: Whether to stream response
    
    Returns:
        Dict with 'content' (analysis text) and 'tokens' metadata
    """
    system_prompt, user_prompt = get_analysis_prompt(content)
    response = model_client.call(system_prompt, user_prompt, stream=stream)
    
    tokens = response['tokens'].copy()
    if 'cost' in response:
        tokens['cost'] = response['cost']
    
    return {
        'content': response['content'],
        'tokens': tokens
    }


def transform_content(
    content: str,
    analysis: Dict[str, Any],
    model_client: ModelClient,
    tone: str,
    stream: bool,
    json_mode: bool = False
) -> Dict[str, Any]:
    """
    Step 2: Transform content into summary, bullets, and rewritten version.
    
    Week 1 Day 5 learning: Uses analysis results to guide transformation.
    This is the second LLM call - it takes the analysis and generates structured output.
    
    Args:
        content: Original text content
        analysis: Analysis results from previous step
        model_client: Model client instance
        tone: Desired tone for rewritten content
        stream: Whether to stream response
        json_mode: Whether to use JSON mode for structured output
    
    Returns:
        Dict with 'summary', 'bullets', 'rewritten', and 'tokens'
    """
    system_prompt, user_prompt = get_transform_prompt(content, analysis, tone, json_mode=json_mode)
    
    # Week 1 learning: JSON mode requires response_format parameter
    # Note: JSON mode doesn't work with streaming, so we disable it if streaming
    response_format = 'json_object' if json_mode and not stream else None
    response = model_client.call(system_prompt, user_prompt, stream=stream, response_format=response_format)
    
    # Week 1 learning: Parse structured LLM response
    # JSON mode provides guaranteed valid JSON, making parsing more reliable
    # Markdown mode requires regex parsing which can be fragile
    transform_text = response['content']
    
    if json_mode:
        # Week 1 learning: JSON mode returns valid JSON, parse directly
        # This is more reliable than regex parsing of markdown
        import json
        try:
            # Parse JSON response
            parsed = json.loads(transform_text)
            summary = parsed.get('summary')
            bullets_list = parsed.get('key_points', [])
            # Convert list to formatted string
            bullets_text = '\n'.join(f"* {bullet}" for bullet in bullets_list) if bullets_list else None
            rewritten = parsed.get('rewritten')
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Falling back to markdown parsing.")
            # Fallback to markdown parsing if JSON parsing fails
            json_mode = False
    
    if not json_mode:
        # Extract summary (look for "Summary:" or "## Summary" section)
        summary_match = re.search(r'(?:Summary|## Summary)[:\s]+\s*(.+?)(?=\n\n|\n\*\*|\n##|$)', transform_text, re.DOTALL | re.IGNORECASE)
        summary = summary_match.group(1).strip() if summary_match else None
        
        # Extract bullet points (look for "Key Points:" or bullet list)
        bullets_match = re.search(r'(?:Key Points|## Key Points)[:\s]+\s*(.+?)(?=\n\n|\n\*\*|\n##|$)', transform_text, re.DOTALL | re.IGNORECASE)
        bullets_text = bullets_match.group(1).strip() if bullets_match else None
        
        # Extract rewritten content (look for "Rewritten:" section)
        rewritten_match = re.search(r'(?:Rewritten|## Rewritten)[:\s]+\s*(.+?)(?=\n\n|\n\*\*|\n##|$)', transform_text, re.DOTALL | re.IGNORECASE)
        rewritten = rewritten_match.group(1).strip() if rewritten_match else None
        
        # Fallback: if parsing fails, use the full response as rewritten
        # This handles cases where LLM doesn't follow exact format
        if not rewritten:
            rewritten = transform_text
    
    tokens = response['tokens'].copy()
    if 'cost' in response:
        tokens['cost'] = response['cost']
    
    return {
        'summary': summary,
        'bullets': bullets_text,
        'rewritten': rewritten,
        'tokens': tokens
    }


def translate_content(
    text: str,
    target_lang: str,
    model_client: ModelClient,
    stream: bool
) -> Dict[str, Any]:
    """
    Step 3 (Optional): Translate text to target language.
    
    Week 1 Day 5 learning: Additional LLM call extends the workflow.
    This demonstrates how easy it is to add more steps to a multi-step pipeline.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'nl' for Dutch)
        model_client: Model client instance
        stream: Whether to stream response
    
    Returns:
        Dict with 'content' (translated text) and 'tokens' metadata
    """
    system_prompt, user_prompt = get_translation_prompt(text, target_lang)
    response = model_client.call(system_prompt, user_prompt, stream=stream)
    
    tokens = response['tokens'].copy()
    if 'cost' in response:
        tokens['cost'] = response['cost']
    
    return {
        'content': response['content'],
        'tokens': tokens
    }


def handle_error(step: str, error: Exception, results: Dict[str, Any]) -> None:
    """
    Handle errors in pipeline steps.
    
    Week 1 learning: Fail-fast approach - log errors clearly and stop pipeline.
    This prevents partial/corrupted results from propagating.
    
    Args:
        step: Name of the step that failed (e.g., "analysis", "transformation")
        error: Exception that occurred
        results: Results dict to update with error info
    """
    error_info = {
        'step': step,
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    results['errors'].append(error_info)
    logger.error(f"Error in {step} step: {error_info['error_type']}: {error_info['error_message']}")


def print_analysis(analysis: Dict[str, Any]) -> None:
    """
    Print analysis results for debugging/learning.
    
    Week 1 learning: Optional debug output helps understand what the LLM detected.
    This is useful for learning how analysis guides transformation.
    
    Args:
        analysis: Analysis results dict with 'content' key
    """
    print("\n" + "=" * 60)
    print("Analysis Results:")
    print("=" * 60)
    if analysis and 'content' in analysis:
        print(analysis['content'])
    print("=" * 60 + "\n")


def print_token_usage(tokens: Dict[str, Any], costs: Optional[Dict[str, float]] = None) -> None:
    """
    Print token usage statistics and cost information.
    
    Week 1 learning: Token awareness is crucial for cost management.
    This helps track costs across the multi-step workflow.
    
    Args:
        tokens: Dict with token counts per step (e.g., {'analysis': {...}, 'transform': {...}})
        costs: Optional dict with cost per step (for OpenAI models)
    """
    if not tokens:
        return
    
    print("\n" + "=" * 60)
    print("Token Usage:")
    print("=" * 60)
    
    total_input = 0
    total_output = 0
    total_total = 0
    total_cost = 0.0
    
    for step, step_tokens in tokens.items():
        if isinstance(step_tokens, dict):
            input_tokens = step_tokens.get('input', 0)
            output_tokens = step_tokens.get('output', 0)
            step_total = step_tokens.get('total', 0)
            step_cost = costs.get(step) if costs else None
            
            print(f"{step.capitalize()}:")
            print(f"  Input:  {input_tokens:,} tokens")
            print(f"  Output: {output_tokens:,} tokens")
            print(f"  Total:  {step_total:,} tokens")
            if step_cost is not None:
                print(f"  Cost:   ${step_cost:.6f}")
            print()
            
            total_input += input_tokens
            total_output += output_tokens
            total_total += step_total
            if step_cost is not None:
                total_cost += step_cost
    
    if total_total > 0:
        print("-" * 60)
        print(f"Grand Total:")
        print(f"  Input:  {total_input:,} tokens")
        print(f"  Output: {total_output:,} tokens")
        print(f"  Total:  {total_total:,} tokens")
        if total_cost > 0:
            print(f"  Cost:   ${total_cost:.6f}")
    
    print("=" * 60 + "\n")


def run_pipeline(
    content: str,
    model_provider: str,
    model_name: Optional[str] = None,
    tone: str = 'professional',
    stream: bool = True,
        translate_to: Optional[str] = None,
        show_analysis: bool = False,
        show_tokens: bool = False,
        show_progress: bool = True,
        json_mode: bool = False
) -> Dict[str, Any]:
    """
    Main pipeline: Analyze → Transform → (Optional Translate)
    
    Week 1 Day 5 learning: This orchestrates the multi-step LLM workflow.
    Each step builds on the previous one, creating an "agentic-lite" pattern.
    
    Flow:
    1. Analyze: Detect topics, tone, structure
    2. Transform: Generate summary, bullets, rewritten content
    3. Translate (optional): Translate rewritten content to target language
    
    Args:
        content: Text content to process
        model_provider: 'openai' or 'ollama'
        model_name: Optional custom model name (overrides default for provider)
        tone: Desired tone for rewritten content (professional, casual, technical, humorous)
        stream: Whether to stream responses
        translate_to: Optional target language code (e.g., 'nl' for Dutch)
        show_analysis: Whether to print analysis results
        show_tokens: Whether to print token usage statistics
        show_progress: Whether to show progress indicators (default: True)
        json_mode: Whether to use JSON mode for structured output (OpenAI only, non-streaming)
    
    Returns:
        Dict with:
            - 'analysis': Analysis results
            - 'summary': Generated summary
            - 'bullets': Key bullet points
            - 'rewritten': Rewritten content in specified tone
            - 'translated': Translated content (if translate_to provided)
            - 'tokens': Token usage per step
            - 'errors': List of errors (if any)
    """
    model_client = ModelClient(model_provider, model_name=model_name)
    results = {
        'analysis': None,
        'summary': None,
        'bullets': None,
        'rewritten': None,
        'translated': None,
        'tokens': {},
        'errors': []
    }
    
    # Week 1 learning: Progress indicators improve UX for long-running operations
    # Calculate total steps for progress bar
    total_steps = 2  # Analysis + Transform
    if translate_to:
        total_steps += 1
    
    # Create progress bar if enabled
    progress_bar = None
    if show_progress and not stream:  # Only show progress for non-streaming (streaming shows real-time output)
        progress_bar = tqdm(
            total=total_steps,
            desc="Pipeline",
            unit="step",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
    
    try:
        # Step 1: Analyze
        # Week 1 Day 5 learning: Analysis step identifies key characteristics
        # This guides the transformation step for better results
        if progress_bar:
            progress_bar.set_description("Analyzing content...")
        logger.info("Starting analysis step...")
        try:
            analysis = analyze_content(content, model_client, stream)
            results['analysis'] = analysis
            results['tokens']['analysis'] = analysis['tokens']
            
            if show_analysis:
                print_analysis(analysis)
            logger.info("Analysis step completed successfully")
            if progress_bar:
                progress_bar.update(1)
        except Exception as e:
            handle_error("analysis", e, results)
            if progress_bar:
                progress_bar.close()
            return results  # Fail fast - can't transform without analysis
        
        # Step 2: Transform
        # Week 1 Day 5 learning: Transformation uses analysis to generate structured output
        # This is where the multi-step workflow shows its value - analysis guides transformation
        if progress_bar:
            progress_bar.set_description("Transforming content...")
        logger.info("Starting transformation step...")
        try:
            transform_results = transform_content(
                content, analysis, model_client, tone, stream, json_mode=json_mode
            )
            transform_tokens = transform_results.pop('tokens', None)
            results.update(transform_results)
            if transform_tokens is not None:
                results['tokens']['transform'] = transform_tokens
            logger.info("Transformation step completed successfully")
            if progress_bar:
                progress_bar.update(1)
        except Exception as e:
            handle_error("transformation", e, results)
            if progress_bar:
                progress_bar.close()
            return results  # Fail fast - transformation is critical
        
        # Step 3: Optional Translation
        # Week 1 Day 5 learning: Additional LLM call extends the workflow
        # This demonstrates how easy it is to add more steps
        if translate_to:
            if progress_bar:
                progress_bar.set_description(f"Translating to {translate_to}...")
            logger.info(f"Starting translation step (target: {translate_to})...")
            try:
                # Only translate if we have rewritten content
                if results['rewritten']:
                    translated = translate_content(
                        results['rewritten'], translate_to, model_client, stream
                    )
                    results['translated'] = translated['content']
                    results['tokens']['translation'] = translated['tokens']
                    logger.info("Translation step completed successfully")
                    if progress_bar:
                        progress_bar.update(1)
                else:
                    logger.warning("No rewritten content to translate")
            except Exception as e:
                handle_error("translation", e, results)
                # Don't fail pipeline for translation - it's optional
                # Just log the error and continue
    finally:
        if progress_bar:
            progress_bar.set_description("Complete")
            progress_bar.close()
    
    # Collect costs from all steps for display
    costs = {}
    for step, step_tokens in results['tokens'].items():
        if isinstance(step_tokens, dict) and step_tokens.get('cost') is not None:
            costs[step] = step_tokens['cost']
    
    if show_tokens:
        print_token_usage(results['tokens'], costs if costs else None)
    
    logger.info("Pipeline execution completed")
    return results