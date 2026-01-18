# UI Testing Examples - Master Prompt Generator


> This document describes **manual UI and behavior testing scenarios**.
> It complements automated tests but is not a replacement for them.


## Why Do Some Models Appear Disabled (🔒) in the UI?

The model dropdown shows **all supported models** defined in
`config/model_prompt_profiles.yaml`.

Models may appear disabled (🔒) when:
- An API key is missing (paid models)
- Ollama is not running (local models)
- Hugging Face gated access is not configured (LLaMA-4)

This is intentional and enforces the principle:

Capability ≠ Availability

The UI always shows what the system *supports*, even if a model
is not currently usable on this machine.


---

## Comprehensive Testing Examples

### Example 1: Business Email (Simple → Complex)

**Test Purpose**: Basic generation, evaluation, and approval flow

**Input**:
- **Use Case**: "Write a professional follow-up email after a client meeting"
- **Category**: `business`
- **Complexity Tier**: `2` (Intermediate)
- **Context**: 
  ```
  The meeting discussed project timeline and deliverables. 
  Need to follow up with action items and request confirmation 
  on the proposed schedule.
  ```
- **Additional Requirements**:
  ```
  Professional tone
  Include action items
  Request confirmation
  Mention next steps
  ```
- **Target Model**: `claude-sonnet`

**Expected Flow**:
1. Click "Generate Prompt" → Should create prompt with version 1.0.0
2. Check metadata → Should show lifecycle_state="generated"
3. Click "Evaluate" → Should score 6 metrics, show anti-patterns
4. If score < 8.0 → Click "Refine" → Should create version 1.1.0
5. Re-evaluate → Score should improve
6. Click "Approve" → Should transition to "approved" state

---

### Example 2: Technical Code Explanation (Test Model Adaptation)

**Test Purpose**: Verify model-specific adaptations are applied

**Input**:
- **Use Case**: "Explain a complex Python function to a beginner"
- **Category**: `technical`
- **Complexity Tier**: `3` (Advanced)
- **Context**:
  ```
  Need to explain recursive algorithms, specifically a binary 
  search tree traversal function. Target audience is beginners 
  who understand basic Python but not advanced concepts.
  ```
- **Additional Requirements**:
  ```
  Use simple language
  Include step-by-step breakdown
  Provide examples
  Explain recursion concept
  ```
- **Target Model**: `gpt-4o` (Test GPT-specific adaptations)

**What to Check**:
- Metadata should show `model_adaptations_applied` with GPT-specific preferences
- Prompt should use GPT-preferred structure (strict schemas, explicit JSON formatting)
- Token economics should show cost for GPT-4o

---

### Example 3: Creative Writing (Test Breaking Change Detection)

**Test Purpose**: Test refinement and version increment logic

**Input**:
- **Use Case**: "Generate a sci-fi short story prompt"
- **Category**: `creative`
- **Complexity Tier**: `4` (Expert)
- **Context**:
  ```
  Create a prompt that will generate a compelling sci-fi story 
  about time travel paradoxes, with strong character development 
  and unexpected plot twists.
  ```
- **Additional Requirements**:
  ```
  Include character development guidelines
  Specify plot structure
  Request unexpected twists
  ```
- **Target Model**: `gemini-2.5-pro`

**Test Steps**:
1. Generate initial prompt
2. Evaluate → Note the score
3. Refine → Check if version increments (should be 1.1.0 for minor changes)
4. Make a major change manually (change technique from zero-shot to few-shot)
5. Refine again → Should increment to 2.0.0 (major version for breaking change)

---

### Example 4: Regression Detection (Test Guards)

**Test Purpose**: Verify regression blocking works

**Input**:
- **Use Case**: "Write a product review analysis prompt"
- **Category**: `analysis`
- **Complexity Tier**: `2` (Intermediate)
- **Context**:
  ```
  Need to analyze customer reviews and extract sentiment, 
  key themes, and actionable insights for product improvement.
  ```
- **Additional Requirements**:
  ```
  Extract sentiment
  Identify key themes
  Provide actionable insights
  ```
- **Target Model**: `claude-sonnet`

**Test Steps**:
1. Generate → Version 1.0.0, score ~8.5
2. Evaluate → Record score
3. Manually modify prompt to be worse (remove instructions, make vague)
4. Refine → Should create version 1.1.0
5. Evaluate → Score should drop
6. Try to Approve → **Should FAIL** with "REGRESSION DETECTED" blocker
7. Check approval status → Should show regression blocker clearly

---

### Example 5: Lifecycle Guard Testing (Test Invalid Operations)

**Test Purpose**: Verify guards prevent misuse

**Input**: Use any example above

**Test Invalid Operations**:
1. **Try to approve without evaluation**:
   - Generate prompt
   - Immediately click "Approve" (skip Evaluate)
   - **Expected**: Should fail with error about needing evaluation

2. **Try to refine archived prompt**:
   - Generate → Evaluate → Approve → Archive (if implemented)
   - Try to Refine
   - **Expected**: Should fail with "Cannot refine archived prompt"

3. **Check version immutability**:
   - Generate → Evaluate → Approve
   - Try to modify approved prompt
   - **Expected**: Should fail with "Approved prompts are immutable"

---

### Example 6: Token Economics (Test Cost Analysis)

**Test Purpose**: Verify token economics are calculated correctly

**Input**:
- **Use Case**: "Generate a comprehensive market analysis report"
- **Category**: `business`
- **Complexity Tier**: `4` (Expert)
- **Context**: 
  ```
  Very long context with detailed requirements, multiple sections, 
  extensive formatting requirements, and comprehensive analysis needs.
  ```
- **Additional Requirements**: (Leave extensive)
- **Target Model**: `claude-sonnet`

**What to Check**:
- Token Economics section should show:
  - Input tokens: ~500-1000+
  - Output tokens: ~200-500
  - Cost per run: ~$0.01-0.05 (for Claude)
  - Efficiency score: percentage
  - Cost-quality tradeoff: "balanced" or other

---

### Example 7: Anti-Pattern Detection (Test Smell Detector)

**Test Purpose**: Verify anti-patterns are detected and suggestions provided

**Input** (Intentionally Bad):
- **Use Case**: "Write something"
- **Category**: `business`
- **Complexity Tier**: `1` (Simple)
- **Context**: "Do it"
- **Additional Requirements**: (Leave empty or vague)
- **Target Model**: `claude-sonnet`

**What to Check**:
- Generate prompt
- Evaluate
- Anti-Patterns section should show:
  - Overly vague
  - Missing context
  - Low specificity
  - Each with severity and fix suggestions

---

### Example 8: Version History (Test Parent-Child Relationships)

**Test Purpose**: Verify version tracking works correctly

**Input**: Use Example 1

**Test Steps**:
1. Generate → Version 1.0.0 (no parent)
2. Refine → Version 1.1.0 (parent: 1.0.0)
3. Refine again → Version 1.2.0 (parent: 1.1.0)
4. Check metadata → Should show:
   - Version increments correctly
   - Parent relationships maintained
   - Change reasons tracked
   - Score deltas calculated

---

### Example 9: Multi-Model Comparison (Test Different Adaptations)

**Test Purpose**: Compare how prompts adapt for different models

**Input**: Use Example 1 (Business Email)

**Test Steps**:
1. Generate with `claude-sonnet`
   - Check model adaptations → Should prefer polite constraints, longer context
2. Generate same use case with `gpt-4o`
   - Check model adaptations → Should prefer strict schemas, explicit JSON
3. Generate same use case with `gemini-2.5-pro`
   - Check model adaptations → Should prefer concise structure
4. Compare → Prompts should be adapted differently for each model

---

### Example 10: Full Workflow (End-to-End)

**Test Purpose**: Complete workflow from generation to approval

**Input**:
- **Use Case**: "Create a data analysis prompt for sales data"
- **Category**: `analysis`
- **Complexity Tier**: `3` (Advanced)
- **Context**:
  ```
  Analyze monthly sales data, identify trends, detect anomalies, 
  and provide actionable recommendations. Data includes revenue, 
  units sold, customer segments, and geographic regions.
  ```
- **Additional Requirements**:
  ```
  Output in JSON format
  Include statistical analysis
  Provide visualizations suggestions
  Identify top performers
  Flag anomalies
  ```
- **Target Model**: `claude-sonnet`

**Complete Flow**:
1. **Generate** → Prompt created, version 1.0.0, state="generated"
2. **Evaluate** → Score calculated, anti-patterns checked, state="evaluated"
3. **Check Approval Status** → Shows blockers if any
4. **Refine** (if needed) → New version created, parent tracked
5. **Re-evaluate** → New score, delta calculated
6. **Approve** → State="approved", approved_at timestamp set
7. **Verify Immutability** → Try to modify → Should fail

---

## Testing Checklist

### Core Functionality
- [ ] Generate prompt successfully
- [ ] Evaluate prompt (6 metrics scored)
- [ ] Refine prompt (version increments)
- [ ] Approve prompt (when conditions met)

### Guards & Integrity
- [ ] Cannot approve without evaluation
- [ ] Cannot refine archived prompts
- [ ] Regression blocks approval
- [ ] Approved prompts are immutable
- [ ] Version increments correctly

### Metadata & Display
- [ ] Version displayed correctly
- [ ] Lifecycle state shown
- [ ] Parent version tracked
- [ ] Quality metrics displayed
- [ ] Anti-patterns shown with severity
- [ ] Token economics calculated
- [ ] Model adaptations listed

### Model-Specific Features
- [ ] Claude adaptations applied
- [ ] GPT adaptations applied
- [ ] Gemini adaptations applied
- [ ] Ollama works (if running locally)

---

## Tips for Maximum Testing

1. **Test Edge Cases**:
   - Very short use cases
   - Very long contexts
   - Empty requirements
   - Maximum complexity tier

2. **Test Error Handling**:
   - Missing API keys (should fail gracefully)
   - Invalid model names
   - Network errors

3. **Test UI Responsiveness**:
   - Multiple rapid clicks
   - Large prompt outputs
   - Long metadata displays

4. **Test Version History**:
   - Multiple refinements
   - Breaking changes (major version)
   - Regression scenarios

---

## Expected Behaviors

✅ **Should Work**:
- All buttons respond correctly
- Metadata updates in real-time
- Version history tracks correctly
- Guards prevent invalid operations
- Errors are clear and actionable

❌ **Should Fail Gracefully**:
- Missing API keys → Clear error message
- Invalid operations → Exception with explanation
- Network errors → User-friendly message
- Invalid inputs → Validation errors

---

**Happy Testing!** 🚀
