"""
Semantic chunking with structured outputs for interview preparation.

This module transforms normalized source documents into semantically meaningful
chunks suitable for expert reasoning and interview preparation.
"""

import json
import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

load_dotenv(override=True)

MODEL = "openai/gpt-4o-mini"  # Using gpt-4o-mini for cost efficiency
wait = wait_exponential(multiplier=1, min=2, max=30)


class ChunkMetadata(BaseModel):
    """Metadata inherited from source document."""
    requirement_id: Optional[str] = None
    company_domain: Optional[str] = None
    source_url: str
    source_type: str
    freshness_year: str


class SemanticChunk(BaseModel):
    """A semantically coherent chunk of content."""
    chunk_id: str = Field(
        description="Deterministic, stable identifier for this chunk"
    )
    headline: str = Field(
        description="Clear, interview-salient heading (typically a few words)"
    )
    summary: str = Field(
        description="2-4 sentences summarizing the content, factual and grounded"
    )
    original_text: str = Field(
        description="Verbatim excerpt from the source document, unchanged"
    )
    chunk_type: str = Field(
        description="One of: primary, interview_question, tradeoff, failure_mode"
    )
    inherited_metadata: ChunkMetadata


class ChunkList(BaseModel):
    """List of chunks for a document."""
    chunks: List[SemanticChunk]
    missing_chunk_types: List[str] = Field(
        default_factory=list,
        description="Chunk types that were intended but not possible to create from this source"
    )


class DocumentSource:
    """Represents a source document with metadata."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.metadata: Dict[str, Any] = {}
        self.content: str = ""
        self._parse()
    
    def _parse(self):
        """Parse YAML frontmatter and Markdown content."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and body
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1].strip()
                self.content = parts[2].strip()
                
                # Parse YAML frontmatter
                try:
                    self.metadata = yaml.safe_load(frontmatter_str) or {}
                except yaml.YAMLError as e:
                    print(f"⚠️  Warning: Failed to parse YAML frontmatter in {self.filepath}: {e}")
                    self.metadata = {}
            else:
                self.content = content
        else:
            self.content = content
    
    def get_chunk_metadata(self) -> ChunkMetadata:
        """Extract chunk metadata from document metadata."""
        return ChunkMetadata(
            requirement_id=self.metadata.get('requirement_id'),
            company_domain=self.metadata.get('company_domain'),
            source_url=self.metadata.get('source_url', ''),
            source_type=self.metadata.get('source_type', ''),
            freshness_year=self.metadata.get('freshness_year', '2024')
        )
    
    def get_intended_chunk_types(self) -> List[str]:
        """Get intended chunk types from document metadata."""
        chunk_types = self.metadata.get('chunk_types', [])
        if isinstance(chunk_types, str):
            chunk_types = [ct.strip() for ct in chunk_types.split(',')]
        return chunk_types if isinstance(chunk_types, list) else []


class SemanticChunker:
    """Create semantic chunks from source documents."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_chunk_id(self, source_path: Path, chunk_index: int, headline: str) -> str:
        """Generate deterministic chunk ID."""
        # Use source filename, index, and headline hash for stability
        source_name = source_path.stem
        headline_hash = hashlib.md5(headline.encode()).hexdigest()[:8]
        return f"{source_name}_chunk_{chunk_index}_{headline_hash}"
    
    def _create_chunking_prompt(self, document: DocumentSource) -> str:
        """Create prompt for LLM-based semantic chunking."""
        intended_types = document.get_intended_chunk_types()
        intended_types_str = ", ".join(intended_types) if intended_types else "primary"
        
        # Determine context
        if document.metadata.get('requirement_id'):
            context = f"Requirement: {document.metadata.get('requirement_id')} - {document.metadata.get('category', '')}"
        elif document.metadata.get('company_domain'):
            context = f"Company Context: {document.metadata.get('company_domain')}"
        else:
            context = "General technical content"
        
        prompt = f"""You are creating semantic chunks for an AI Interview Preparation Assistant.

CONTEXT:
{context}
Source: {document.metadata.get('source_name', 'Unknown')}
Source Type: {document.metadata.get('source_type', 'Unknown')}

CHUNKING RULES:
1. Create SEMANTIC chunks - each chunk represents ONE coherent idea or concept
2. Do NOT use token-based or size-based splitting
3. Do NOT summarize the entire document into one chunk
4. Do NOT hallucinate or infer missing content
5. Preserve verbatim original text in each chunk

CHUNK TYPES TO CREATE:
Intended chunk types: {intended_types_str}

For each chunk, assign ONE of these types:
- primary: Core authoritative content, main concepts
- interview_question: Content that answers common interview questions
- tradeoff: Discussions of tradeoffs, design decisions, alternatives
- failure_mode: Error handling, edge cases, failure scenarios

ACROSS ALL CHUNKS, attempt to create:
- At least one primary chunk
- At least one interview_question chunk  
- At least one tradeoff OR failure_mode chunk

If the document is shallow, index-like, or navigation-only:
- Create 1-2 high-level chunks only
- Mark missing chunk types explicitly

TONE & AUDIENCE:
- Assume readers are senior engineers or hiring managers
- Avoid tutorial tone
- Emphasize reasoning, constraints, and real-world framing
- Prefer depth over breadth

OUTPUT FORMAT:
For each chunk, provide:
- headline: Clear, interview-salient heading (few words)
- summary: 2-4 sentences, factual, grounded in the original text
- original_text: Verbatim excerpt from the document (unchanged)
- chunk_type: One of the types listed above

DOCUMENT CONTENT:
{document.content}

CRITICAL REQUIREMENTS:
- Ensure ALL document content is represented across chunks (no content left out)
- Each chunk should be semantically coherent (one idea/concept)
- Overlap between chunks is acceptable for context preservation
- Original text must be verbatim - do not modify or summarize it
- If document is too shallow for intended chunk types, mark them as missing

Respond with a JSON object containing:
- chunks: List of semantic chunks
- missing_chunk_types: List of intended chunk types that could not be created"""

        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait)
    def _chunk_document(self, document: DocumentSource) -> ChunkList:
        """Use LLM to create semantic chunks from a document."""
        prompt = self._create_chunking_prompt(document)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = completion(
            model=MODEL,
            messages=messages,
            response_format=ChunkList
        )
        
        reply = response.choices[0].message.content
        chunk_list = ChunkList.model_validate_json(reply)
        
        # Generate chunk IDs and attach metadata
        base_metadata = document.get_chunk_metadata()
        for i, chunk in enumerate(chunk_list.chunks):
            chunk.chunk_id = self._generate_chunk_id(document.filepath, i, chunk.headline)
            chunk.inherited_metadata = base_metadata
        
        return chunk_list
    
    def process_document(self, source_path: Path) -> bool:
        """Process a single source document into chunks."""
        try:
            # Check if chunks already exist
            output_file = self.output_dir / f"{source_path.stem}_chunks.json"
            if output_file.exists():
                print(f"⏭️  Skipping (chunks exist): {source_path.name}")
                return True
            
            print(f"📄 Processing: {source_path.name}")
            
            # Load and parse document
            document = DocumentSource(source_path)
            
            # Skip if content is too shallow
            if len(document.content.strip()) < 100:
                print(f"   ⚠️  Document too short, creating minimal chunk")
                # Create a single high-level chunk
                base_metadata = document.get_chunk_metadata()
                chunk = SemanticChunk(
                    chunk_id=self._generate_chunk_id(source_path, 0, "Document Overview"),
                    headline="Document Overview",
                    summary=f"This document ({document.metadata.get('source_name', 'Unknown')}) contains minimal or index-like content.",
                    original_text=document.content[:500] if len(document.content) > 500 else document.content,
                    chunk_type="primary",
                    inherited_metadata=base_metadata
                )
                chunk_list = ChunkList(
                    chunks=[chunk],
                    missing_chunk_types=["interview_question", "tradeoff", "failure_mode"]
                )
            else:
                # Use LLM for semantic chunking
                chunk_list = self._chunk_document(document)
            
            # Save chunks as JSON
            output_data = {
                "source_file": str(source_path.name),
                "source_metadata": document.metadata,
                "chunks": [chunk.model_dump() for chunk in chunk_list.chunks],
                "missing_chunk_types": chunk_list.missing_chunk_types,
                "total_chunks": len(chunk_list.chunks)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created {len(chunk_list.chunks)} chunks")
            if chunk_list.missing_chunk_types:
                print(f"   ⚠️  Missing chunk types: {', '.join(chunk_list.missing_chunk_types)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing {source_path.name}: {e}")
            return False
    
    def process_all(self, sources_dir: Path):
        """Process all source documents."""
        source_files = list(sources_dir.glob("*.md"))
        
        print(f"🔍 Found {len(source_files)} source documents")
        
        successful = 0
        failed = 0
        skipped = 0
        
        for source_file in tqdm(source_files, desc="Chunking documents"):
            result = self.process_document(source_file)
            if result:
                successful += 1
            else:
                failed += 1
        
        print(f"\n✅ Chunking complete!")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Total: {len(source_files)}")


def main():
    """Main entry point for semantic chunking."""
    project_root = Path(__file__).parent.parent
    sources_dir = project_root / "data" / "sources"
    output_dir = project_root / "data" / "chunks"
    
    chunker = SemanticChunker(output_dir)
    chunker.process_all(sources_dir)


if __name__ == "__main__":
    main()
