"""
Minimal UI for Master Prompt Generator.

Inspection console - shows all required metadata for prompt inspection.
No dashboards, charts, or analytics - just visibility.
"""

import gradio as gr
from typing import Optional, Tuple, Dict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    PromptOrchestrator,
    PromptWithMetadata,
    EvaluationResult,
    LifecycleGuard,
    VersionGuard,
    ModelManager
)


class UIState:
    """Maintains UI state across interactions."""
    
    def __init__(self):
        self.orchestrator = PromptOrchestrator(quality_threshold=8.0)
        self.model_manager = ModelManager()
        self.current_prompt: Optional[PromptWithMetadata] = None
        self.current_evaluation: Optional[EvaluationResult] = None
        self.version_history: list[PromptWithMetadata] = []
        self.evaluation_history: list[EvaluationResult] = []
        self.lifecycle_guard = LifecycleGuard()
        self.version_guard = VersionGuard()


state = UIState()


def get_model_display_name(model_info: Dict) -> str:
    """Get display name for model with availability indicator."""
    model_name = model_info["name"]
    is_available = model_info["available"]
    unavailable_reason = model_info.get("unavailable_reason", "")
    
    if is_available:
        return f"✅ {model_name}"
    else:
        # Shorten reason for display
        if "Requires API key:" in unavailable_reason:
            env_var = unavailable_reason.replace("Requires API key: ", "")
            return f"🔒 {model_name} (needs {env_var})"
        elif "Ollama not running" in unavailable_reason:
            return f"🔒 {model_name} (Ollama offline)"
        else:
            return f"🔒 {model_name} ({unavailable_reason})"


def format_anti_patterns(patterns: list) -> str:
    """Format anti-patterns for display."""
    if not patterns:
        return "✅ No anti-patterns detected"
    
    lines = []
    for pattern in patterns:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(pattern.get("severity", "low"), "⚪")
        
        lines.append(
            f"{severity_emoji} **{pattern.get('name', 'Unknown').upper().replace('_', ' ')}** "
            f"({pattern.get('severity', 'unknown').upper()})\n"
            f"   - {pattern.get('description', '')}\n"
            f"   - Fix: {pattern.get('suggestion', '')}"
        )
    
    return "\n\n".join(lines)


def format_metrics(evaluation: EvaluationResult) -> str:
    """Format quality metrics for display."""
    return f"""
**Overall Score: {evaluation.total_score}/10**

| Metric | Score |
|--------|-------|
| Clarity | {evaluation.clarity}/10 |
| Completeness | {evaluation.completeness}/10 |
| Structure | {evaluation.structure}/10 |
| Best Practices | {evaluation.best_practices}/10 |
| Specificity | {evaluation.specificity}/10 |
| Reusability | {evaluation.reusability}/10 |
"""


def format_economics(metadata: PromptWithMetadata) -> str:
    """Format token economics for display."""
    cost = metadata.estimated_cost_per_run.get(metadata.target_model, 0.0)
    return f"""
**Token Economics**

- Input Tokens: ~{metadata.estimated_input_tokens}
- Output Tokens: ~{metadata.estimated_output_tokens}
- Total Tokens: ~{metadata.estimated_input_tokens + metadata.estimated_output_tokens}
- Cost ({metadata.target_model}): ${cost:.4f} per run
- Efficiency Score: {metadata.verbosity_efficiency_score:.0%}
- Tradeoff: {metadata.cost_quality_tradeoff}
"""


def format_approval_status(
    metadata: PromptWithMetadata,
    evaluation: EvaluationResult,
    blockers: list[str]
) -> str:
    """Format approval status with blockers."""
    if metadata.lifecycle_state == "approved":
        return "✅ **APPROVED** - Ready for production use"
    
    if blockers:
        blocker_text = "\n".join(f"  - {b}" for b in blockers)
        return f"❌ **NOT APPROVED**\n\n**Blockers:**\n{blocker_text}"
    
    can_approve, _ = state.orchestrator.approval_logic.check_approval_readiness(
        metadata, evaluation, state.version_history[0] if len(state.version_history) > 1 else None
    )
    
    if can_approve:
        return "⚠️ **READY FOR APPROVAL** - Meets all requirements"
    else:
        return "⏳ **PENDING** - Evaluation in progress"


def generate_prompt(
    use_case: str,
    category: str,
    complexity_tier: int,
    context: str,
    requirements: str,
    target_model: str
) -> Tuple[str, str, str, str, str, str]:
    """
    Generate a new prompt.
    
    Returns:
        (prompt_text, metadata_display, metrics_display, anti_patterns_display, 
         economics_display, approval_status)
    """
    if not use_case or not context:
        return "", "⚠️ Please provide use case and context", "", "", "", ""
    
    # Check model availability before generating
    is_available, reason = state.model_manager.check_model_availability(target_model)
    if not is_available:
        error_msg = f"❌ Model unavailable: {reason}\n\nPlease configure required credentials or ensure local runtime is running."
        return "", error_msg, "", "", "", ""
    
    req_list = [r.strip() for r in requirements.split("\n") if r.strip()] if requirements else []
    
    try:
        final_prompt, version_history, evaluation_history = state.orchestrator.generate_and_approve(
            use_case=use_case,
            category=category,
            complexity_tier=complexity_tier,
            context=context,
            requirements=req_list,
            target_model=target_model,
            auto_approve=False  # Manual approval only
        )
        
        state.current_prompt = final_prompt
        state.current_evaluation = evaluation_history[-1] if evaluation_history else None
        state.version_history = version_history
        state.evaluation_history = evaluation_history
        
        # Format displays
        prompt_text = final_prompt.full_prompt
        
        metadata_display = f"""
**Version:** {final_prompt.version}
**Lifecycle State:** {final_prompt.lifecycle_state.upper()}
**Parent Version:** {final_prompt.parent_prompt_id[:8] + "..." if final_prompt.parent_prompt_id else "None (root)"}
**Use Case:** {final_prompt.use_case}
**Category:** {final_prompt.category}
**Complexity Tier:** {final_prompt.complexity_tier}
**Target Model:** {final_prompt.target_model}
**Generated By:** {final_prompt.generated_by}
**Model Adaptations:** {", ".join(final_prompt.model_adaptations_applied) if final_prompt.model_adaptations_applied else "None"}
"""
        
        metrics_display = format_metrics(state.current_evaluation) if state.current_evaluation else "No evaluation yet"
        
        anti_patterns_display = format_anti_patterns(final_prompt.anti_patterns_detected)
        
        economics_display = format_economics(final_prompt)
        
        blockers = []
        if state.current_evaluation:
            can_approve, blockers = state.orchestrator.approval_logic.check_approval_readiness(
                final_prompt,
                state.current_evaluation,
                version_history[0] if len(version_history) > 1 else None
            )
        
        approval_status = format_approval_status(final_prompt, state.current_evaluation, blockers)
        
        return prompt_text, metadata_display, metrics_display, anti_patterns_display, economics_display, approval_status
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", error_msg, "", "", "", ""


def evaluate_prompt() -> Tuple[str, str, str, str]:
    """Manually trigger evaluation."""
    if not state.current_prompt:
        return "", "", "", "⚠️ No prompt to evaluate. Generate a prompt first."
    
    try:
        evaluation = state.orchestrator.evaluator.score_prompt(state.current_prompt)
        state.orchestrator.evaluator.update_prompt_metadata(state.current_prompt, evaluation)
        state.current_evaluation = evaluation
        
        # Update metadata display to show lifecycle_state="evaluated"
        metadata_display = f"""
**Version:** {state.current_prompt.version}
**Lifecycle State:** {state.current_prompt.lifecycle_state.upper()}
**Parent Version:** {state.current_prompt.parent_prompt_id[:8] + "..." if state.current_prompt.parent_prompt_id else "None (root)"}
**Use Case:** {state.current_prompt.use_case}
**Category:** {state.current_prompt.category}
**Complexity Tier:** {state.current_prompt.complexity_tier}
**Target Model:** {state.current_prompt.target_model}
**Generated By:** {state.current_prompt.generated_by}
**Model Adaptations:** {", ".join(state.current_prompt.model_adaptations_applied) if state.current_prompt.model_adaptations_applied else "None"}
**Evaluation Score:** {evaluation.total_score}/10
"""
        
        metrics_display = format_metrics(evaluation)
        anti_patterns_display = format_anti_patterns(state.current_prompt.anti_patterns_detected)
        
        blockers = []
        can_approve, blockers = state.orchestrator.approval_logic.check_approval_readiness(
            state.current_prompt,
            evaluation,
            state.version_history[0] if len(state.version_history) > 1 else None
        )
        approval_status = format_approval_status(state.current_prompt, evaluation, blockers)
        
        return metadata_display, metrics_display, anti_patterns_display, approval_status
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", "", "", error_msg


def refine_prompt() -> Tuple[str, str, str, str, str, str]:
    """Manually trigger refinement."""
    if not state.current_prompt or not state.current_evaluation:
        return "", "", "", "", "", "⚠️ No prompt or evaluation to refine. Generate and evaluate first."
    
    try:
        refined = state.orchestrator.refiner.refine(
            state.current_prompt,
            state.current_evaluation
        )
        
        # Re-evaluate
        previous_score = state.current_evaluation.total_score
        new_evaluation = state.orchestrator.evaluator.score_prompt(
            refined,
            previous_score=previous_score
        )
        # Update metadata with previous_score to calculate delta
        state.orchestrator.evaluator.update_prompt_metadata(refined, new_evaluation, previous_score=previous_score)
        
        state.current_prompt = refined
        state.current_evaluation = new_evaluation
        state.version_history.append(refined)
        state.evaluation_history.append(new_evaluation)
        
        # Format displays
        prompt_text = refined.full_prompt
        
        # Format score delta safely (handle None)
        # Calculate delta if not already set
        if refined.evaluation_delta is None and refined.evaluation_score_before is not None and refined.evaluation_score_after is not None:
            refined.evaluation_delta = refined.evaluation_score_after - refined.evaluation_score_before
        
        score_delta_str = f"{refined.evaluation_delta:+.2f}" if refined.evaluation_delta is not None else "N/A"
        
        metadata_display = f"""
**Version:** {refined.version}
**Lifecycle State:** {refined.lifecycle_state.upper()}
**Parent Version:** {refined.parent_prompt_id[:8] + "..." if refined.parent_prompt_id else "None (root)"}
**Change Reason:** {refined.change_reason or "N/A"}
**Score Before:** {refined.evaluation_score_before if refined.evaluation_score_before is not None else "N/A"}
**Score After:** {refined.evaluation_score_after if refined.evaluation_score_after is not None else "N/A"}
**Score Delta:** {score_delta_str}
"""
        
        metrics_display = format_metrics(new_evaluation)
        anti_patterns_display = format_anti_patterns(refined.anti_patterns_detected)
        economics_display = format_economics(refined)
        
        blockers = []
        can_approve, blockers = state.orchestrator.approval_logic.check_approval_readiness(
            refined,
            new_evaluation,
            state.version_history[-2] if len(state.version_history) > 1 else None
        )
        approval_status = format_approval_status(refined, new_evaluation, blockers)
        
        return prompt_text, metadata_display, metrics_display, anti_patterns_display, economics_display, approval_status
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", error_msg, "", "", "", ""


def approve_prompt() -> Tuple[str, str]:
    """Manually approve prompt."""
    if not state.current_prompt or not state.current_evaluation:
        return "", "⚠️ No prompt or evaluation to approve. Generate and evaluate first."
    
    try:
        can_approve, blockers = state.orchestrator.approval_logic.check_approval_readiness(
            state.current_prompt,
            state.current_evaluation,
            state.version_history[0] if len(state.version_history) > 1 else None
        )
        
        if not can_approve:
            blocker_text = "\n".join(f"  - {b}" for b in blockers)
            return "", f"❌ **Cannot approve.** Blockers:\n{blocker_text}"
        
        approved = state.orchestrator.approval_logic.approve(state.current_prompt)
        state.current_prompt = approved
        
        status = f"✅ **APPROVED**\n\nVersion {approved.version} is now approved and ready for production use."
        metadata_display = f"""
**Version:** {approved.version}
**Lifecycle State:** {approved.lifecycle_state.upper()}
**Parent Version:** {approved.parent_prompt_id[:8] + "..." if approved.parent_prompt_id else "None (root)"}
**Use Case:** {approved.use_case}
**Category:** {approved.category}
**Complexity Tier:** {approved.complexity_tier}
**Target Model:** {approved.target_model}
**Generated By:** {approved.generated_by}
**Approved At:** {approved.approved_at}
**Evaluation Score:** {approved.evaluation_score_after if approved.evaluation_score_after is not None else "N/A"}/10
"""
        
        return status, metadata_display
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", error_msg


def create_ui():
    """Create and return Gradio interface."""
    with gr.Blocks(title="Master Prompt Generator") as ui:
        gr.Markdown("# Master Prompt Generator - Inspection Console")
        gr.Markdown("Generate, evaluate, refine, and approve prompts with full visibility.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Input")
                
                use_case_input = gr.Textbox(
                    label="Use Case",
                    placeholder="e.g., Write a professional follow-up email",
                    lines=2
                )
                
                category_input = gr.Dropdown(
                    label="Category",
                    choices=["business", "technical", "creative", "education", "analysis", "communication", "problem-solving"],
                    value="business"
                )
                
                complexity_input = gr.Slider(
                    label="Complexity Tier",
                    minimum=1,
                    maximum=4,
                    value=2,
                    step=1,
                    info="1=Simple, 2=Intermediate, 3=Advanced, 4=Expert"
                )
                
                context_input = gr.Textbox(
                    label="Context",
                    placeholder="Describe the task and requirements...",
                    lines=5
                )
                
                requirements_input = gr.Textbox(
                    label="Additional Requirements (one per line)",
                    placeholder="Professional tone\nInclude action items",
                    lines=3
                )
                
                # Get all supported models with availability
                all_models = state.model_manager.get_all_supported_models()
                model_choices = []
                
                for model_info in all_models:
                    model_name = model_info["name"]
                    is_available = model_info["available"]
                    unavailable_reason = model_info.get("unavailable_reason", "")
                    
                    # Create display label with availability status
                    if is_available:
                        display_label = f"✅ {model_name}"
                    else:
                        # Shorten reason for dropdown
                        if "Requires API key:" in unavailable_reason:
                            env_var = unavailable_reason.replace("Requires API key: ", "")
                            display_label = f"🔒 {model_name} (needs {env_var})"
                        elif "Ollama not running" in unavailable_reason:
                            display_label = f"🔒 {model_name} (Ollama offline)"
                        else:
                            display_label = f"🔒 {model_name}"
                    
                    # Store as tuple: (display_label, actual_model_name)
                    model_choices.append((display_label, model_name))
                
                # Default to first available model, or first model if none available
                default_model = next((m["name"] for m in all_models if m["available"]), all_models[0]["name"] if all_models else "claude-sonnet")
                
                model_input = gr.Dropdown(
                    label="Target Model",
                    choices=model_choices,
                    value=default_model,
                    info="✅ = Available | 🔒 = Requires setup (API key or local runtime)"
                )
                
                generate_btn = gr.Button("Generate Prompt", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("## Generated Prompt")
                
                prompt_output = gr.Code(
                    label="Prompt Text",
                    language=None,
                    lines=15,
                    interactive=False
                )
                
                metadata_output = gr.Markdown(label="Metadata")
                
                with gr.Row():
                    evaluate_btn = gr.Button("Evaluate", variant="secondary")
                    refine_btn = gr.Button("Refine", variant="secondary")
                    approve_btn = gr.Button("Approve", variant="primary")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Quality Metrics")
                metrics_output = gr.Markdown()
            
            with gr.Column():
                gr.Markdown("## Anti-Patterns")
                anti_patterns_output = gr.Markdown()
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Token Economics")
                economics_output = gr.Markdown()
            
            with gr.Column():
                gr.Markdown("## Approval Status")
                approval_output = gr.Markdown()
        
        # Event handlers
        generate_btn.click(
            fn=generate_prompt,
            inputs=[
                use_case_input,
                category_input,
                complexity_input,
                context_input,
                requirements_input,
                model_input
            ],
            outputs=[
                prompt_output,
                metadata_output,
                metrics_output,
                anti_patterns_output,
                economics_output,
                approval_output
            ]
        )
        
        evaluate_btn.click(
            fn=evaluate_prompt,
            inputs=[],
            outputs=[metadata_output, metrics_output, anti_patterns_output, approval_output]
        )
        
        refine_btn.click(
            fn=refine_prompt,
            inputs=[],
            outputs=[
                prompt_output,
                metadata_output,
                metrics_output,
                anti_patterns_output,
                economics_output,
                approval_output
            ]
        )
        
        approve_btn.click(
            fn=approve_prompt,
            inputs=[],
            outputs=[approval_output, metadata_output]
        )
    
    return ui


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True, share=False, theme=gr.themes.Soft())
