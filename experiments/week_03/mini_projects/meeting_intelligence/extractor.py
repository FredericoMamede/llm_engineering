"""
Meeting Intelligence Extractor

Extracts structured information from meeting transcripts using LLMs.
"""

import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from schemas import MeetingIntelligence, meeting_to_dict


# Load environment variables
load_dotenv()


class MeetingExtractor:
    """
    Extracts structured information from meeting transcripts.
    
    Uses OpenAI API to analyze meeting text and extract:
    - Key decisions
    - Action items
    - Attendees
    - Topics
    - Summary
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize the extractor.
        
        Args:
            model: OpenAI model to use (default: gpt-4o-mini)
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            temperature: Generation temperature (lower = more structured)
        """
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter"
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def _load_prompt_template(self) -> str:
        """Load the prompt template from prompts/meeting_analysis.md"""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            "meeting_analysis.md"
        )
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback prompt if file doesn't exist
            return self._default_prompt()
    
    def _default_prompt(self) -> str:
        """Default prompt if template file is missing"""
        return """You are a meeting intelligence system. Extract structured information from the meeting transcript below.

Extract:
1. Meeting title, date, duration
2. List of attendees and organizer
3. A concise summary (2-3 paragraphs)
4. Topics discussed (with summaries)
5. Decisions made (with rationale and impact)
6. Action items (with owner, due date, priority)
7. Key insights
8. Next steps

Output ONLY valid JSON matching this schema:
{
  "title": "Meeting Title",
  "date": "YYYY-MM-DD",
  "duration_minutes": 60,
  "attendees": ["Name1", "Name2"],
  "organizer": "Name",
  "summary": "Meeting summary...",
  "topics": [
    {"topic": "Topic name", "summary": "Summary", "duration_minutes": 15}
  ],
  "decisions": [
    {"decision": "Decision text", "rationale": "Why", "impact": "Impact"}
  ],
  "action_items": [
    {"item": "Action", "owner": "Name", "due_date": "YYYY-MM-DD", "priority": "high"}
  ],
  "key_insights": ["Insight 1", "Insight 2"],
  "next_steps": ["Step 1", "Step 2"],
  "metadata": {}
}

Meeting transcript:
{transcript}"""
    
    def extract(self, transcript_path: str) -> Dict[str, Any]:
        """
        Extract structured information from a meeting transcript.
        
        Args:
            transcript_path: Path to meeting transcript file
            
        Returns:
            Dictionary with extracted meeting information
        """
        # Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        
        # Load prompt template
        prompt_template = self._load_prompt_template()
        
        # Replace placeholder if present
        if "{transcript}" in prompt_template:
            prompt = prompt_template.replace("{transcript}", transcript)
        else:
            # Append transcript if no placeholder
            prompt = f"{prompt_template}\n\nMeeting transcript:\n{transcript}"
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a meeting intelligence system. Extract structured information and output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Parse JSON response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {result_text}")
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {e}")
    
    def extract_to_file(
        self,
        transcript_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract and save to file.
        
        Args:
            transcript_path: Path to meeting transcript
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to output file
        """
        result = self.extract(transcript_path)
        
        # Generate output path if not provided
        if output_path is None:
            import datetime
            base_name = os.path.splitext(os.path.basename(transcript_path))[0]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(
                os.path.dirname(__file__),
                "sample_outputs"
            )
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}_{timestamp}.json")
        
        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_path
