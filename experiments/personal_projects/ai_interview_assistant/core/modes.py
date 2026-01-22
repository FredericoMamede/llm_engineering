"""
Interview modes and system orchestration.

This module composes retrieval and answer generation into distinct,
interview-focused behaviors without duplicating core logic.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion

try:
    from .retriever import KnowledgeRetriever, RetrievalResult
    from .answer_generator import AnswerGenerator, GeneratedAnswer
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.retriever import KnowledgeRetriever, RetrievalResult
    from core.answer_generator import AnswerGenerator, GeneratedAnswer

load_dotenv(override=True)

FOLLOWUP_MODEL = "openai/gpt-4o-mini"


class InterviewMode(str, Enum):
    """Available interview modes."""
    EXPLAIN = "explain"
    INTERVIEWER = "interviewer"
    EVALUATION = "evaluation"
    COMPANY_AWARE = "company_aware"
    SYSTEM_DESIGN = "system_design"
    RAPID_FIRE = "rapid_fire"


@dataclass
class ModeConfig:
    """Configuration for an interview mode."""
    mode: InterviewMode
    name: str
    description: str
    
    # Retrieval parameters
    top_k_original: int = 10
    top_k_rewritten: int = 10
    final_k: int = 10
    enable_query_rewrite: bool = True
    
    # Filter preferences (applied as bias, not strict filter)
    prefer_chunk_types: Optional[List[str]] = None
    prefer_requirement_id: Optional[str] = None
    prefer_company_domain: Optional[str] = None
    
    # Answer generation parameters
    min_chunks: int = 1
    min_similarity: float = 0.2
    max_answer_length: Optional[int] = None  # None = no limit
    
    # Mode-specific behavior flags
    ask_followup: bool = False
    evaluate_candidate: bool = False
    emphasize_tradeoffs: bool = False
    emphasize_clarity: bool = False
    company_context: Optional[str] = None


class ModeOrchestrator:
    """Orchestrates retrieval and answer generation based on interview mode."""
    
    def __init__(
        self,
        vector_db_dir: Path,
        backend: str = "local",
        answer_model: str = "openai/gpt-4o-mini"
    ):
        """
        Initialize orchestrator.
        
        Args:
            vector_db_dir: Directory containing vector database
            backend: Vector store backend
            answer_model: Model for answer generation
        """
        self.vector_db_dir = vector_db_dir
        self.backend = backend
        self.answer_model = answer_model
        
        # Initialize components (will be created per-mode with different configs)
        self._base_retriever = None
        self._base_generator = None
    
    def _get_mode_config(self, mode: InterviewMode) -> ModeConfig:
        """Get configuration for a specific mode."""
        configs = {
            InterviewMode.EXPLAIN: ModeConfig(
                mode=InterviewMode.EXPLAIN,
                name="Explain Mode",
                description="Explain concepts clearly and concisely",
                top_k_original=15,
                top_k_rewritten=15,
                final_k=12,
                enable_query_rewrite=True,
                emphasize_clarity=True,
                min_chunks=2,
                min_similarity=0.2
            ),
            
            InterviewMode.INTERVIEWER: ModeConfig(
                mode=InterviewMode.INTERVIEWER,
                name="Interviewer Mode",
                description="Simulate a senior interviewer with follow-up questions",
                top_k_original=10,
                top_k_rewritten=10,
                final_k=8,
                enable_query_rewrite=True,
                ask_followup=True,
                min_chunks=1,
                min_similarity=0.25,
                max_answer_length=300  # Shorter, sharper answers
            ),
            
            InterviewMode.EVALUATION: ModeConfig(
                mode=InterviewMode.EVALUATION,
                name="Evaluation Mode",
                description="Evaluate candidate answers",
                top_k_original=12,
                top_k_rewritten=12,
                final_k=10,
                enable_query_rewrite=True,
                evaluate_candidate=True,
                min_chunks=2,
                min_similarity=0.2
            ),
            
            InterviewMode.COMPANY_AWARE: ModeConfig(
                mode=InterviewMode.COMPANY_AWARE,
                name="Company-Aware Mode (Eventyr)",
                description="Frame answers in Eventyr's context and constraints",
                top_k_original=12,
                top_k_rewritten=12,
                final_k=10,
                enable_query_rewrite=True,
                prefer_company_domain="domain_1",  # Eventyr domain
                company_context="Eventyr is an AI-first startup building an autonomous recruiting platform. The team is small (2-3 engineers), works with sub-5-minute response time constraints, and handles hundreds of parallel conversations.",
                min_chunks=1,
                min_similarity=0.2
            ),
            
            InterviewMode.SYSTEM_DESIGN: ModeConfig(
                mode=InterviewMode.SYSTEM_DESIGN,
                name="System Design Mode",
                description="Answer system design questions with emphasis on tradeoffs",
                top_k_original=15,
                top_k_rewritten=15,
                final_k=12,
                enable_query_rewrite=True,
                prefer_chunk_types=["tradeoff", "failure_mode"],
                emphasize_tradeoffs=True,
                min_chunks=2,
                min_similarity=0.2
            ),
            
            InterviewMode.RAPID_FIRE: ModeConfig(
                mode=InterviewMode.RAPID_FIRE,
                name="Rapid Fire Mode",
                description="Short, precise answers (3-5 sentences max)",
                top_k_original=8,
                top_k_rewritten=8,
                final_k=5,
                enable_query_rewrite=False,  # Skip rewriting for speed
                min_chunks=1,
                min_similarity=0.3,  # Higher threshold for precision
                max_answer_length=150  # Very short
            )
        }
        
        return configs.get(mode, configs[InterviewMode.EXPLAIN])
    
    def _apply_mode_filters(
        self,
        config: ModeConfig,
        base_filter: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Apply mode-specific filter preferences.
        
        Returns a filter dict that can be used by the retriever.
        The vector store will apply these as strict filters.
        """
        filter_dict = base_filter.copy() if base_filter else {}
        
        # Apply strict filters if specified
        if config.prefer_requirement_id:
            filter_dict['requirement_id'] = config.prefer_requirement_id
        
        if config.prefer_company_domain:
            filter_dict['company_domain'] = config.prefer_company_domain
        
        # Note: prefer_chunk_types is handled via prompt instructions
        # since we want to bias toward but not strictly require them
        
        return filter_dict if filter_dict else None
    
    def _create_mode_prompt_addition(self, config: ModeConfig) -> str:
        """Create additional prompt instructions based on mode."""
        additions = []
        
        if config.prefer_chunk_types:
            types_str = ", ".join(config.prefer_chunk_types)
            additions.append(
                f"Prioritize information from chunks with types: {types_str}. "
                "If such chunks are available, give them more weight in your answer."
            )
        
        if config.emphasize_clarity:
            additions.append(
                "Focus on clarity and structure. Break down complex concepts into "
                "clear, logical sections. Use examples from the context when available."
            )
        
        if config.emphasize_tradeoffs:
            additions.append(
                "Emphasize tradeoffs, constraints, and decision criteria. "
                "Highlight failure modes and edge cases mentioned in the context."
            )
        
        if config.company_context:
            additions.append(
                f"Frame your answer in the context of: {config.company_context}. "
                "Reference specific constraints and tradeoffs relevant to this context."
            )
        
        if config.max_answer_length:
            additions.append(
                f"Keep your answer concise - maximum {config.max_answer_length} words. "
                "Be direct and precise."
            )
        
        if config.mode == InterviewMode.RAPID_FIRE:
            additions.append(
                "This is Rapid Fire Mode. Provide a very short answer (3-5 sentences). "
                "If you cannot answer confidently from the context, refuse immediately."
            )
        
        return "\n".join(additions) if additions else ""
    
    def _generate_followup_question(
        self,
        original_query: str,
        answer: GeneratedAnswer,
        retrieval_result: RetrievalResult
    ) -> Optional[str]:
        """Generate a follow-up question for Interviewer Mode."""
        if not answer.answer_text or answer.refusal_reason:
            return None
        
        prompt = f"""You are a senior technical interviewer conducting a technical interview.

The candidate was asked: "{original_query}"

The candidate's answer (based on retrieved knowledge):
{answer.answer_text[:500]}

Generate a single, sharp follow-up question that:
1. Probes deeper into the topic
2. Tests understanding of tradeoffs or edge cases
3. Is appropriate for a senior engineer interview
4. Can be answered from the available knowledge base

Keep it concise (one sentence). Do not ask about topics not covered in the knowledge base.

Follow-up question:"""

        try:
            response = completion(
                model=FOLLOWUP_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            followup = response.choices[0].message.content.strip()
            # Remove quotes if present
            followup = followup.strip('"\'')
            return followup if followup else None
        except Exception:
            return None
    
    def _evaluate_candidate_answer(
        self,
        candidate_response: str,
        question: str,
        retrieval_result: RetrievalResult
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer against retrieved context."""
        context_summary = "\n".join([
            f"- {chunk.headline}: {chunk.summary}"
            for chunk in retrieval_result.retrieved_chunks[:5]
        ])
        
        prompt = f"""You are evaluating a candidate's answer in a technical interview.

QUESTION:
{question}

EXPECTED KNOWLEDGE AREAS (from knowledge base):
{context_summary}

CANDIDATE'S ANSWER:
{candidate_response}

Evaluate the candidate's answer and provide:
1. Strengths: What did they get right?
2. Gaps: What important concepts did they miss?
3. Missed Concepts: List specific concepts from the knowledge base that weren't mentioned
4. Follow-up Questions: Suggest 2-3 questions to probe deeper

Be constructive and specific. Reference the knowledge base context when identifying gaps.

Evaluation:"""

        try:
            response = completion(
                model=self.answer_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0
            )
            evaluation_text = response.choices[0].message.content.strip()
            
            # Parse evaluation (simple extraction)
            return {
                "evaluation_text": evaluation_text,
                "strengths": self._extract_section(evaluation_text, "Strengths"),
                "gaps": self._extract_section(evaluation_text, "Gaps"),
                "missed_concepts": self._extract_section(evaluation_text, "Missed Concepts"),
                "followup_questions": self._extract_section(evaluation_text, "Follow-up Questions")
            }
        except Exception as e:
            return {
                "evaluation_text": f"Error generating evaluation: {e}",
                "strengths": [],
                "gaps": [],
                "missed_concepts": [],
                "followup_questions": []
            }
    
    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """Extract a section from evaluation text."""
        # Simple extraction - look for section headers
        lines = text.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            if section_name.lower() in line.lower() and ':' in line:
                in_section = True
                continue
            if in_section:
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    items.append(line.strip().lstrip('-•').strip())
                elif line.strip() and not line.strip().startswith(('1.', '2.', '3.', '4.')):
                    # Check if we've moved to next section
                    if any(keyword in line.lower() for keyword in ['strengths', 'gaps', 'missed', 'follow']):
                        break
                    if line.strip():
                        items.append(line.strip())
        
        return items if items else [f"See evaluation text for {section_name}"]
    
    def process(
        self,
        query: str,
        mode: InterviewMode,
        candidate_response: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Process a query in a specific interview mode.
        
        Args:
            query: User query
            mode: Interview mode to use
            candidate_response: Optional candidate answer (for Evaluation Mode)
            debug: Enable debug output
        
        Returns:
            Dictionary with answer, metadata, and mode-specific outputs
        """
        config = self._get_mode_config(mode)
        
        if debug:
            print(f"🎯 Mode: {config.name}")
            print(f"   {config.description}")
        
        # Create retriever with mode-specific config
        retriever = KnowledgeRetriever(
            vector_db_dir=self.vector_db_dir,
            backend=self.backend,
            enable_query_rewrite=config.enable_query_rewrite,
            top_k_original=config.top_k_original,
            top_k_rewritten=config.top_k_rewritten,
            final_k=config.final_k
        )
        
        # Apply filters if specified
        filter_dict = self._apply_mode_filters(config)
        
        # Retrieve context
        retrieval_result = retriever.retrieve(query, filter_dict=filter_dict, debug=debug)
        
        # Handle Evaluation Mode differently
        if mode == InterviewMode.EVALUATION and candidate_response:
            evaluation = self._evaluate_candidate_answer(
                candidate_response,
                query,
                retrieval_result
            )
            return {
                "mode": mode.value,
                "mode_name": config.name,
                "query": query,
                "retrieval_result": retrieval_result,
                "evaluation": evaluation,
                "answer": None  # No answer generated in evaluation mode
            }
        
        # Create answer generator
        generator = AnswerGenerator(model=self.answer_model, temperature=0)
        
        # Get mode-specific prompt instructions
        mode_instructions = self._create_mode_prompt_addition(config)
        
        # Generate answer with mode-specific instructions
        answer = generator.generate(
            retrieval_result,
            min_chunks=config.min_chunks,
            min_similarity=config.min_similarity,
            mode_instructions=mode_instructions if mode_instructions else None
        )
        
        # Apply mode-specific post-processing
        if config.max_answer_length and answer.answer_text:
            words = answer.answer_text.split()
            if len(words) > config.max_answer_length:
                # Truncate to max length (rough approximation)
                truncated = ' '.join(words[:config.max_answer_length])
                answer.answer_text = truncated + "..."
                answer.confidence_level = "medium"  # Lower confidence for truncated
        
        # Generate follow-up question if in Interviewer Mode
        followup_question = None
        if config.ask_followup and not answer.refusal_reason:
            followup_question = self._generate_followup_question(
                query,
                answer,
                retrieval_result
            )
        
        # Build result
        result = {
            "mode": mode.value,
            "mode_name": config.name,
            "query": query,
            "retrieval_result": retrieval_result,
            "answer": answer,
            "followup_question": followup_question,
            "mode_config": {
                "top_k_original": config.top_k_original,
                "top_k_rewritten": config.top_k_rewritten,
                "final_k": config.final_k,
                "filters_applied": filter_dict or {}
            }
        }
        
        return result


def main():
    """Test the orchestrator with different modes."""
    project_root = Path(__file__).parent.parent
    vector_db_dir = project_root / "data" / "vector_db"
    
    orchestrator = ModeOrchestrator(vector_db_dir=vector_db_dir, backend="local")
    
    # Test Explain Mode
    print("=" * 80)
    print("TESTING EXPLAIN MODE")
    print("=" * 80)
    result = orchestrator.process(
        "What is TypeScript and why is it useful?",
        InterviewMode.EXPLAIN,
        debug=True
    )
    if result["answer"]:
        print(f"\nAnswer: {result['answer'].answer_text[:200]}...")
        print(f"Confidence: {result['answer'].confidence_level.value}")
    
    # Test Rapid Fire Mode
    print("\n" + "=" * 80)
    print("TESTING RAPID FIRE MODE")
    print("=" * 80)
    result = orchestrator.process(
        "What is React?",
        InterviewMode.RAPID_FIRE,
        debug=True
    )
    if result["answer"]:
        print(f"\nAnswer: {result['answer'].answer_text}")
        print(f"Length: {len(result['answer'].answer_text.split())} words")


if __name__ == "__main__":
    main()
