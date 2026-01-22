"""
LLM-as-a-judge evaluation system for candidate answers.

This module evaluates candidate answers against retrieved knowledge chunks,
providing grounded, interview-relevant feedback.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re
from dotenv import load_dotenv
from litellm import completion

try:
    from core.retriever import RetrievalResult, RetrievedChunk
    from core.answer_generator import GeneratedAnswer
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.retriever import RetrievalResult, RetrievedChunk
    from core.answer_generator import GeneratedAnswer

load_dotenv(override=True)

JUDGE_MODEL = "openai/gpt-4o-mini"
TEMPERATURE = 0  # Deterministic evaluation


@dataclass
class EvaluationFeedback:
    """Structured evaluation feedback for a candidate answer."""
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    missed_concepts: List[str] = field(default_factory=list)
    followup_questions: List[str] = field(default_factory=list)
    overall_assessment: str = ""
    confidence_score: int = 3  # 1-5 scale


class AnswerJudge:
    """Evaluate candidate answers against retrieved knowledge."""
    
    def __init__(self, model: str = JUDGE_MODEL, temperature: float = TEMPERATURE):
        """
        Initialize answer judge.
        
        Args:
            model: LLM model to use for evaluation
            temperature: Temperature for evaluation (0 for deterministic)
        """
        self.model = model
        self.temperature = temperature
    
    def _format_retrieved_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format retrieved chunks as evaluation context."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"""
--- Chunk {i} (ID: {chunk.chunk_id}) ---
Type: {chunk.chunk_type}
Headline: {chunk.headline}
Summary: {chunk.summary}
Original Text: {chunk.original_text}
Source: {chunk.inherited_metadata.get('source_url', 'N/A')}
""")
        
        return "\n".join(context_parts)
    
    def _create_evaluation_prompt(
        self,
        question: str,
        candidate_answer: str,
        retrieved_chunks: List[RetrievedChunk],
        reference_answer: Optional[GeneratedAnswer] = None
    ) -> str:
        """Create prompt for answer evaluation."""
        context_text = self._format_retrieved_context(retrieved_chunks)
        num_chunks = len(retrieved_chunks)
        
        reference_section = ""
        if reference_answer and reference_answer.answer_text:
            reference_section = f"""
REFERENCE ANSWER (for context, not to compare directly):
{reference_answer.answer_text[:500]}

Note: The reference answer is provided for context only. Evaluate the candidate's answer
based on the retrieved knowledge chunks, not by comparing to the reference answer.
"""
        
        prompt = f"""You are evaluating a candidate's answer in a technical interview.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{candidate_answer}

GROUND TRUTH (Retrieved Knowledge Chunks):
{context_text}
{reference_section}

EVALUATION RULES (NON-NEGOTIABLE):
1. Evaluate ONLY against the retrieved knowledge chunks above.
2. Do NOT use external knowledge or assumptions.
3. Do NOT penalize for style or writing quality alone.
4. Focus on technical accuracy and coverage of concepts.
5. Be fair and constructive - identify what they got right.

EVALUATION DIMENSIONS:

1. ACCURACY
   - Are the candidate's claims supported by the retrieved chunks?
   - Are there any factual errors or misconceptions?
   - Are technical details correct?

2. COVERAGE
   - Which key concepts from the chunks did the candidate mention?
   - Which important concepts were missed?
   - Is the answer comprehensive relative to the available knowledge?

3. DEPTH
   - Did the candidate address tradeoffs, constraints, or decision criteria?
   - Were failure modes or edge cases mentioned?
   - Was the reasoning appropriate for a senior engineer interview?

4. FRAMING
   - Was the answer appropriate for a technical interview?
   - Did it emphasize reasoning over memorization?
   - Was it concise but substantive?

5. CONFIDENCE SIGNALS
   - Did the candidate overclaim (state things not in the chunks)?
   - Did they show appropriate uncertainty when needed?
   - Were they appropriately confident about well-supported claims?

OUTPUT FORMAT:
Provide your evaluation in the following structure:

STRENGTHS:
- [List specific things the candidate got right, grounded in chunks]
- [Be specific and reference which concepts they covered well]

GAPS:
- [List areas where the answer was incomplete or shallow]
- [Reference specific concepts from chunks that were missed]

MISSED CONCEPTS:
- [List specific concepts from the retrieved chunks that were not mentioned]
- [Be specific - name the concepts, not just general topics]

FOLLOW-UP QUESTIONS:
- [Suggest 2-3 interview-relevant follow-up questions]
- [Questions should probe deeper into concepts from the chunks]
- [Questions should be answerable from the knowledge base]

OVERALL ASSESSMENT:
[Write 2-3 sentences summarizing the candidate's performance. Be constructive and specific.
Reference the retrieved chunks when making claims about what was covered or missed.]

CONFIDENCE SCORE:
[Rate 1-5 where:
1 = Major gaps, significant inaccuracies
2 = Some gaps, minor inaccuracies
3 = Adequate coverage, mostly accurate
4 = Good coverage, accurate, some depth
5 = Excellent coverage, accurate, demonstrates deep understanding]

Provide your evaluation now."""

        return prompt
    
    def _parse_evaluation_response(self, response_text: str) -> EvaluationFeedback:
        """Parse LLM evaluation response into structured feedback."""
        import re
        feedback = EvaluationFeedback()
        
        # Normalize text
        text = response_text.strip()
        
        # Extract sections using regex patterns
        sections = {}
        
        # Pattern for section headers
        section_patterns = {
            'strengths': r'(?:^|\n)\s*STRENGTHS?\s*:?\s*\n',
            'gaps': r'(?:^|\n)\s*GAPS?\s*:?\s*\n',
            'missed_concepts': r'(?:^|\n)\s*MISSED\s+CONCEPTS?\s*:?\s*\n',
            'followup': r'(?:^|\n)\s*FOLLOW[- ]?UP\s+QUESTIONS?\s*:?\s*\n',
            'overall': r'(?:^|\n)\s*OVERALL\s+ASSESSMENT\s*:?\s*\n',
            'confidence': r'(?:^|\n)\s*CONFIDENCE\s+SCORE\s*:?\s*\n'
        }
        
        # Find all section positions
        section_positions = []
        for name, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                section_positions.append((match.end(), name))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        # Extract content for each section
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Find end position (next section or end of text)
            if i + 1 < len(section_positions):
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(text)
            
            section_text = text[start_pos:end_pos].strip()
            
            if section_name == 'strengths':
                feedback.strengths = self._extract_list_items(section_text)
            elif section_name == 'gaps':
                feedback.gaps = self._extract_list_items(section_text)
            elif section_name == 'missed_concepts':
                feedback.missed_concepts = self._extract_list_items(section_text)
            elif section_name == 'followup':
                feedback.followup_questions = self._extract_list_items(section_text)
            elif section_name == 'overall':
                feedback.overall_assessment = self._extract_paragraph(section_text)
            elif section_name == 'confidence':
                score_match = re.search(r'\b([1-5])\b', section_text)
                if score_match:
                    try:
                        feedback.confidence_score = int(score_match.group(1))
                    except ValueError:
                        pass
        
        # Fallback parsing if regex didn't work
        if not any([feedback.strengths, feedback.gaps, feedback.missed_concepts]):
            feedback = self._fallback_parse(response_text)
        
        # Ensure we have at least minimal feedback
        if not feedback.overall_assessment:
            feedback.overall_assessment = "Evaluation completed. See strengths, gaps, and missed concepts above."
        
        return feedback
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract bullet points or numbered items from text."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match bullet points (-, •, *)
            if re.match(r'^[-•*]\s+', line):
                item = re.sub(r'^[-•*]\s+', '', line).strip()
                if item:
                    items.append(item)
            # Match numbered items (1., 2., etc.)
            elif re.match(r'^\d+[.)]\s+', line):
                item = re.sub(r'^\d+[.)]\s+', '', line).strip()
                if item:
                    items.append(item)
            # Match lines that look like items (short, no periods at end)
            elif len(line) < 200 and not line.endswith('.'):
                items.append(line)
        
        return items
    
    def _extract_paragraph(self, text: str) -> str:
        """Extract paragraph text, removing list markers."""
        lines = text.split('\n')
        paragraph_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip lines that look like list items
            if re.match(r'^[-•*]\s+', line) or re.match(r'^\d+[.)]\s+', line):
                continue
            paragraph_lines.append(line)
        
        return ' '.join(paragraph_lines).strip()
    
    def _fallback_parse(self, text: str) -> EvaluationFeedback:
        """Fallback parsing using line-by-line analysis."""
        feedback = EvaluationFeedback()
        lines = text.split('\n')
        current_section = None
        current_items = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Detect section headers
            line_upper = line_stripped.upper()
            if 'STRENGTH' in line_upper and current_section != 'strengths':
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'strengths'
                current_items = []
                continue
            elif 'GAP' in line_upper and current_section != 'gaps':
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'gaps'
                current_items = []
                continue
            elif 'MISSED' in line_upper and 'CONCEPT' in line_upper:
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'missed_concepts'
                current_items = []
                continue
            elif 'FOLLOW' in line_upper and 'QUESTION' in line_upper:
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'followup'
                current_items = []
                continue
            elif 'OVERALL' in line_upper:
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'overall'
                current_items = []
                continue
            elif 'CONFIDENCE' in line_upper:
                if current_section:
                    self._finalize_section(feedback, current_section, current_items)
                current_section = 'confidence'
                continue
            
            # Collect items
            if current_section:
                if current_section == 'overall':
                    current_items.append(line_stripped)
                elif current_section == 'confidence':
                    import re
                    score_match = re.search(r'\b([1-5])\b', line_stripped)
                    if score_match:
                        try:
                            feedback.confidence_score = int(score_match.group(1))
                        except ValueError:
                            pass
                else:
                    # List item
                    item = re.sub(r'^[-•*]\s+', '', line_stripped).strip()
                    item = re.sub(r'^\d+[.)]\s+', '', item).strip()
                    if item:
                        current_items.append(item)
        
        # Finalize last section
        if current_section:
            self._finalize_section(feedback, current_section, current_items)
        
        return feedback
    
    def _finalize_section(self, feedback: EvaluationFeedback, section: str, items: List[str]):
        """Finalize a section with collected items."""
        if section == 'strengths':
            feedback.strengths = items
        elif section == 'gaps':
            feedback.gaps = items
        elif section == 'missed_concepts':
            feedback.missed_concepts = items
        elif section == 'followup':
            feedback.followup_questions = items
        elif section == 'overall':
            feedback.overall_assessment = ' '.join(items).strip()
    
    def evaluate(
        self,
        question: str,
        candidate_answer: str,
        retrieval_result: RetrievalResult,
        reference_answer: Optional[GeneratedAnswer] = None
    ) -> EvaluationFeedback:
        """
        Evaluate a candidate's answer against retrieved knowledge.
        
        Args:
            question: Original interview question
            candidate_answer: Candidate's answer text
            retrieval_result: Retrieved knowledge chunks
            reference_answer: Optional reference answer for context
        
        Returns:
            EvaluationFeedback with structured evaluation
        """
        if not retrieval_result.retrieved_chunks:
            return EvaluationFeedback(
                strengths=[],
                gaps=["No knowledge chunks were retrieved for evaluation."],
                missed_concepts=[],
                followup_questions=[],
                overall_assessment="Cannot evaluate answer: no knowledge base context available.",
                confidence_score=1
            )
        
        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(
            question=question,
            candidate_answer=candidate_answer,
            retrieved_chunks=retrieval_result.retrieved_chunks,
            reference_answer=reference_answer
        )
        
        # Generate evaluation
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1500
            )
            
            evaluation_text = response.choices[0].message.content.strip()
            
            # Parse evaluation
            feedback = self._parse_evaluation_response(evaluation_text)
            
            return feedback
            
        except Exception as e:
            return EvaluationFeedback(
                strengths=[],
                gaps=[f"Error during evaluation: {e}"],
                missed_concepts=[],
                followup_questions=[],
                overall_assessment=f"Evaluation failed due to error: {e}",
                confidence_score=1
            )


def main():
    """Test the answer judge."""
    from core.retriever import KnowledgeRetriever
    from core.answer_generator import AnswerGenerator
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    vector_db_dir = project_root / "data" / "vector_db"
    
    # Retrieve context
    retriever = KnowledgeRetriever(vector_db_dir=vector_db_dir, backend="local")
    retrieval_result = retriever.retrieve(
        "How does TypeScript help with large-scale JavaScript development?",
        debug=False
    )
    
    # Generate reference answer (optional)
    generator = AnswerGenerator()
    reference_answer = generator.generate(retrieval_result)
    
    # Candidate answer (example)
    candidate_answer = """
    TypeScript is a superset of JavaScript that adds static typing.
    It helps catch errors at compile time and provides better IDE support.
    For large-scale development, it helps with code organization and refactoring.
    """
    
    # Evaluate
    judge = AnswerJudge()
    feedback = judge.evaluate(
        question="How does TypeScript help with large-scale JavaScript development?",
        candidate_answer=candidate_answer,
        retrieval_result=retrieval_result,
        reference_answer=reference_answer
    )
    
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print(f"\nSTRENGTHS ({len(feedback.strengths)}):")
    for strength in feedback.strengths:
        print(f"  • {strength}")
    
    print(f"\nGAPS ({len(feedback.gaps)}):")
    for gap in feedback.gaps:
        print(f"  • {gap}")
    
    print(f"\nMISSED CONCEPTS ({len(feedback.missed_concepts)}):")
    for concept in feedback.missed_concepts:
        print(f"  • {concept}")
    
    print(f"\nFOLLOW-UP QUESTIONS ({len(feedback.followup_questions)}):")
    for question in feedback.followup_questions:
        print(f"  • {question}")
    
    print(f"\nOVERALL ASSESSMENT:")
    print(f"  {feedback.overall_assessment}")
    
    print(f"\nCONFIDENCE SCORE: {feedback.confidence_score}/5")


if __name__ == "__main__":
    main()
