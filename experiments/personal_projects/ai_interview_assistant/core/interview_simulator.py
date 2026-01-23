"""
Interview Simulator: Adaptive, strict-first interview mode.

This module implements an autonomous interview simulator that asks questions,
evaluates answers, and teaches only on demand. All questions and explanations
are grounded in the RAG corpus.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv
from litellm import completion

try:
    from .retriever import KnowledgeRetriever, RetrievalResult, RetrievedChunk
    from .answer_generator import AnswerGenerator, GeneratedAnswer
    from evaluation.judge import AnswerJudge, EvaluationFeedback
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.retriever import KnowledgeRetriever, RetrievalResult, RetrievedChunk
    from core.answer_generator import AnswerGenerator, GeneratedAnswer
    from evaluation.judge import AnswerJudge, EvaluationFeedback

# Import WeaknessTracker separately to handle circular import
try:
    from ui.weakness_tracker import WeaknessTracker
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from ui.weakness_tracker import WeaknessTracker

load_dotenv(override=True)

QUESTION_MODEL = "openai/gpt-4o-mini"
TEACHING_MODEL = "openai/gpt-4o-mini"


class QuestionIntent(str, Enum):
    """Intent types for interview questions."""
    CONCEPT = "concept"
    TRADEOFF = "tradeoff"
    FAILURE_MODE = "failure_mode"
    SYSTEM_DESIGN = "system_design"


class Difficulty(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Outcome(str, Enum):
    """Evaluation outcome."""
    CORRECT = "correct"
    PARTIAL = "partial"
    INCORRECT = "incorrect"


@dataclass
class InterviewQuestion:
    """A generated interview question with metadata."""
    question_id: str
    question_text: str
    requirement_id: Optional[str] = None
    company_domain: Optional[str] = None
    intent: QuestionIntent = QuestionIntent.CONCEPT
    difficulty: Difficulty = Difficulty.MEDIUM
    source_chunks: List[str] = field(default_factory=list)  # chunk_ids
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QuestionAnswer:
    """User's answer to a question."""
    question_id: str
    answer_text: str
    answered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QuestionEvaluation:
    """Evaluation of a user's answer."""
    question_id: str
    evaluation: EvaluationFeedback
    outcome: Outcome
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionState:
    """State of an interview session."""
    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    
    # Configuration
    company: str = "Eventyr"
    requirement_set: str = "ai-first-mern-fullstack"
    difficulty_target: Difficulty = Difficulty.MEDIUM
    focus_areas: List[str] = field(default_factory=list)
    session_length: Optional[int] = None  # max questions
    
    # Progress
    questions_asked: List[InterviewQuestion] = field(default_factory=list)
    answers_given: List[QuestionAnswer] = field(default_factory=list)
    evaluations: List[QuestionEvaluation] = field(default_factory=list)
    
    # Tracking
    current_question: Optional[InterviewQuestion] = None
    current_answer: Optional[QuestionAnswer] = None
    current_evaluation: Optional[QuestionEvaluation] = None
    
    # Difficulty progression
    current_difficulty: Difficulty = Difficulty.MEDIUM
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    
    # Topics covered
    covered_requirements: Set[str] = field(default_factory=set)
    covered_domains: Set[str] = field(default_factory=set)
    
    # Weaknesses triggered
    weaknesses_triggered: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "company": self.company,
            "requirement_set": self.requirement_set,
            "difficulty_target": self.difficulty_target.value,
            "focus_areas": self.focus_areas,
            "session_length": self.session_length,
            "questions_asked": [
                {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "requirement_id": q.requirement_id,
                    "company_domain": q.company_domain,
                    "intent": q.intent.value,
                    "difficulty": q.difficulty.value,
                    "source_chunks": q.source_chunks,
                    "generated_at": q.generated_at
                }
                for q in self.questions_asked
            ],
            "answers_given": [
                {
                    "question_id": a.question_id,
                    "answer_text": a.answer_text,
                    "answered_at": a.answered_at
                }
                for a in self.answers_given
            ],
            "evaluations": [
                {
                    "question_id": e.question_id,
                    "outcome": e.outcome.value,
                    "confidence_score": e.evaluation.confidence_score,
                    "evaluated_at": e.evaluated_at
                }
                for e in self.evaluations
            ],
            "current_question": {
                "question_id": self.current_question.question_id,
                "question_text": self.current_question.question_text
            } if self.current_question else None,
            "current_difficulty": self.current_difficulty.value,
            "consecutive_correct": self.consecutive_correct,
            "consecutive_incorrect": self.consecutive_incorrect,
            "covered_requirements": list(self.covered_requirements),
            "covered_domains": list(self.covered_domains),
            "weaknesses_triggered": self.weaknesses_triggered
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Create from dictionary."""
        state = cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            ended_at=data.get("ended_at"),
            company=data.get("company", "Eventyr"),
            requirement_set=data.get("requirement_set", "ai-first-mern-fullstack"),
            difficulty_target=Difficulty(data.get("difficulty_target", "medium")),
            focus_areas=data.get("focus_areas", []),
            session_length=data.get("session_length"),
            current_difficulty=Difficulty(data.get("current_difficulty", "medium")),
            consecutive_correct=data.get("consecutive_correct", 0),
            consecutive_incorrect=data.get("consecutive_incorrect", 0),
            covered_requirements=set(data.get("covered_requirements", [])),
            covered_domains=set(data.get("covered_domains", [])),
            weaknesses_triggered=data.get("weaknesses_triggered", [])
        )
        
        # Reconstruct questions, answers, evaluations (simplified)
        # Full reconstruction would require full data, but we'll keep it minimal for now
        
        return state


class InterviewSimulator:
    """Autonomous interview simulator with adaptive difficulty."""
    
    def __init__(
        self,
        vector_db_dir: Path,
        backend: str = "local",
        question_model: str = QUESTION_MODEL,
        teaching_model: str = TEACHING_MODEL
    ):
        """
        Initialize interview simulator.
        
        Args:
            vector_db_dir: Directory containing vector database
            backend: Vector store backend
            question_model: Model for question generation
            teaching_model: Model for teaching explanations
        """
        self.vector_db_dir = vector_db_dir
        self.backend = backend
        self.question_model = question_model
        self.teaching_model = teaching_model
        
        # Initialize components
        self.retriever = KnowledgeRetriever(vector_db_dir=vector_db_dir, backend=backend)
        self.answer_generator = AnswerGenerator()
        self.judge = AnswerJudge()
        self.weakness_tracker = WeaknessTracker()
        
        # Session management
        self.sessions_dir = Path(__file__).parent.parent / "data" / "interview_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Active session
        self.current_session: Optional[SessionState] = None
    
    def start_session(
        self,
        company: str = "Eventyr",
        requirement_set: str = "ai-first-mern-fullstack",
        difficulty_target: Difficulty = Difficulty.MEDIUM,
        focus_areas: Optional[List[str]] = None,
        session_length: Optional[int] = None
    ) -> SessionState:
        """
        Start a new interview session.
        
        Args:
            company: Company name
            requirement_set: Requirement set identifier
            difficulty_target: Target difficulty level
            focus_areas: Optional list of focus areas
            session_length: Optional maximum number of questions
        
        Returns:
            SessionState for the new session
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = SessionState(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            company=company,
            requirement_set=requirement_set,
            difficulty_target=difficulty_target,
            focus_areas=focus_areas or [],
            session_length=session_length,
            current_difficulty=difficulty_target
        )
        
        self._save_session()
        return self.current_session
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """
        End the current session and generate summary.
        
        Returns:
            Session summary dictionary
        """
        if not self.current_session:
            return None
        
        self.current_session.ended_at = datetime.now().isoformat()
        summary = self._generate_session_summary()
        self._save_session()
        
        # Clear current session
        self.current_session = None
        
        return summary
    
    def generate_question(
        self,
        consider_weaknesses: bool = True,
        consider_history: bool = True
    ) -> Optional[InterviewQuestion]:
        """
        Generate the next interview question.
        
        Args:
            consider_weaknesses: Whether to prioritize tracked weaknesses
            consider_history: Whether to avoid recently asked topics
        
        Returns:
            InterviewQuestion or None if generation fails
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        # Build query for retrieval
        query_parts = []
        
        # Consider weaknesses
        if consider_weaknesses:
            weaknesses = self.weakness_tracker.get_weaknesses(min_occurrences=1)
            if weaknesses:
                # Prioritize top weaknesses
                top_weakness = weaknesses[0].concept
                query_parts.append(f"concepts related to {top_weakness}")
        
        # Consider focus areas
        if self.current_session.focus_areas:
            query_parts.append(f"topics: {', '.join(self.current_session.focus_areas)}")
        
        # Consider difficulty
        difficulty_hint = {
            Difficulty.EASY: "basic concepts and fundamentals",
            Difficulty.MEDIUM: "intermediate concepts with tradeoffs",
            Difficulty.HARD: "advanced concepts, system design, and failure modes"
        }.get(self.current_session.current_difficulty, "intermediate concepts")
        query_parts.append(difficulty_hint)
        
        # Avoid recently covered topics
        if consider_history and self.current_session.covered_requirements:
            # We'll filter in retrieval, not in query
            pass
        
        # Build final query
        if query_parts:
            base_query = " ".join(query_parts)
        else:
            base_query = "technical interview questions"
        
        # Retrieve knowledge chunks
        retrieval_result = self.retriever.retrieve(
            base_query,
            top_k_original=15,
            top_k_rewritten=15,
            final_k=10,
            enable_query_rewrite=True,
            debug=False
        )
        
        if not retrieval_result.retrieved_chunks:
            return None
        
        # Filter out recently covered chunks
        if consider_history:
            recent_chunk_ids = {
                chunk_id
                for q in self.current_session.questions_asked[-5:]  # Last 5 questions
                for chunk_id in q.source_chunks
            }
            retrieval_result.retrieved_chunks = [
                chunk for chunk in retrieval_result.retrieved_chunks
                if chunk.chunk_id not in recent_chunk_ids
            ]
        
        if not retrieval_result.retrieved_chunks:
            # If all chunks were filtered, use original set
            retrieval_result = self.retriever.retrieve(
                base_query,
                top_k_original=15,
                top_k_rewritten=15,
                final_k=10,
                enable_query_rewrite=True,
                debug=False
            )
        
        # Generate question using LLM
        question = self._generate_question_from_chunks(
            retrieval_result.retrieved_chunks,
            self.current_session.current_difficulty
        )
        
        if not question:
            return None
        
        # Extract metadata from chunks
        question.requirement_id = self._extract_requirement_id(retrieval_result.retrieved_chunks)
        question.company_domain = self._extract_company_domain(retrieval_result.retrieved_chunks)
        question.source_chunks = [chunk.chunk_id for chunk in retrieval_result.retrieved_chunks[:5]]
        
        # Update session
        self.current_session.current_question = question
        self.current_session.questions_asked.append(question)
        if question.requirement_id:
            self.current_session.covered_requirements.add(question.requirement_id)
        if question.company_domain:
            self.current_session.covered_domains.add(question.company_domain)
        
        self._save_session()
        return question
    
    def _generate_question_from_chunks(
        self,
        chunks: List[RetrievedChunk],
        difficulty: Difficulty
    ) -> Optional[InterviewQuestion]:
        """Generate interview question from retrieved chunks."""
        # Format chunks for prompt
        chunks_text = []
        for i, chunk in enumerate(chunks[:5], 1):  # Use top 5 chunks
            chunks_text.append(f"""
Chunk {i} (ID: {chunk.chunk_id}):
Type: {chunk.chunk_type}
Headline: {chunk.headline}
Summary: {chunk.summary}
Original Text: {chunk.original_text[:500]}...
Source: {chunk.inherited_metadata.get('source_url', 'N/A')}
""")
        
        chunks_context = "\n".join(chunks_text)
        
        # Determine intent based on chunk types
        chunk_types = [chunk.chunk_type for chunk in chunks[:5]]
        if "tradeoff" in chunk_types or "failure_mode" in chunk_types:
            intent = QuestionIntent.TRADEOFF
        elif "system_design" in chunk_types or "architecture" in chunk_types.lower():
            intent = QuestionIntent.SYSTEM_DESIGN
        elif "failure_mode" in chunk_types:
            intent = QuestionIntent.FAILURE_MODE
        else:
            intent = QuestionIntent.CONCEPT
        
        # Build prompt
        difficulty_instruction = {
            Difficulty.EASY: "Ask a straightforward question about basic concepts. The answer should be clear from the chunks.",
            Difficulty.MEDIUM: "Ask a question that requires understanding tradeoffs or intermediate concepts. The answer should require reasoning.",
            Difficulty.HARD: "Ask a challenging question about system design, failure modes, or advanced tradeoffs. The answer should require deep understanding."
        }.get(difficulty, "Ask an intermediate-level question.")
        
        prompt = f"""You are a technical interviewer generating interview questions.

KNOWLEDGE CHUNKS (GROUND TRUTH):
{chunks_context}

REQUIREMENTS:
1. Generate ONE interview question based ONLY on the knowledge chunks above.
2. The question must be answerable from the chunks - do NOT use external knowledge.
3. Difficulty: {difficulty.value.upper()}
4. Intent: {intent.value}
5. {difficulty_instruction}
6. The question should be appropriate for a senior engineer interview.
7. Do NOT include hints or explanations in the question.
8. Make the question specific and technical.

OUTPUT FORMAT:
QUESTION: [Your question here]

Generate the question now."""

        try:
            response = completion(
                model=self.question_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            question_text = response.choices[0].message.content.strip()
            
            # Extract question (remove "QUESTION:" prefix if present)
            if question_text.startswith("QUESTION:"):
                question_text = question_text[9:].strip()
            question_text = question_text.strip('"').strip("'").strip()
            
            if not question_text:
                return None
            
            # Create question object
            question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            return InterviewQuestion(
                question_id=question_id,
                question_text=question_text,
                intent=intent,
                difficulty=difficulty
            )
            
        except Exception as e:
            print(f"Error generating question: {e}")
            return None
    
    def submit_answer(self, answer_text: str) -> Optional[QuestionEvaluation]:
        """
        Submit user's answer and evaluate it.
        
        Args:
            answer_text: User's answer text
        
        Returns:
            QuestionEvaluation or None if no active question
        """
        if not self.current_session or not self.current_session.current_question:
            return None
        
        question = self.current_session.current_question
        
        # Store answer
        answer = QuestionAnswer(
            question_id=question.question_id,
            answer_text=answer_text
        )
        self.current_session.current_answer = answer
        self.current_session.answers_given.append(answer)
        
        # Retrieve context for evaluation
        retrieval_result = self.retriever.retrieve(
            question.question_text,
            top_k_original=10,
            top_k_rewritten=10,
            final_k=8,
            enable_query_rewrite=True,
            debug=False
        )
        
        if not retrieval_result.retrieved_chunks:
            # Fallback: use source chunks if available
            # This is a simplified fallback - in production, we'd store full chunks
            retrieval_result = self.retriever.retrieve(
                question.question_text,
                top_k_original=10,
                top_k_rewritten=10,
                final_k=8,
                enable_query_rewrite=True,
                debug=False
            )
        
        # Evaluate answer
        evaluation_feedback = self.judge.evaluate(
            question=question.question_text,
            candidate_answer=answer_text,
            retrieval_result=retrieval_result
        )
        
        # Determine outcome
        outcome = self._determine_outcome(evaluation_feedback)
        
        # Create evaluation
        evaluation = QuestionEvaluation(
            question_id=question.question_id,
            evaluation=evaluation_feedback,
            outcome=outcome
        )
        
        self.current_session.current_evaluation = evaluation
        self.current_session.evaluations.append(evaluation)
        
        # Update weakness tracker
        if evaluation_feedback.missed_concepts:
            self.weakness_tracker.record_missed_concepts(
                concepts=evaluation_feedback.missed_concepts,
                question=question.question_text,
                topic=question.requirement_id or question.company_domain
            )
            self.current_session.weaknesses_triggered.extend(evaluation_feedback.missed_concepts)
        
        # Update difficulty progression
        self._update_difficulty_progression(outcome)
        
        self._save_session()
        return evaluation
    
    def _determine_outcome(self, feedback: EvaluationFeedback) -> Outcome:
        """Determine evaluation outcome from feedback."""
        score = feedback.confidence_score
        
        if score >= 4:
            return Outcome.CORRECT
        elif score >= 3:
            return Outcome.PARTIAL
        else:
            return Outcome.INCORRECT
    
    def _update_difficulty_progression(self, outcome: Outcome):
        """Update difficulty based on outcomes."""
        if outcome == Outcome.CORRECT:
            self.current_session.consecutive_correct += 1
            self.current_session.consecutive_incorrect = 0
            
            # Escalate difficulty after 2 consecutive correct
            if self.current_session.consecutive_correct >= 2:
                if self.current_session.current_difficulty == Difficulty.EASY:
                    self.current_session.current_difficulty = Difficulty.MEDIUM
                elif self.current_session.current_difficulty == Difficulty.MEDIUM:
                    self.current_session.current_difficulty = Difficulty.HARD
        
        elif outcome == Outcome.INCORRECT:
            self.current_session.consecutive_incorrect += 1
            self.current_session.consecutive_correct = 0
            
            # Lower difficulty after 2 consecutive incorrect
            if self.current_session.consecutive_incorrect >= 2:
                if self.current_session.current_difficulty == Difficulty.HARD:
                    self.current_session.current_difficulty = Difficulty.MEDIUM
                elif self.current_session.current_difficulty == Difficulty.MEDIUM:
                    self.current_session.current_difficulty = Difficulty.EASY
        
        # PARTIAL doesn't change difficulty
    
    def teach(
        self,
        explanation_type: str = "full"
    ) -> Optional[GeneratedAnswer]:
        """
        Generate teaching explanation (on-demand only).
        
        Args:
            explanation_type: "full", "ideal_answer", "why_weak", or "missed_concepts"
        
        Returns:
            GeneratedAnswer with explanation
        """
        if not self.current_session or not self.current_session.current_question:
            return None
        
        question = self.current_session.current_question
        evaluation = self.current_session.current_evaluation
        
        # Retrieve context
        retrieval_result = self.retriever.retrieve(
            question.question_text,
            top_k_original=10,
            top_k_rewritten=10,
            final_k=8,
            enable_query_rewrite=True,
            debug=False
        )
        
        if not retrieval_result.retrieved_chunks:
            return None
        
        # Generate explanation based on type
        if explanation_type == "ideal_answer":
            # Generate ideal answer using standard generator
            answer = self.answer_generator.generate(retrieval_result)
            return answer
        
        elif explanation_type == "why_weak" and evaluation and self.current_session.current_answer:
            # Explain why the answer was weak
            answer = self._generate_why_weak_explanation(question, evaluation, retrieval_result)
            return answer
        
        elif explanation_type == "missed_concepts" and evaluation:
            # Explain missed concepts
            answer = self._generate_missed_concepts_explanation(question, evaluation, retrieval_result)
            return answer
        
        else:
            # Full explanation
            answer = self.answer_generator.generate(retrieval_result)
            return answer
    
    def _generate_why_weak_explanation(
        self,
        question: InterviewQuestion,
        evaluation: QuestionEvaluation,
        retrieval_result: RetrievalResult
    ) -> GeneratedAnswer:
        """Generate explanation of why answer was weak."""
        # Format chunks for context
        chunks_text = []
        for i, chunk in enumerate(retrieval_result.retrieved_chunks[:5], 1):
            chunks_text.append(f"""
Chunk {i}:
{chunk.headline}
{chunk.summary}
{chunk.original_text[:300]}...
""")
        
        context = "\n".join(chunks_text)
        
        candidate_answer = self.current_session.current_answer.answer_text if self.current_session.current_answer else "N/A"
        
        prompt = f"""You are explaining to a candidate why their answer was weak, based on the retrieved knowledge chunks.

QUESTION: {question.question_text}

CANDIDATE'S ANSWER:
{candidate_answer}

EVALUATION FEEDBACK:
- Gaps: {', '.join(evaluation.evaluation.gaps[:3]) if evaluation.evaluation.gaps else 'None'}
- Missed Concepts: {', '.join(evaluation.evaluation.missed_concepts[:3]) if evaluation.evaluation.missed_concepts else 'None'}

KNOWLEDGE CHUNKS (GROUND TRUTH):
{context}

Explain:
1. What the candidate got wrong or missed
2. What the correct approach should be (based on the chunks)
3. Why their answer was weak

Be constructive and specific. Reference the knowledge chunks when explaining the correct approach."""

        try:
            response = completion(
                model=self.teaching_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            explanation_text = response.choices[0].message.content.strip()
            
            # Create a GeneratedAnswer-like object
            # We'll create a minimal one for compatibility
            return GeneratedAnswer(
                answer_text=explanation_text,
                confidence_level=None,  # Not applicable for teaching
                cited_chunks=retrieval_result.retrieved_chunks[:3],  # Use top chunks
                refusal_reason=None
            )
        except Exception as e:
            return GeneratedAnswer(
                answer_text=f"Error generating explanation: {str(e)}",
                confidence_level=None,
                cited_chunks=[],
                refusal_reason=None
            )
    
    def _generate_missed_concepts_explanation(
        self,
        question: InterviewQuestion,
        evaluation: QuestionEvaluation,
        retrieval_result: RetrievalResult
    ) -> GeneratedAnswer:
        """Generate explanation of missed concepts."""
        # Format chunks for context
        chunks_text = []
        for i, chunk in enumerate(retrieval_result.retrieved_chunks[:5], 1):
            chunks_text.append(f"""
Chunk {i}:
{chunk.headline}
{chunk.summary}
{chunk.original_text[:300]}...
""")
        
        context = "\n".join(chunks_text)
        
        missed_concepts = evaluation.evaluation.missed_concepts
        if not missed_concepts:
            return GeneratedAnswer(
                answer_text="No missed concepts identified.",
                confidence_level=None,
                cited_chunks=[],
                refusal_reason=None
            )
        
        prompt = f"""You are explaining concepts that a candidate missed in their answer, based on the retrieved knowledge chunks.

QUESTION: {question.question_text}

MISSED CONCEPTS:
{chr(10).join([f"- {c}" for c in missed_concepts])}

KNOWLEDGE CHUNKS (GROUND TRUTH):
{context}

For each missed concept, provide:
1. A clear explanation of what the concept is
2. Why it's relevant to the question
3. How it relates to the knowledge chunks

Be specific and grounded in the chunks."""

        try:
            response = completion(
                model=self.teaching_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            explanation_text = response.choices[0].message.content.strip()
            
            return GeneratedAnswer(
                answer_text=explanation_text,
                confidence_level=None,
                cited_chunks=retrieval_result.retrieved_chunks[:3],
                refusal_reason=None
            )
        except Exception as e:
            return GeneratedAnswer(
                answer_text=f"Error generating explanation: {str(e)}",
                confidence_level=None,
                cited_chunks=[],
                refusal_reason=None
            )
    
    def _extract_requirement_id(self, chunks: List[RetrievedChunk]) -> Optional[str]:
        """Extract requirement_id from chunks."""
        for chunk in chunks:
            req_id = chunk.inherited_metadata.get("requirement_id")
            if req_id:
                return str(req_id)
        return None
    
    def _extract_company_domain(self, chunks: List[RetrievedChunk]) -> Optional[str]:
        """Extract company_domain from chunks."""
        for chunk in chunks:
            domain = chunk.inherited_metadata.get("company_domain")
            if domain:
                return str(domain)
        return None
    
    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate summary of completed session."""
        if not self.current_session:
            return {}
        
        session = self.current_session
        
        # Calculate statistics
        total_questions = len(session.questions_asked)
        total_answers = len(session.answers_given)
        total_evaluations = len(session.evaluations)
        
        correct_count = sum(1 for e in session.evaluations if e.outcome == Outcome.CORRECT)
        partial_count = sum(1 for e in session.evaluations if e.outcome == Outcome.PARTIAL)
        incorrect_count = sum(1 for e in session.evaluations if e.outcome == Outcome.INCORRECT)
        
        accuracy = (correct_count / total_evaluations * 100) if total_evaluations > 0 else 0
        
        # Get top weaknesses
        top_weaknesses = session.weaknesses_triggered[:10]
        
        # Get covered topics
        covered_topics = {
            "requirements": list(session.covered_requirements),
            "domains": list(session.covered_domains)
        }
        
        summary = {
            "session_id": session.session_id,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "total_questions": total_questions,
            "total_answers": total_answers,
            "total_evaluations": total_evaluations,
            "accuracy": round(accuracy, 1),
            "correct": correct_count,
            "partial": partial_count,
            "incorrect": incorrect_count,
            "final_difficulty": session.current_difficulty.value,
            "top_weaknesses": top_weaknesses,
            "covered_topics": covered_topics,
            "recommendations": self._generate_recommendations(session)
        }
        
        return summary
    
    def _generate_recommendations(self, session: SessionState) -> List[str]:
        """Generate study recommendations based on session."""
        recommendations = []
        
        # Weakness-based recommendations
        if session.weaknesses_triggered:
            top_weakness = session.weaknesses_triggered[0]
            recommendations.append(f"Focus on: {top_weakness}")
        
        # Difficulty-based recommendations
        if session.current_difficulty == Difficulty.EASY:
            recommendations.append("Consider practicing more medium-difficulty questions")
        elif session.current_difficulty == Difficulty.HARD:
            recommendations.append("You're handling hard questions well! Consider system design topics")
        
        # Coverage-based recommendations
        if len(session.covered_requirements) < 5:
            recommendations.append("Try to cover more requirement areas in your next session")
        
        return recommendations
    
    def _save_session(self):
        """Save current session to disk."""
        if not self.current_session:
            return
        
        session_file = self.sessions_dir / f"{self.current_session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_session(self, session_id: str) -> Optional[SessionState]:
        """Load a session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except Exception:
            return None
