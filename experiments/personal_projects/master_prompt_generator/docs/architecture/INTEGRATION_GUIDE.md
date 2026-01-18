# Integration Guide - New Components

This guide explains how the new world-class enhancements integrate with the existing system.

---

## Component Integration Map

### 1. Prompt Lifecycle & Versioning

**Location**: `PROMPT_LIFECYCLE.md` (documentation), `core/prompt_generator.py` (implementation)

**Integration Points**:
- `PromptGenerator.generate()` → Creates prompt with lifecycle state "generated"
- `PromptEvaluator.score_prompt()` → Transitions to "evaluated"
- `PromptRefiner.refine()` → Creates new version, transitions to "refined"
- UI → Shows lifecycle state, version history, allows approval/archival

**Metadata Storage**:
- All prompts stored with full metadata schema
- Version relationships tracked (parent → children)
- Change reasons documented

**API Changes**:
```python
# New methods in PromptGenerator
def generate_with_versioning(self, ...) -> PromptWithMetadata:
    prompt = self.generate(...)
    return PromptWithMetadata(
        prompt=prompt,
        version="1.0.0",
        lifecycle_state="generated",
        parent_prompt_id=None,
        ...
    )

# New methods in PromptRefiner
def refine_with_tracking(self, prompt_id, ...) -> PromptWithMetadata:
    parent = self.get_prompt(prompt_id)
    refined = self.refine(parent.prompt, ...)
    return PromptWithMetadata(
        prompt=refined,
        version=self._increment_version(parent.version, change_type),
        lifecycle_state="refined",
        parent_prompt_id=prompt_id,
        evaluation_score_before=parent.evaluation_score,
        change_reason=change_reason,
        ...
    )
```

---

### 2. Model Manager & Availability

**Location**: `core/model_manager.py`, `config/model_prompt_profiles.yaml`

**Responsibilities**:
- Load model profiles from YAML configuration
- Initialize LLM clients based on available API keys
- Check Ollama runtime availability for local models
- Provide availability status for all supported models
- Map model names to appropriate providers

**Key Methods**:
- `get_all_supported_models()` → Returns all models with availability status
- `check_model_availability(model_name)` → Returns (is_available, reason)
- `get_model_profile(model_name)` → Returns model adaptation profile
- `get_client(model_name)` → Returns initialized client or None

**Integration Points**:
- `PromptGenerator.generate()` → Uses ModelManager to get client and profile
- UI → Uses ModelManager to populate model dropdown with availability
- `PromptEvaluator` → Uses ModelManager for model-specific evaluation criteria

### 3. Model-Specific Prompt Adaptation

**Location**: `config/model_prompt_profiles.yaml`, `core/prompt_generator.py`

**Integration Points**:
- `PromptGenerator.generate()` → Loads model profile via ModelManager, applies adaptations
- UI → Model selector shows all models with availability status
- `PromptEvaluator` → Considers model-specific quality criteria

**Implementation Flow**:
```python
# In PromptGenerator.generate()
def generate(self, ..., target_model: str):
    # 1. Load model profile
    profile = self._load_model_profile(target_model)
    
    # 2. Build base meta-prompt
    meta_prompt = self._build_meta_prompt(...)
    
    # 3. Add model-specific instructions
    meta_prompt += f"\n\nModel-specific preferences for {target_model}:"
    for preference in profile.prefers:
        meta_prompt += f"\n- {preference.description}"
    
    # 4. Generate
    prompt = self._call_llm(meta_prompt)
    
    # 5. Apply adaptations
    adapted_prompt = self._apply_adaptations(prompt, profile)
    
    # 6. Track adaptations in metadata
    metadata.model_adaptations_applied = profile.adaptations
    
    return adapted_prompt, metadata
```

**UI Integration**:
- Model dropdown triggers adaptation preview
- Shows "Adapted for {model}" badge
- Explains what adaptations were applied

---

### 3. Prompt Smell Detector

**Location**: `core/prompt_smell_detector.py`

**Integration Points**:
- `PromptEvaluator.score_prompt()` → Runs detector, includes in score
- `PromptRefiner.refine()` → Uses suggestions to improve prompts
- UI → Shows anti-patterns with severity and fixes

**Implementation Flow**:
```python
# In PromptEvaluator.score_prompt()
def score_prompt(self, prompt: str) -> EvaluationResult:
    # 1. Run smell detector
    detector = PromptSmellDetector()
    anti_patterns = detector.detect(prompt)
    
    # 2. Adjust scores based on anti-patterns
    base_score = self._calculate_base_score(prompt)
    penalty = self._calculate_penalty(anti_patterns)
    final_score = base_score - penalty
    
    # 3. Include in result
    return EvaluationResult(
        score=final_score,
        metrics={...},
        anti_patterns=anti_patterns,
        smell_report=detector.generate_report(anti_patterns)
    )

# In PromptRefiner.refine()
def refine(self, prompt: str, evaluation_result: EvaluationResult):
    # 1. Get fix suggestions from detector
    suggestions = evaluation_result.anti_patterns.get_fix_suggestions()
    
    # 2. Build refinement prompt
    refinement_prompt = f"""
    Refine this prompt by addressing these issues:
    {suggestions}
    
    Original prompt:
    {prompt}
    """
    
    # 3. Generate refined version
    refined = self._call_llm(refinement_prompt)
    
    return refined
```

**UI Integration**:
- Warning badges for detected anti-patterns
- Expandable sections showing issues
- "Fix Issues" button triggers auto-refinement

---

### 4. Token Economics

**Location**: `core/token_economics.py`

**Integration Points**:
- `PromptGenerator.generate()` → Estimates tokens during generation
- `PromptEvaluator.score_prompt()` → Includes economics in evaluation
- UI → Shows cost estimates, efficiency scores
- `PromptRefiner.refine()` → Suggests optimizations

**Implementation Flow**:
```python
# In PromptGenerator.generate()
def generate(self, ..., use_case: str, complexity_tier: int):
    # ... generate prompt ...
    
    # Calculate economics
    economics = TokenEconomics()
    estimate = economics.analyze_prompt_economics(
        prompt=generated_prompt,
        use_case=use_case,
        complexity_tier=complexity_tier,
        models=[target_model]
    )
    
    # Include in metadata
    metadata.estimated_input_tokens = estimate.input_tokens
    metadata.estimated_output_tokens = estimate.output_tokens
    metadata.estimated_cost_per_run = estimate.estimated_cost
    
    return generated_prompt, metadata

# In UI
def display_prompt_with_economics(prompt, metadata):
    # Show token counts
    print(f"Input: {metadata.estimated_input_tokens} tokens")
    print(f"Output: ~{metadata.estimated_output_tokens} tokens")
    
    # Show costs
    for model, cost in metadata.estimated_cost_per_run.items():
        print(f"{model}: ${cost:.4f} per run")
    
    # Show efficiency
    print(f"Efficiency: {metadata.verbosity_efficiency_score:.0%}")
    print(f"Tradeoff: {metadata.cost_quality_tradeoff}")
```

**UI Integration**:
- Cost estimate panel
- Token count display
- Efficiency meter
- "Optimize for Cost" button
- Comparison view for prompt variants

---

## Data Flow with All Components

```
User Input
    ↓
[Use Case Selection] → [Model Selection]
    ↓
[PromptGenerator.generate()]
    ├── Load model profile → Apply adaptations
    ├── Build meta-prompt
    ├── Generate prompt
    └── Calculate token economics
    ↓
[PromptWithMetadata] (state: "generated", version: "1.0.0")
    ↓
[PromptEvaluator.score_prompt()]
    ├── Calculate quality scores (6 criteria)
    ├── Run smell detector → Detect anti-patterns
    ├── Analyze token economics
    └── Generate evaluation report
    ↓
[EvaluationResult] (state: "evaluated", score: 7.5)
    ↓
[Decision: Refine?]
    ├── Yes → [PromptRefiner.refine()]
    │   ├── Use anti-pattern suggestions
    │   ├── Apply optimizations (if requested)
    │   ├── Create new version (1.1.0)
    │   └── Track parent relationship
    │   ↓
    │   [Re-evaluate] → Loop until approved
    │
    └── No → [Approve]
        ↓
[PromptWithMetadata] (state: "approved", version: "1.0.0")
    ↓
[Save/Export]
```

---

## Database Schema Updates

```sql
-- Add new columns to prompts table
ALTER TABLE prompts ADD COLUMN IF NOT EXISTS
    parent_prompt_id UUID REFERENCES prompts(id),
    lifecycle_state VARCHAR(20) DEFAULT 'draft',
    change_reason TEXT,
    evaluation_score_before FLOAT,
    evaluation_score_after FLOAT,
    evaluation_delta FLOAT,
    estimated_input_tokens INTEGER,
    estimated_output_tokens INTEGER,
    verbosity_efficiency_score FLOAT,
    cost_quality_tradeoff VARCHAR(20),
    has_anti_patterns BOOLEAN DEFAULT FALSE,
    anti_patterns_detected JSONB,
    model_adaptations_applied JSONB;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_prompts_parent ON prompts(parent_prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompts_state ON prompts(lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_prompts_version ON prompts(version);
```

---

## Configuration Updates

### `config/model_prompt_profiles.yaml`
- Already created with profiles for Claude, GPT, Gemini, Llama, Qwen, DeepSeek
- Loaded by `ModelManager` on startup
- Used by `PromptGenerator` for adaptations

### `config/settings.yaml` (to be created)
```yaml
evaluation:
  quality_threshold: 8.0  # Minimum score for approval
  regression_threshold: 0.5  # Score drop to trigger alert

economics:
  show_cost_estimates: true
  default_models: ["claude-sonnet", "gpt-4o", "llama3.2:latest"]
  optimization_target: 0.2  # 20% reduction target

lifecycle:
  auto_evaluate: true
  require_approval: false  # Auto-approve if score > threshold
  archive_after_days: 365
```

---

## Testing Integration

### Unit Tests
```python
def test_prompt_lifecycle():
    generator = PromptGenerator()
    prompt = generator.generate(...)
    assert prompt.lifecycle_state == "generated"
    
    evaluator = PromptEvaluator()
    result = evaluator.score_prompt(prompt.prompt)
    assert prompt.lifecycle_state == "evaluated"

def test_model_adaptation():
    generator = PromptGenerator()
    prompt_claude = generator.generate(..., target_model="claude-sonnet")
    prompt_gpt = generator.generate(..., target_model="gpt-4o")
    
    # Should have different adaptations
    assert prompt_claude.model_adaptations_applied != prompt_gpt.model_adaptations_applied

def test_smell_detection():
    detector = PromptSmellDetector()
    bad_prompt = "Generate text. Don't generate text. Must include examples. Never include examples."
    patterns = detector.detect(bad_prompt)
    assert len(patterns) > 0
    assert any(p.name == "conflicting_instructions" for p in patterns)

def test_token_economics():
    economics = TokenEconomics()
    estimate = economics.analyze_prompt_economics(
        prompt="Test prompt",
        use_case="summarization",
        complexity_tier=2
    )
    assert estimate.input_tokens > 0
    assert estimate.estimated_cost["gpt-4o"] > 0
```

---

## Migration Path

### For Existing Prompts
1. Set default lifecycle state to "approved"
2. Set version to "1.0.0"
3. Calculate token estimates retroactively
4. Run smell detector on existing prompts
5. Mark prompts with anti-patterns for review

### For New Prompts
- All new prompts automatically get full metadata
- Lifecycle tracking from generation
- Versioning from first refinement
- Economics calculated on generation

---

This integration guide ensures all new components work seamlessly with the existing architecture while maintaining the system's focus and quality.
