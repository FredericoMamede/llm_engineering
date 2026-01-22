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
except ImportError:
    import sys
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.modes import ModeOrchestrator, InterviewMode
    from evaluation.judge import AnswerJudge


# Initialize components
PROJECT_ROOT = Path(__file__).parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vector_db"

orchestrator = ModeOrchestrator(vector_db_dir=VECTOR_DB_DIR, backend="local")
judge = AnswerJudge()


def format_cited_chunks(cited_chunks) -> str:
    """Format cited chunks for display."""
    if not cited_chunks:
        return "No chunks cited."
    
    formatted = []
    for i, chunk in enumerate(cited_chunks, 1):
        formatted.append(
            f"{i}. **{chunk.headline}**\n"
            f"   Type: {chunk.chunk_type}\n"
            f"   Source: {chunk.source_url}"
        )
    
    return "\n\n".join(formatted)


def format_retrieved_chunks(retrieval_result, show_scores: bool = False) -> str:
    """Format retrieved chunks for display."""
    if not retrieval_result or not retrieval_result.retrieved_chunks:
        return "No chunks retrieved."
    
    formatted = []
    for i, chunk in enumerate(retrieval_result.retrieved_chunks, 1):
        score_info = ""
        if show_scores:
            score_info = f" (similarity: {chunk.similarity_score:.3f})"
        
        formatted.append(
            f"**Chunk {i}**{score_info}\n"
            f"- Headline: {chunk.headline}\n"
            f"- Type: {chunk.chunk_type}\n"
            f"- Source: {chunk.inherited_metadata.get('source_url', 'N/A')}\n"
            f"- Summary: {chunk.summary[:150]}..."
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
    """Format evaluation feedback for display."""
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
    
    strengths_text = "\n".join([f"• {s}" for s in strengths]) if strengths else "None identified."
    gaps_text = "\n".join([f"• {g}" for g in gaps]) if gaps else "None identified."
    missed_text = "\n".join([f"• {m}" for m in missed_concepts]) if missed_concepts else "None identified."
    followup_text = "\n".join([f"• {q}" for q in followup_questions]) if followup_questions else "None suggested."
    
    overall_text = overall_assessment or "No overall assessment available."
    confidence_text = f"{confidence_score}/5"
    
    return strengths_text, gaps_text, missed_text, followup_text, f"{overall_text}\n\n**Confidence Score: {confidence_text}**"


def process_question(
    question: str,
    mode: str,
    candidate_answer: Optional[str],
    debug: bool
) -> Tuple[str, str, str, str, str, str, str, str, str]:
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
            "", "", "", ""
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
                strengths, gaps, missed, followup, overall
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
        
        # Format answer output
        answer_text = answer.answer_text or ""
        confidence = answer.confidence_level.value if answer.confidence_level else "N/A"
        cited_chunks_text = format_cited_chunks(answer.cited_chunks) if answer.cited_chunks else "No chunks cited."
        refusal_reason = answer.refusal_reason or ""
        
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
        else:
            strengths, gaps, missed, followup, overall = "", "", "", "", ""
        
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
            overall
        )
        
    except Exception as e:
        error_msg = f"Error processing question: {str(e)}"
        return (
            "", "N/A", "", error_msg,
            "", "",
            "", "", "", ""
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
                
                debug_checkbox = gr.Checkbox(
                    label="Debug Mode",
                    value=False,
                    info="Show similarity scores and retrieval metadata"
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
        
        # Event handlers
        submit_btn.click(
            fn=process_question,
            inputs=[question_input, mode_dropdown, candidate_answer_input, debug_checkbox],
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
                overall_assessment_output
            ]
        )
        
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
