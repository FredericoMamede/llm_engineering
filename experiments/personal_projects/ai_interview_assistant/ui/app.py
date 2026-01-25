"""
Gradio UI for AI Interview Preparation Assistant.

This UI provides transparent access to the interview preparation system,
emphasizing visibility over polish.
"""

from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import gradio as gr

try:
    from core.modes import ModeOrchestrator, InterviewMode
    from evaluation.judge import AnswerJudge
    from core.interview_simulator import InterviewSimulator, Difficulty, Outcome, ExaminerPersonality
    from core.config_loader import ConfigLoader
    from evaluation.analysis import (
        load_evaluation_run,
        rank_weakest_requirements,
        analyze_chunk_type_usage,
        find_retrieval_answer_mismatches,
        compare_evaluation_runs,
        generate_analysis_summary
    )
    from .drill_mode import DrillModeManager
    from .weakness_tracker import WeaknessTracker
except ImportError:
    import sys
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.modes import ModeOrchestrator, InterviewMode
    from evaluation.judge import AnswerJudge
    from core.interview_simulator import InterviewSimulator, Difficulty, Outcome, ExaminerPersonality
    from core.config_loader import ConfigLoader
    from evaluation.analysis import (
        load_evaluation_run,
        rank_weakest_requirements,
        analyze_chunk_type_usage,
        find_retrieval_answer_mismatches,
        compare_evaluation_runs,
        generate_analysis_summary
    )
    from ui.drill_mode import DrillModeManager
    from ui.weakness_tracker import WeaknessTracker


# Initialize components
PROJECT_ROOT = Path(__file__).parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vector_db"

orchestrator = ModeOrchestrator(vector_db_dir=VECTOR_DB_DIR, backend="local")
judge = AnswerJudge()
drill_manager = DrillModeManager()
weakness_tracker = WeaknessTracker()
simulator = InterviewSimulator(vector_db_dir=VECTOR_DB_DIR, backend="local")
config_loader = ConfigLoader()


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


def create_interview_simulator_ui():
    """Create the Interview Simulator UI tab."""
    
    with gr.Column():
        gr.Markdown("""
        ## Interview Simulator
        
        The system asks questions, you answer, and we evaluate. Teaching is available on demand only.
        All questions are grounded in the knowledge base.
        """)
        
        # Session Configuration
        with gr.Accordion("Session Configuration", open=True):
            # Load available options
            companies = config_loader.load_companies()
            requirement_sets = config_loader.load_requirement_sets()
            
            company_choices = [(c['name'], c['id']) for c in companies] if companies else [("Eventyr", "eventyr")]
            req_set_choices = [(r['name'], r['id']) for r in requirement_sets] if requirement_sets else [("AI-First MERN Fullstack Developer", "ai-first-mern-fullstack")]
            
            with gr.Row():
                company_dropdown = gr.Dropdown(
                    choices=company_choices,
                    value=company_choices[0][1] if company_choices else "eventyr",
                    label="Company",
                    interactive=True,
                    info="Select company context for questions"
                )
                requirement_set_dropdown = gr.Dropdown(
                    choices=req_set_choices,
                    value=req_set_choices[0][1] if req_set_choices else "ai-first-mern-fullstack",
                    label="Requirement Set",
                    interactive=True,
                    info="Select requirement set to focus on"
                )
            
            with gr.Row():
                difficulty_dropdown = gr.Dropdown(
                    choices=["easy", "medium", "hard"],
                    value="medium",
                    label="Target Difficulty",
                    interactive=True
                )
                examiner_personality_dropdown = gr.Dropdown(
                    choices=["strict", "balanced", "supportive"],
                    value="balanced",
                    label="Examiner Personality",
                    interactive=True,
                    info="Strict: High bar, minimal feedback | Balanced: Realistic | Supportive: Teaching-oriented"
                )
            
            with gr.Row():
                session_length_input = gr.Number(
                    label="Max Questions (optional)",
                    value=None,
                    interactive=True,
                    precision=0
                )
            
            focus_areas_input = gr.Textbox(
                label="Focus Areas (comma-separated, optional)",
                placeholder="e.g., TypeScript, React, PostgreSQL",
                interactive=True
            )
            
            with gr.Row():
                start_session_btn = gr.Button("Start Session", variant="primary")
                end_session_btn = gr.Button("End Session", variant="stop")
        
        # Current Question Panel
        with gr.Group():
            gr.Markdown("### Current Question")
            question_display = gr.Markdown(
                value="**No active question. Start a session to begin.**",
                label="Question"
            )
            
            with gr.Row():
                requirement_tag = gr.Textbox(
                    label="Requirement/Domain",
                    interactive=False,
                    visible=False
                )
                difficulty_tag = gr.Textbox(
                    label="Difficulty",
                    interactive=False
                )
        
        # Answer Input
        with gr.Group():
            gr.Markdown("### Your Answer")
            answer_input = gr.Textbox(
                label="Answer",
                placeholder="Enter your answer here...",
                lines=5,
                interactive=True
            )
            submit_answer_btn = gr.Button("Submit Answer", variant="primary")
        
        # Evaluation Panel
        with gr.Accordion("Evaluation", open=True):
            evaluation_status = gr.Markdown(
                value="**No evaluation yet. Submit an answer to see feedback.**",
                label="Status"
            )
            
            with gr.Row():
                with gr.Column():
                    eval_strengths = gr.Markdown(label="Strengths")
                    eval_gaps = gr.Markdown(label="Gaps")
                with gr.Column():
                    eval_missed = gr.Markdown(label="Missed Concepts")
                    eval_followup = gr.Markdown(label="Follow-up Questions")
            
            eval_overall = gr.Markdown(label="Overall Assessment")
            eval_outcome = gr.Textbox(
                label="Outcome",
                interactive=False
            )
        
        # Teaching Panel (conditional)
        with gr.Accordion("Teaching (On Demand)", open=False):
            teaching_display = gr.Markdown(
                value="**Teaching content will appear here when requested.**",
                label="Explanation"
            )
            
            with gr.Row():
                teach_full_btn = gr.Button("Teach Me (Full Explanation)", variant="secondary")
                teach_ideal_btn = gr.Button("Show Ideal Answer", variant="secondary")
                teach_why_weak_btn = gr.Button("Why Was My Answer Weak?", variant="secondary")
                teach_missed_btn = gr.Button("Explain Missed Concepts", variant="secondary")
        
        # Control Panel
        with gr.Group():
            gr.Markdown("### Actions")
            with gr.Row():
                next_question_btn = gr.Button("Next Question", variant="primary")
                retry_question_btn = gr.Button("Retry Question", variant="secondary")
                followup_question_btn = gr.Button("Ask Follow-up", variant="secondary")
                move_on_btn = gr.Button("Move On", variant="secondary")
        
        # Progress Panel
        with gr.Accordion("Progress", open=False):
            progress_display = gr.Markdown(
                value="**No progress data yet.**",
                label="Session Progress"
            )
        
        # Coverage Visualization Panel
        with gr.Accordion("Coverage Visualization", open=False):
            coverage_display = gr.Markdown(
                value="**No coverage data yet.**",
                label="Coverage by Requirement, Topic, and Chunk Type"
            )
        
        # Session Summary (when ended)
        with gr.Accordion("Session Summary", open=False, visible=False) as summary_accordion:
            session_summary_display = gr.Markdown(
                value="",
                label="Session Summary"
            )
            with gr.Row():
                export_json_btn = gr.Button("Export as JSON", variant="secondary")
                export_markdown_btn = gr.Button("Export as Markdown", variant="secondary")
        
        # State management
        session_state_var = gr.State(value=None)
        
        def update_progress(session_state):
            """Update progress display."""
            if not session_state:
                return gr.update(value="**No active session.**")
            
            try:
                session = simulator.current_session
                if not session:
                    return gr.update(value="**No active session.**")
                
                total_q = len(session.questions_asked)
                total_a = len(session.answers_given)
                total_e = len(session.evaluations)
                
                correct = sum(1 for e in session.evaluations if e.outcome == Outcome.CORRECT)
                partial = sum(1 for e in session.evaluations if e.outcome == Outcome.PARTIAL)
                incorrect = sum(1 for e in session.evaluations if e.outcome == Outcome.INCORRECT)
                
                accuracy = (correct / total_e * 100) if total_e > 0 else 0
                
                progress_text = f"""
## Session Progress

**Questions Asked:** {total_q}
**Answers Given:** {total_a}
**Evaluations:** {total_e}

### Results
- ✅ **Correct:** {correct}
- ⚠️ **Partial:** {partial}
- ❌ **Incorrect:** {incorrect}
- **Accuracy:** {accuracy:.1f}%

### Current Status
- **Difficulty:** {session.current_difficulty.value.upper()}
- **Consecutive Correct:** {session.consecutive_correct}
- **Consecutive Incorrect:** {session.consecutive_incorrect}

### Coverage
- **Requirements Covered:** {len(session.covered_requirements)}
- **Domains Covered:** {len(session.covered_domains)}
- **Weaknesses Triggered:** {len(session.weaknesses_triggered)}
"""
                return gr.update(value=progress_text)
            except Exception as e:
                return gr.update(value=f"**Error: {str(e)}**")
        
        def update_coverage(session_state):
            """Update coverage visualization."""
            if not session_state:
                return gr.update(value="**No active session.**")
            
            try:
                session = simulator.current_session
                if not session:
                    return gr.update(value="**No active session.**")
                
                # Build coverage visualization
                coverage_lines = ["## Coverage Visualization\n"]
                
                # Coverage by requirement
                if session.coverage_by_requirement:
                    coverage_lines.append("### By Requirement ID")
                    for req_id, count in sorted(session.coverage_by_requirement.items(), key=lambda x: x[1], reverse=True)[:10]:
                        coverage_lines.append(f"- **Requirement {req_id}**: {count} question(s)")
                    coverage_lines.append("")
                
                # Coverage by topic
                if session.coverage_by_topic:
                    coverage_lines.append("### By Topic")
                    for topic, count in sorted(session.coverage_by_topic.items(), key=lambda x: x[1], reverse=True)[:10]:
                        coverage_lines.append(f"- **{topic}**: {count} question(s)")
                    coverage_lines.append("")
                
                # Coverage by chunk type
                if session.coverage_by_chunk_type:
                    coverage_lines.append("### By Chunk Type")
                    for chunk_type, count in sorted(session.coverage_by_chunk_type.items(), key=lambda x: x[1], reverse=True):
                        coverage_lines.append(f"- **{chunk_type}**: {count} question(s)")
                    coverage_lines.append("")
                
                if len(coverage_lines) == 1:
                    coverage_lines.append("**No coverage data yet.**")
                
                return gr.update(value="\n".join(coverage_lines))
            except Exception as e:
                return gr.update(value=f"**Error: {str(e)}**")
        
        def start_session(company_id, req_set_id, difficulty, personality, session_length, focus_areas):
            """Start a new interview session."""
            try:
                # Get company and requirement set names
                company_data = config_loader.get_company_by_id(company_id)
                req_set_data = config_loader.get_requirement_set_by_id(req_set_id)
                
                company_name = company_data['name'] if company_data else company_id
                req_set_name = req_set_data['name'] if req_set_data else req_set_id
                
                # Parse focus areas
                focus_list = [f.strip() for f in focus_areas.split(",") if f.strip()] if focus_areas else []
                
                # Parse difficulty
                diff_enum = Difficulty(difficulty.lower())
                
                # Parse personality (handle both string and tuple from dropdown)
                if isinstance(personality, (list, tuple)):
                    personality_str = personality[1] if len(personality) > 1 else personality[0]
                else:
                    personality_str = str(personality)
                personality_enum = ExaminerPersonality(personality_str.lower())
                
                # Parse session length
                length = int(session_length) if session_length else None
                
                session = simulator.start_session(
                    company=company_name,
                    requirement_set=req_set_name,
                    difficulty_target=diff_enum,
                    focus_areas=focus_list,
                    session_length=length,
                    examiner_personality=personality_enum
                )
                
                # Generate first question
                question = simulator.generate_question()
                
                if question:
                    return (
                        gr.update(value=f"**{question.question_text}**"),
                        gr.update(value=question.requirement_id or question.company_domain or "N/A"),
                        gr.update(value=question.difficulty.value.upper()),
                        gr.update(value=""),
                        gr.update(value="**Session started. Answer the question above.**"),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value="**No coverage data yet.**"),
                        session
                    )
                else:
                    return (
                        gr.update(value="**Error generating question. Please try again.**"),
                        gr.update(value="N/A"),
                        gr.update(value="N/A"),
                        gr.update(value=""),
                        gr.update(value="**Error: Could not generate question.**"),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        session
                    )
            except Exception as e:
                return (
                    gr.update(value=f"**Error: {str(e)}**"),
                    gr.update(value="N/A"),
                    gr.update(value="N/A"),
                    gr.update(value=""),
                    gr.update(value=f"**Error starting session: {str(e)}**"),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value="**No coverage data yet.**"),
                    None
                )
        
        def submit_answer(answer_text, session_state):
            """Submit answer and evaluate."""
            if not session_state or not answer_text:
                return (
                    gr.update(),
                    gr.update(value="**Please enter an answer.**"),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(),
                    session_state
                )
            
            try:
                evaluation = simulator.submit_answer(answer_text)
                
                if not evaluation:
                    return (
                        gr.update(),
                        gr.update(value="**Error: No active question.**"),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        gr.update(value=""),
                        session_state
                    )
                
                # Format evaluation
                feedback = evaluation.evaluation
                strengths_text = "\n".join([f"✅ {s}" for s in feedback.strengths]) if feedback.strengths else "*None*"
                gaps_text = "\n".join([f"⚠️ {g}" for g in feedback.gaps]) if feedback.gaps else "*None*"
                missed_text = "\n".join([f"❌ {m}" for m in feedback.missed_concepts]) if feedback.missed_concepts else "*None*"
                followup_text = "\n".join([f"💡 {q}" for q in feedback.followup_questions]) if feedback.followup_questions else "*None*"
                
                outcome_text = {
                    Outcome.CORRECT: "✅ **CORRECT** - Strong answer!",
                    Outcome.PARTIAL: "⚠️ **PARTIAL** - Some gaps.",
                    Outcome.INCORRECT: "❌ **INCORRECT** - Needs improvement."
                }.get(evaluation.outcome, "Unknown")
                
                outcome_text += f"\n\n**Confidence Score:** {feedback.confidence_score}/5"
                
                # Update coverage visualization
                coverage_update = update_coverage(session_state)
                
                return (
                    gr.update(),
                    gr.update(value="**Evaluation complete. See details below.**"),
                    gr.update(value=strengths_text),
                    gr.update(value=gaps_text),
                    gr.update(value=missed_text),
                    gr.update(value=followup_text),
                    gr.update(value=feedback.overall_assessment),
                    gr.update(value=outcome_text),
                    coverage_update,
                    session_state
                )
            except Exception as e:
                return (
                    gr.update(),
                    gr.update(value=f"**Error evaluating answer: {str(e)}**"),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value=""),
                    gr.update(value="**Error updating coverage.**"),
                    session_state
                )
        
        def teach_explanation(explanation_type, session_state):
            """Generate teaching explanation."""
            if not session_state:
                return gr.update(value="**No active session.**")
            
            try:
                answer = simulator.teach(explanation_type=explanation_type)
                if answer and answer.answer_text:
                    return gr.update(value=answer.answer_text)
                else:
                    return gr.update(value="**Could not generate explanation.**")
            except Exception as e:
                return gr.update(value=f"**Error: {str(e)}**")
        
        def next_question(session_state):
            """Generate next question."""
            if not session_state:
                return (
                    gr.update(value="**No active session. Start a session first.**"),
                    gr.update(value="N/A"),
                    gr.update(value="N/A"),
                    gr.update(value=""),
                    gr.update(value="**No active session.**"),
                    session_state
                )
            
            try:
                question = simulator.generate_question()
                if question:
                    return (
                        gr.update(value=f"**{question.question_text}**"),
                        gr.update(value=question.requirement_id or question.company_domain or "N/A"),
                        gr.update(value=question.difficulty.value.upper()),
                        gr.update(value=""),
                        gr.update(value="**New question generated. Answer above.**"),
                        session_state
                    )
                else:
                    return (
                        gr.update(value="**Error generating question.**"),
                        gr.update(value="N/A"),
                        gr.update(value="N/A"),
                        gr.update(value=""),
                        gr.update(value="**Error: Could not generate question.**"),
                        session_state
                    )
            except Exception as e:
                return (
                    gr.update(value=f"**Error: {str(e)}**"),
                    gr.update(value="N/A"),
                    gr.update(value="N/A"),
                    gr.update(value=""),
                    gr.update(value=f"**Error: {str(e)}**"),
                    session_state
                )
        
        def format_session_summary(summary: Dict[str, Any]) -> str:
            """Format session summary as markdown."""
            duration_min = summary.get('duration_seconds', 0) // 60
            duration_sec = summary.get('duration_seconds', 0) % 60
            
            summary_text = f"""## Session Summary

**Session ID:** {summary['session_id']}
**Started:** {summary['started_at'][:19] if summary.get('started_at') else 'N/A'}
**Ended:** {summary['ended_at'][:19] if summary.get('ended_at') else 'N/A'}
**Duration:** {duration_min}m {duration_sec}s

### Statistics
- **Total Questions:** {summary['total_questions']}
- **Total Answers:** {summary['total_answers']}
- **Total Evaluations:** {summary['total_evaluations']}
- **Accuracy:** {summary['accuracy']}%
- **Correct:** {summary['correct']}
- **Partial:** {summary['partial']}
- **Incorrect:** {summary['incorrect']}
- **Final Difficulty:** {summary['final_difficulty'].upper()}

### Strong Areas
"""
            strong_areas = summary.get('strong_areas', {})
            if strong_areas.get('requirements'):
                summary_text += "\n**Requirements:**\n"
                for req_id in strong_areas['requirements']:
                    summary_text += f"- Requirement {req_id}\n"
            if strong_areas.get('domains'):
                summary_text += "\n**Company Domains:**\n"
                for domain in strong_areas['domains']:
                    summary_text += f"- {domain}\n"
            
            summary_text += "\n### Weak Areas\n"
            weaknesses = summary.get('weak_areas', [])
            if weaknesses:
                for w in weaknesses[:5]:
                    summary_text += f"- {w}\n"
            else:
                summary_text += "*None identified*\n"
            
            summary_text += "\n### Coverage\n"
            covered = summary.get('covered_topics', {})
            summary_text += f"- **Requirements Covered:** {len(covered.get('requirements', []))}\n"
            summary_text += f"- **Domains Covered:** {len(covered.get('domains', []))}\n"
            
            # Example questions
            examples = summary.get('example_questions', [])
            if examples:
                summary_text += "\n### Example Questions\n"
                for ex in examples:
                    summary_text += f"\n**Q:** {ex['question'][:100]}...\n"
                    summary_text += f"- Difficulty: {ex['difficulty'].upper()}\n"
                    summary_text += f"- Outcome: {ex['outcome'].upper()}\n"
                    summary_text += f"- Confidence: {ex['confidence_score']}/5\n"
            
            summary_text += "\n### Recommendations\n"
            recommendations = summary.get('recommendations', [])
            if recommendations:
                for r in recommendations:
                    summary_text += f"- {r}\n"
            else:
                summary_text += "*Continue practicing*\n"
            
            return summary_text
        
        def end_session(session_state):
            """End session and generate summary."""
            if not session_state:
                return (
                    gr.update(value="**No active session.**"),
                    gr.update(visible=False),
                    None
                )
            
            try:
                summary = simulator.end_session()
                if summary:
                    summary_text = format_session_summary(summary)
                    return (
                        gr.update(value=summary_text),
                        gr.update(visible=True),
                        summary
                    )
                else:
                    return (
                        gr.update(value="**Error generating summary.**"),
                        gr.update(visible=True),
                        None
                    )
            except Exception as e:
                return (
                    gr.update(value=f"**Error: {str(e)}**"),
                    gr.update(visible=True),
                    None
                )
        
        summary_data_var = gr.State(value=None)
        
        def export_summary_json(summary_data):
            """Export summary as JSON."""
            if not summary_data:
                return "No summary data available."
            
            import json
            return json.dumps(summary_data, indent=2, ensure_ascii=False)
        
        def export_summary_markdown(summary_data):
            """Export summary as Markdown."""
            if not summary_data:
                return "No summary data available."
            
            return format_session_summary(summary_data)
        
        # Event handlers
        start_session_btn.click(
            fn=start_session,
            inputs=[company_dropdown, requirement_set_dropdown, difficulty_dropdown, examiner_personality_dropdown, session_length_input, focus_areas_input],
            outputs=[
                question_display, requirement_tag, difficulty_tag, answer_input,
                evaluation_status, eval_strengths, eval_gaps, eval_missed, eval_followup,
                eval_overall, eval_outcome, coverage_display, session_state_var
            ]
        )
        
        submit_answer_btn.click(
            fn=submit_answer,
            inputs=[answer_input, session_state_var],
            outputs=[
                answer_input, evaluation_status, eval_strengths, eval_gaps, eval_missed,
                eval_followup, eval_overall, eval_outcome, coverage_display, session_state_var
            ]
        ).then(
            fn=update_progress,
            inputs=[session_state_var],
            outputs=[progress_display]
        )
        
        teach_full_btn.click(
            fn=lambda s: teach_explanation("full", s),
            inputs=[session_state_var],
            outputs=[teaching_display]
        )
        
        teach_ideal_btn.click(
            fn=lambda s: teach_explanation("ideal_answer", s),
            inputs=[session_state_var],
            outputs=[teaching_display]
        )
        
        teach_why_weak_btn.click(
            fn=lambda s: teach_explanation("why_weak", s),
            inputs=[session_state_var],
            outputs=[teaching_display]
        )
        
        teach_missed_btn.click(
            fn=lambda s: teach_explanation("missed_concepts", s),
            inputs=[session_state_var],
            outputs=[teaching_display]
        )
        
        next_question_btn.click(
            fn=next_question,
            inputs=[session_state_var],
            outputs=[question_display, requirement_tag, difficulty_tag, answer_input, evaluation_status, session_state_var]
        ).then(
            fn=update_coverage,
            inputs=[session_state_var],
            outputs=[coverage_display]
        ).then(
            fn=update_progress,
            inputs=[session_state_var],
            outputs=[progress_display]
        )
        
        end_session_btn.click(
            fn=end_session,
            inputs=[session_state_var],
            outputs=[session_summary_display, summary_accordion, summary_data_var]
        )
        
        export_json_btn.click(
            fn=export_summary_json,
            inputs=[summary_data_var],
            outputs=[session_summary_display]
        )
        
        export_markdown_btn.click(
            fn=export_summary_markdown,
            inputs=[summary_data_var],
            outputs=[session_summary_display]
        )


def get_available_evaluation_runs() -> List[Tuple[str, str]]:
    """
    Get list of available evaluation runs from evaluation/runs/ directory.
    
    Returns:
        List of (display_name, filepath) tuples for dropdown
    """
    runs_dir = PROJECT_ROOT / "evaluation" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    runs = []
    for json_file in sorted(runs_dir.glob("run_*.json"), reverse=True):
        # Extract run_id from filename
        run_id = json_file.stem
        # Format display name: run_20250123_143022 -> 2025-01-23 14:30:22
        try:
            parts = run_id.split("_")
            if len(parts) >= 3:
                date_part = parts[1]
                time_part = parts[2]
                display = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            else:
                display = run_id
        except:
            display = run_id
        
        runs.append((display, str(json_file)))
    
    return runs if runs else [("No runs available", "")]


def load_and_analyze_run(run_filepath: str) -> Tuple[str, str, str, str, str]:
    """
    Load an evaluation run and generate all analysis displays.
    
    Returns:
        Tuple of (metrics_summary, weakest_requirements, chunk_type_analysis, 
                 mismatch_report, export_content)
    """
    if not run_filepath or run_filepath == "":
        return (
            "**No run selected.**",
            "**No run selected.**",
            "**No run selected.**",
            "**No run selected.**",
            ""
        )
    
    try:
        run = load_evaluation_run(Path(run_filepath))
        
        # Generate metrics summary
        metrics_summary = f"""
## Overall Metrics

- **Average Concept MRR:** {run.avg_concept_mrr:.3f}
- **Average nDCG@10:** {run.avg_ndcg_at_10:.3f}
- **Average Recall@10:** {run.avg_recall_at_10:.3f}
- **Average Concept Coverage:** {run.avg_concept_coverage:.3f}
- **Average Answer Confidence:** {run.avg_confidence_score:.2f}/5

**Run Info:**
- Run ID: `{run.run_id}`
- Timestamp: {run.timestamp}
- Test Set: {run.test_set_name}
- Total Test Cases: {run.total_test_cases}
"""
        
        # Generate weakest requirements table
        ranking = rank_weakest_requirements(run)
        if ranking.weakest_requirements:
            req_lines = [
                "| Rank | Requirement ID | Tests | Coverage | MRR | Confidence | Weakness Score |",
                "|------|----------------|-------|----------|-----|------------|----------------|"
            ]
            for i, weakness in enumerate(ranking.weakest_requirements[:10], 1):
                req_lines.append(
                    f"| {i} | `{weakness.requirement_id}` | {weakness.test_count} | "
                    f"{weakness.avg_concept_coverage:.3f} | {weakness.avg_retrieval_mrr:.3f} | "
                    f"{weakness.avg_answer_confidence:.2f} | {weakness.weakness_score:.3f} |"
                )
            weakest_requirements = "\n".join(req_lines)
        else:
            weakest_requirements = "**No requirements with sufficient test coverage.**"
        
        # Generate chunk type analysis
        chunk_analysis = analyze_chunk_type_usage(run)
        chunk_lines = [
            "| Chunk Type | Expected | Actual | Ratio | Status |",
            "|------------|----------|--------|-------|--------|"
        ]
        for usage in chunk_analysis.chunk_type_usages:
            status = "⚠️ OVER-USED" if usage.over_used else ("⚠️ UNDER-USED" if usage.under_used else "✓ Balanced")
            chunk_lines.append(
                f"| `{usage.chunk_type}` | {usage.expected_count} | {usage.actual_count} | "
                f"{usage.usage_ratio:.2f} | {status} |"
            )
        chunk_lines.append("")
        chunk_lines.append("### Recommendations")
        for rec in chunk_analysis.recommendations:
            chunk_lines.append(f"- {rec}")
        chunk_type_analysis = "\n".join(chunk_lines)
        
        # Generate mismatch report
        mismatch_report_data = find_retrieval_answer_mismatches(run)
        if mismatch_report_data.mismatches:
            mismatch_lines = [
                f"**Found {mismatch_report_data.mismatch_count} mismatches** (out of {mismatch_report_data.total_tests} tests)",
                f"Average mismatch score: {mismatch_report_data.avg_mismatch_score:.3f}",
                "",
                "| Test ID | Question | Retrieval MRR | Coverage | Answer Confidence | Mismatch Score |",
                "|---------|----------|---------------|----------|-------------------|----------------|"
            ]
            for mismatch in mismatch_report_data.mismatches[:10]:
                question_short = mismatch.question[:60] + "..." if len(mismatch.question) > 60 else mismatch.question
                mismatch_lines.append(
                    f"| `{mismatch.test_id}` | {question_short} | {mismatch.retrieval_mrr:.3f} | "
                    f"{mismatch.retrieval_concept_coverage:.3f} | {mismatch.answer_confidence_score}/5 | "
                    f"{mismatch.mismatch_score:.3f} |"
                )
            mismatch_report = "\n".join(mismatch_lines)
        else:
            mismatch_report = "**No significant mismatches detected.**"
        
        # Generate export content (full analysis summary)
        export_content = generate_analysis_summary(run)
        
        return (
            metrics_summary,
            weakest_requirements,
            chunk_type_analysis,
            mismatch_report,
            export_content
        )
    except Exception as e:
        error_msg = f"**Error loading run:** {str(e)}"
        return (error_msg, error_msg, error_msg, error_msg, "")


def compare_runs(baseline_filepath: str, current_filepath: str) -> str:
    """
    Compare two evaluation runs and return regression report.
    
    Returns:
        Markdown-formatted comparison report
    """
    if not baseline_filepath or not current_filepath or baseline_filepath == "" or current_filepath == "":
        return "**Please select both baseline and current runs.**"
    
    if baseline_filepath == current_filepath:
        return "**Baseline and current runs must be different.**"
    
    try:
        baseline_run = load_evaluation_run(Path(baseline_filepath))
        current_run = load_evaluation_run(Path(current_filepath))
        
        regression = compare_evaluation_runs(baseline_run, current_run)
        
        lines = [
            f"## Regression Analysis",
            "",
            f"**Baseline:** {regression.baseline_run_id}",
            f"**Current:** {regression.current_run_id}",
            "",
            f"### {regression.overall_assessment}",
            "",
            f"- Regressions: {regression.regression_count}",
            f"- Improvements: {regression.improvement_count}",
            f"- Stable: {regression.stable_count}",
            "",
            "### Metric Changes",
            "",
            "| Metric | Baseline | Current | Change | % Change | Status |",
            "|--------|----------|---------|--------|----------|--------|"
        ]
        
        for metric in regression.metric_changes:
            status = "📉 Regression" if metric.is_regression else ("📈 Improvement" if metric.is_improvement else "➡️ Stable")
            lines.append(
                f"| {metric.metric_name} | {metric.baseline_value:.3f} | {metric.current_value:.3f} | "
                f"{metric.absolute_change:+.3f} | {metric.relative_change:+.1f}% | {status} |"
            )
        
        if regression.requirement_changes:
            lines.extend([
                "",
                "### Requirement Changes",
                "",
                "| Requirement ID | Baseline Weakness | Current Weakness | Change | % Change | Status |",
                "|----------------|-------------------|------------------|--------|----------|--------|"
            ])
            
            for req_id, change in list(regression.requirement_changes.items())[:10]:
                status = "📉 Regression" if change.is_regression else ("📈 Improvement" if change.is_improvement else "➡️ Stable")
                lines.append(
                    f"| `{req_id}` | {change.baseline_value:.3f} | {change.current_value:.3f} | "
                    f"{change.absolute_change:+.3f} | {change.relative_change:+.1f}% | {status} |"
                )
        
        return "\n".join(lines)
    except Exception as e:
        return f"**Error comparing runs:** {str(e)}"


def create_rag_evaluation_ui():
    """Create the RAG Evaluation Dashboard UI tab."""
    
    with gr.Column():
        gr.Markdown("""
        ## RAG Evaluation Dashboard
        
        View and analyze completed evaluation runs. All data is read-only and comes from existing evaluation runs.
        """)
        
        # Evaluation Run Selector
        with gr.Accordion("Select Evaluation Run", open=True):
            run_choices = get_available_evaluation_runs()
            # Set default value only if we have valid choices
            default_value = run_choices[0][1] if run_choices and run_choices[0][1] and run_choices[0][1] != "" else None
            run_dropdown = gr.Dropdown(
                choices=run_choices,
                value=default_value,
                label="Evaluation Run",
                interactive=True,
                info="Select an evaluation run to analyze"
            )
            load_run_btn = gr.Button("Load Run", variant="primary")
        
        # High-Level Metric Summary
        with gr.Accordion("Overall Metrics", open=True):
            metrics_display = gr.Markdown(
                value="**Select and load an evaluation run to view metrics.**",
                label="Metrics Summary"
            )
        
        # Weakest Requirements
        with gr.Accordion("Weakest Requirements", open=False):
            weakest_requirements_display = gr.Markdown(
                value="**No data loaded.**",
                label="Requirement Weakness Ranking"
            )
        
        # Chunk Type Usage Analysis
        with gr.Accordion("Chunk Type Usage Analysis", open=False):
            chunk_type_display = gr.Markdown(
                value="**No data loaded.**",
                label="Chunk Type Distribution"
            )
        
        # Retrieval-Answer Mismatches
        with gr.Accordion("Retrieval-Answer Mismatches", open=False):
            mismatch_display = gr.Markdown(
                value="**No data loaded.**",
                label="Mismatch Analysis"
            )
        
        # Regression Comparison
        with gr.Accordion("Regression Comparison", open=False):
            gr.Markdown("Compare two evaluation runs to detect regressions and improvements.")
            
            with gr.Row():
                baseline_dropdown = gr.Dropdown(
                    choices=run_choices,
                    value=None,
                    label="Baseline Run",
                    interactive=True
                )
                current_dropdown = gr.Dropdown(
                    choices=run_choices,
                    value=None,
                    label="Current Run",
                    interactive=True
                )
            
            compare_btn = gr.Button("Compare Runs", variant="secondary")
            comparison_display = gr.Markdown(
                value="**Select baseline and current runs, then click Compare Runs.**",
                label="Comparison Results"
            )
        
        # Export Analysis Report
        with gr.Accordion("Export Analysis Report", open=False):
            export_display = gr.Markdown(
                value="**Load a run to generate export content.**",
                label="Export Preview"
            )
        
        # Wire up event handlers
        load_run_btn.click(
            fn=load_and_analyze_run,
            inputs=[run_dropdown],
            outputs=[
                metrics_display,
                weakest_requirements_display,
                chunk_type_display,
                mismatch_display,
                export_display
            ]
        )
        
        compare_btn.click(
            fn=compare_runs,
            inputs=[baseline_dropdown, current_dropdown],
            outputs=[comparison_display]
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
        
        # Create tabs
        with gr.Tabs() as tabs:
            # Q&A Tab (existing functionality)
            with gr.Tab("Q&A Mode"):
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
            
            # Interview Simulator Tab
            with gr.Tab("Interview Simulator"):
                create_interview_simulator_ui()
            
            # RAG Evaluation Tab
            with gr.Tab("RAG Evaluation"):
                create_rag_evaluation_ui()
    
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
