"""
Gradio UI for AI Interview Preparation Assistant.

This UI provides transparent access to the interview preparation system,
emphasizing visibility over polish.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import gradio as gr

try:
    from core.modes import ModeOrchestrator, InterviewMode
    from evaluation.judge import AnswerJudge
    from .drill_mode import DrillModeManager
    from .weakness_tracker import WeaknessTracker
except ImportError:
    import sys
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.modes import ModeOrchestrator, InterviewMode
    from evaluation.judge import AnswerJudge
    from ui.drill_mode import DrillModeManager
    from ui.weakness_tracker import WeaknessTracker


# Initialize components
PROJECT_ROOT = Path(__file__).parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vector_db"

orchestrator = ModeOrchestrator(vector_db_dir=VECTOR_DB_DIR, backend="local")
judge = AnswerJudge()
drill_manager = DrillModeManager()
weakness_tracker = WeaknessTracker()


def format_cited_chunks(cited_chunks) -> str:
    """Format cited chunks for display with badges."""
    if not cited_chunks:
        return "No chunks cited."
    
    formatted = []
    for i, chunk in enumerate(cited_chunks, 1):
        # Badge for chunk type
        type_badge = f"`{chunk.chunk_type}`"
        formatted.append(
            f"**{i}. {chunk.headline}** {type_badge}\n"
            f"   📎 [Source]({chunk.source_url})"
        )
    
    return "\n\n".join(formatted)


def format_retrieved_chunks(retrieval_result, show_scores: bool = False) -> str:
    """Format retrieved chunks for display with badges and highlighting."""
    if not retrieval_result or not retrieval_result.retrieved_chunks:
        return "No chunks retrieved."
    
    formatted = []
    for i, chunk in enumerate(retrieval_result.retrieved_chunks, 1):
        score_info = ""
        if show_scores:
            # Color-code similarity scores
            score = chunk.similarity_score
            if score >= 0.7:
                score_color = "🟢"
            elif score >= 0.5:
                score_color = "🟡"
            else:
                score_color = "🔴"
            score_info = f" {score_color} `{score:.3f}`"
        
        # Badge for chunk type
        type_badge = f"`{chunk.chunk_type}`"
        
        formatted.append(
            f"**Chunk {i}** {type_badge}{score_info}\n"
            f"- **{chunk.headline}**\n"
            f"- 📎 [Source]({chunk.inherited_metadata.get('source_url', 'N/A')})\n"
            f"- {chunk.summary[:150]}..."
        )
    
    return "\n\n".join(formatted)


def format_retrieval_metadata(retrieval_result, mode_config: Dict[str, Any]) -> str:
    """Format retrieval metadata for debug display."""
    if not retrieval_result:
        return "No retrieval metadata available."
    
    metadata = retrieval_result.retrieval_metadata
    lines = [
        "**Retrieval Metadata:**",
        f"- Original Query: {retrieval_result.original_query}",
        f"- Rewritten Query: {retrieval_result.rewritten_query or 'N/A'}",
        f"- Total Candidates: {metadata.get('total_candidates', 'N/A')}",
        f"- Total Returned: {len(retrieval_result.retrieved_chunks)}",
        f"- Backend: {metadata.get('backend', 'N/A')}",
        "",
        "**Mode Configuration:**",
        f"- Top K (Original): {mode_config.get('top_k_original', 'N/A')}",
        f"- Top K (Rewritten): {mode_config.get('top_k_rewritten', 'N/A')}",
        f"- Final K: {mode_config.get('final_k', 'N/A')}",
        f"- Filters Applied: {mode_config.get('filters_applied', {})}",
    ]
    
    return "\n".join(lines)


def format_evaluation_feedback(feedback) -> Tuple[str, str, str, str, str]:
    """Format evaluation feedback for display with badges and highlighting."""
    if not feedback:
        return "", "", "", "", ""
    
    # Handle both EvaluationFeedback object and dict
    if hasattr(feedback, 'strengths'):
        strengths = feedback.strengths
        gaps = feedback.gaps
        missed_concepts = feedback.missed_concepts
        followup_questions = feedback.followup_questions
        overall_assessment = feedback.overall_assessment
        confidence_score = feedback.confidence_score
    elif isinstance(feedback, dict):
        strengths = feedback.get("strengths", [])
        gaps = feedback.get("gaps", [])
        missed_concepts = feedback.get("missed_concepts", [])
        followup_questions = feedback.get("followup_questions", [])
        overall_assessment = feedback.get("overall_assessment", feedback.get("evaluation_text", ""))
        confidence_score = feedback.get("confidence_score", 3)
    else:
        return "", "", "", "", ""
    
    # Format with badges and highlighting
    strengths_text = "\n".join([f"✅ {s}" for s in strengths]) if strengths else "*None identified.*"
    gaps_text = "\n".join([f"⚠️ {g}" for g in gaps]) if gaps else "*None identified.*"
    missed_text = "\n".join([f"❌ {m}" for m in missed_concepts]) if missed_concepts else "*None identified.*"
    followup_text = "\n".join([f"💡 {q}" for q in followup_questions]) if followup_questions else "*None suggested.*"
    
    overall_text = overall_assessment or "No overall assessment available."
    
    # Confidence badge with color
    if confidence_score >= 4:
        confidence_badge = f"🟢 **{confidence_score}/5**"
    elif confidence_score >= 3:
        confidence_badge = f"🟡 **{confidence_score}/5**"
    else:
        confidence_badge = f"🔴 **{confidence_score}/5**"
    
    return strengths_text, gaps_text, missed_text, followup_text, f"{overall_text}\n\n**Confidence Score:** {confidence_badge}"


def process_question(
    question: str,
    mode: str,
    candidate_answer: Optional[str],
    debug: bool,
    use_drill_mode: bool = False
) -> Tuple[str, str, str, str, str, str, str, str, str, str, str]:
    """
    Process an interview question and optionally evaluate a candidate answer.
    
    Returns:
        Tuple of (answer_text, confidence, cited_chunks, refusal_reason,
                  retrieved_context, retrieval_metadata, strengths, gaps,
                  missed_concepts, followup_questions, overall_assessment)
    """
    if not question or not question.strip():
        return (
            "", "N/A", "", "",
            "Please enter a question.", "",
            "", "", "", "",
            ""  # drill_context
        )
    
    try:
        # Convert mode string to enum
        mode_enum = InterviewMode(mode)
        
        # Process with orchestrator
        result = orchestrator.process(
            query=question.strip(),
            mode=mode_enum,
            candidate_response=candidate_answer.strip() if candidate_answer else None,
            debug=debug
        )
        
        # Handle Evaluation Mode (different output structure)
        if mode_enum == InterviewMode.EVALUATION and candidate_answer:
            # In evaluation mode, the result contains an evaluation dict
            # that has the evaluation feedback structure
            evaluation_dict = result.get("evaluation", {})
            
            # Format evaluation feedback (handles both dict and EvaluationFeedback object)
            strengths, gaps, missed, followup, overall = format_evaluation_feedback(evaluation_dict)
            
            # For evaluation mode, we don't have a regular answer
            return (
                "", "N/A", "", "",
                format_retrieved_chunks(result.get("retrieval_result"), show_scores=debug),
                format_retrieval_metadata(result.get("retrieval_result"), result.get("mode_config", {})),
                strengths, gaps, missed, followup, overall,
                ""  # drill_context
            )
        
        # Regular mode processing
        answer = result.get("answer")
        
        if not answer:
            return (
                "", "N/A", "", "No answer generated.",
                format_retrieved_chunks(result.get("retrieval_result"), show_scores=debug),
                format_retrieval_metadata(result.get("retrieval_result"), result.get("mode_config", {})),
                "", "", "", ""
            )
        
        # Format answer output with interview-native structure
        answer_text = answer.answer_text or ""
        
        # Add confidence badge
        if answer.confidence_level:
            conf_value = answer.confidence_level.value
            if conf_value == "high":
                confidence = "🟢 **HIGH**"
            elif conf_value == "medium":
                confidence = "🟡 **MEDIUM**"
            else:
                confidence = "🔴 **LOW**"
        else:
            confidence = "N/A"
        
        cited_chunks_text = format_cited_chunks(answer.cited_chunks) if answer.cited_chunks else "No chunks cited."
        
        # Format refusal reason with highlighting
        if answer.refusal_reason:
            refusal_reason = f"⚠️ **Refusal:** {answer.refusal_reason}"
        else:
            refusal_reason = ""
        
        # Format retrieved context
        retrieved_context = format_retrieved_chunks(
            result.get("retrieval_result"),
            show_scores=debug
        )
        
        # Format metadata
        retrieval_metadata = format_retrieval_metadata(
            result.get("retrieval_result"),
            result.get("mode_config", {})
        )
        
        # Handle follow-up question (Interviewer Mode)
        followup_question = result.get("followup_question")
        if followup_question:
            answer_text += f"\n\n---\n\n**Follow-up Question:**\n{followup_question}"
        
        # Evaluate candidate answer if provided (non-evaluation mode)
        evaluation_feedback = None
        if candidate_answer and candidate_answer.strip() and mode_enum != InterviewMode.EVALUATION:
            try:
                evaluation_feedback = judge.evaluate(
                    question=question.strip(),
                    candidate_answer=candidate_answer.strip(),
                    retrieval_result=result.get("retrieval_result"),
                    reference_answer=answer
                )
            except Exception as e:
                evaluation_feedback = None
        
        # Format evaluation if available
        if evaluation_feedback:
            strengths, gaps, missed, followup, overall = format_evaluation_feedback(evaluation_feedback)
            
            # Track weaknesses if candidate answer was provided
            if candidate_answer and candidate_answer.strip() and missed:
                # Extract topic from question (simple heuristic)
                topic = None
                question_lower = question.lower()
                if "typescript" in question_lower:
                    topic = "TypeScript"
                elif "react" in question_lower:
                    topic = "React"
                elif "postgresql" in question_lower or "postgres" in question_lower:
                    topic = "PostgreSQL"
                elif "redis" in question_lower:
                    topic = "Redis"
                elif "node" in question_lower:
                    topic = "Node.js"
                
                # Extract missed concepts list
                missed_list = [m.strip().lstrip("❌").strip() for m in missed.split("\n") if m.strip() and m.strip() != "*None identified.*"]
                if missed_list:
                    weakness_tracker.record_missed_concepts(
                        concepts=missed_list,
                        question=question,
                        topic=topic
                    )
            
            # Add to drill session if enabled
            if use_drill_mode:
                drill_manager.add_turn(
                    question=question,
                    answer=answer_text,
                    mode=mode,
                    evaluation={
                        "strengths": strengths,
                        "gaps": gaps,
                        "missed_concepts": missed,
                        "overall": overall
                    } if evaluation_feedback else None
                )
        else:
            strengths, gaps, missed, followup, overall = "", "", "", "", ""
            
            # Add to drill session even without evaluation
            if use_drill_mode:
                drill_manager.add_turn(
                    question=question,
                    answer=answer_text,
                    mode=mode
                )
        
        # Get drill context if available
        drill_context = ""
        if use_drill_mode:
            context = drill_manager.get_conversation_context()
            if context:
                drill_context = f"**Recent Context:**\n{context}\n\n"
        
        return (
            answer_text,
            confidence,
            cited_chunks_text,
            refusal_reason,
            retrieved_context,
            retrieval_metadata,
            strengths,
            gaps,
            missed,
            followup,
            overall,
            drill_context
        )
        
    except Exception as e:
        error_msg = f"Error processing question: {str(e)}"
        return (
            "", "N/A", "", error_msg,
            "", "",
            "", "", "", "",
            ""  # drill_context
        )


def create_ui():
    """Create and return the Gradio interface."""
    
    # Mode options
    mode_options = [
        ("Explain Mode", InterviewMode.EXPLAIN.value),
        ("Interviewer Mode", InterviewMode.INTERVIEWER.value),
        ("Evaluation Mode", InterviewMode.EVALUATION.value),
        ("Company-Aware Mode", InterviewMode.COMPANY_AWARE.value),
        ("System Design Mode", InterviewMode.SYSTEM_DESIGN.value),
        ("Rapid Fire Mode", InterviewMode.RAPID_FIRE.value),
    ]
    
    with gr.Blocks(title="AI Interview Preparation Assistant") as app:
        gr.Markdown("""
        # AI Interview Preparation Assistant
        
        Ask interview questions and get grounded answers based on retrieved knowledge.
        All answers are strictly grounded in the knowledge base - no hallucinations.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Inputs
                question_input = gr.Textbox(
                    label="Interview Question",
                    placeholder="e.g., How does TypeScript help with large-scale development?",
                    lines=3
                )
                
                mode_dropdown = gr.Dropdown(
                    choices=[opt[1] for opt in mode_options],
                    value=InterviewMode.EXPLAIN.value,
                    label="Interview Mode",
                    info="Select the interview mode for different behaviors"
                )
                
                candidate_answer_input = gr.Textbox(
                    label="Your Answer (Optional - for evaluation)",
                    placeholder="Enter your answer here to get feedback...",
                    lines=5,
                    visible=True
                )
                
                with gr.Row():
                    debug_checkbox = gr.Checkbox(
                        label="Debug Mode",
                        value=False,
                        info="Show similarity scores and retrieval metadata"
                    )
                    
                    drill_mode_checkbox = gr.Checkbox(
                        label="Drill Mode",
                        value=False,
                        info="Track conversation history for iterative practice"
                    )
                
                submit_btn = gr.Button("Ask Question", variant="primary")
            
            with gr.Column(scale=3):
                # Answer Output
                with gr.Group():
                    gr.Markdown("### Generated Answer")
                    answer_output = gr.Markdown(label="Answer")
                    
                    with gr.Row():
                        confidence_output = gr.Textbox(
                            label="Confidence Level",
                            interactive=False
                        )
                        refusal_output = gr.Textbox(
                            label="Refusal Reason (if applicable)",
                            interactive=False,
                            visible=True
                        )
                    
                    cited_chunks_output = gr.Markdown(
                        label="Cited Chunks",
                        visible=True
                    )
        
        # Retrieved Context Panel
        with gr.Accordion("Retrieved Context", open=False):
            retrieved_context_output = gr.Markdown(label="Retrieved Chunks")
        
        # Debug Panel
        with gr.Accordion("Debug Information", open=False):
            retrieval_metadata_output = gr.Markdown(label="Retrieval Metadata")
        
        # Evaluation Panel
        with gr.Accordion("Answer Evaluation (if candidate answer provided)", open=False):
            with gr.Row():
                with gr.Column():
                    strengths_output = gr.Markdown(label="Strengths")
                    gaps_output = gr.Markdown(label="Gaps")
                with gr.Column():
                    missed_concepts_output = gr.Markdown(label="Missed Concepts")
                    followup_questions_output = gr.Markdown(label="Follow-up Questions")
            
            overall_assessment_output = gr.Markdown(label="Overall Assessment")
        
        # Drill Mode Context Panel
        drill_context_output = gr.Markdown(
            label="Drill Mode Context",
            visible=False
        )
        
        # Weakness Tracking Panel
        with gr.Accordion("Tracked Weaknesses", open=False):
            weakness_summary_output = gr.Markdown(label="Weakness Summary")
            refresh_weaknesses_btn = gr.Button("Refresh Weaknesses", variant="secondary")
        
        def refresh_weaknesses():
            """Refresh weakness summary."""
            return weakness_tracker.get_weakness_summary()
        
        def toggle_drill_mode(enable: bool):
            """Toggle drill mode and start/end session."""
            if enable:
                drill_manager.start_session()
                return gr.update(visible=True)
            else:
                drill_manager.end_session()
                return gr.update(visible=False)
        
        # Event handlers
        submit_btn.click(
            fn=process_question,
            inputs=[question_input, mode_dropdown, candidate_answer_input, debug_checkbox, drill_mode_checkbox],
            outputs=[
                answer_output,
                confidence_output,
                cited_chunks_output,
                refusal_output,
                retrieved_context_output,
                retrieval_metadata_output,
                strengths_output,
                gaps_output,
                missed_concepts_output,
                followup_questions_output,
                overall_assessment_output,
                drill_context_output
            ]
        )
        
        drill_mode_checkbox.change(
            fn=toggle_drill_mode,
            inputs=[drill_mode_checkbox],
            outputs=[drill_context_output]
        )
        
        refresh_weaknesses_btn.click(
            fn=refresh_weaknesses,
            outputs=[weakness_summary_output]
        )
        
        # Load initial weakness summary
        weakness_summary_output.value = weakness_tracker.get_weakness_summary()
        
        # Example questions
        gr.Markdown("""
        ### Example Questions
        
        - "What is TypeScript and why is it useful?"
        - "How does React handle state management?"
        - "Explain PostgreSQL JSONB capabilities"
        - "What are the tradeoffs of using Redis for caching?"
        - "How would you design a high-throughput chat system?"
        """)
    
    return app


def main():
    """Launch the Gradio app."""
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
