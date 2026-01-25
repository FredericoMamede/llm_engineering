# Usage Guide

## Overview

The AI Interview Preparation Assistant provides a production-grade RAG system for technical interview preparation. The system offers two main modes:

- **Q&A Mode**: You ask questions, the system provides grounded answers
- **Interview Simulator**: The system asks questions, you answer, and receive evaluation with optional teaching

This guide covers how to use both modes effectively.

## Q&A Mode Usage

### Asking Questions

1. **Enter your question** in the "Interview Question" text box
2. **Select a mode** from the dropdown:
   - **Explain Mode**: Best for learning concepts in detail
   - **Interviewer Mode**: Simulates a real interview with follow-ups
   - **Evaluation Mode**: Use when you want to evaluate your own answer
   - **Company-Aware Mode**: Frames answers for Eventyr context
   - **System Design Mode**: Focuses on tradeoffs and architecture
   - **Rapid Fire Mode**: Quick, concise answers
3. **Click "Ask Question"**

### Getting Evaluated

1. Enter your interview question
2. **Enter your answer** in the "Your Answer" text box
3. Select a mode (Evaluation Mode is specifically for this)
4. Click "Ask Question"
5. Review the evaluation feedback:
   - **Strengths**: What you got right
   - **Gaps**: Areas that need improvement
   - **Missed Concepts**: Specific concepts you didn't mention
   - **Follow-up Questions**: Suggested questions to probe deeper
   - **Overall Assessment**: Summary with confidence score

## Interview Simulator Usage

The Interview Simulator inverts control: the system asks questions, you answer, and receive evaluation. Teaching is available on demand only.

### Starting a Session

1. Navigate to the **Interview Simulator** tab
2. Configure your session:
   - **Company**: Select from dropdown (populated from `company_context.yaml`)
   - **Requirement Set**: Select from dropdown (populated from `requirements.yaml`)
   - **Target Difficulty**: Choose easy, medium, or hard
   - **Examiner Personality**: 
     - **Strict**: High bar, minimal feedback, terse
     - **Balanced**: Realistic senior engineer interviewer (default)
     - **Supportive**: Teaching-oriented, encouraging
   - **Max Questions** (optional): Set a limit for the session
   - **Focus Areas** (optional): Comma-separated topics to prioritize
3. Click **"Start Session"**
4. The system generates the first question automatically

### Answering Questions

1. Read the question displayed in the "Current Question" panel
2. Note the **Requirement/Domain** tag and **Difficulty** level
3. Enter your answer in the "Your Answer" text box
4. Click **"Submit Answer"**
5. Review the evaluation in the "Evaluation" panel

### Understanding Evaluation

After submitting an answer, you'll see:

- **Strengths**: ✅ What you got right
- **Gaps**: ⚠️ Areas that need improvement
- **Missed Concepts**: ❌ Specific concepts you didn't mention
- **Follow-up Questions**: 💡 Suggested questions to probe deeper
- **Overall Assessment**: Summary with confidence score
- **Outcome**: ✅ CORRECT, ⚠️ PARTIAL, or ❌ INCORRECT

The outcome is determined by your confidence score:
- **4-5**: CORRECT (strong answer)
- **3**: PARTIAL (some gaps)
- **1-2**: INCORRECT (needs improvement)

### Teaching Options (On Demand)

The system does **not** automatically teach. You must explicitly request it:

1. **Teach Me (Full Explanation)**: Complete explanation of the topic
2. **Show Ideal Answer**: What a strong answer would look like
3. **Why Was My Answer Weak?**: Explanation of what was missing or incorrect
4. **Explain Missed Concepts**: Detailed explanation of concepts you didn't mention

All teaching is grounded in retrieved chunks and cites sources.

### Session Controls

- **Next Question**: Generate a new question (difficulty may adjust based on performance)
- **Retry Question**: Answer the same question again
- **Ask Follow-up**: Request a follow-up question on the same topic
- **Move On**: Skip to the next question without retry
- **End Session**: Conclude the session and view summary

### Progress Tracking

The "Progress" accordion shows:
- Questions asked, answers given, evaluations completed
- Accuracy percentage
- Correct/Partial/Incorrect counts
- Current difficulty level
- Consecutive correct/incorrect streak
- Coverage (requirements and domains covered)
- Weaknesses triggered

### Coverage Visualization

The "Coverage Visualization" accordion shows what has been tested:
- **By Requirement ID**: How many questions covered each requirement
- **By Topic**: Coverage by technical topic (TypeScript, React, PostgreSQL, etc.)
- **By Chunk Type**: Coverage by chunk type (concept, tradeoff, failure_mode, etc.)

This helps you see:
- Which requirements you've practiced
- Which topics need more coverage
- What types of questions you've encountered

**Note**: Coverage means "asked about", not "mastered". Use this to identify gaps in your practice.

### Session Summary

When you end a session, you'll receive a comprehensive summary with:

**Statistics:**
- Total questions, answers, evaluations
- Accuracy percentage
- Correct/Partial/Incorrect breakdown
- Session duration
- Final difficulty level

**Performance Analysis:**
- **Strong Areas**: Requirements/domains where you performed well (2+ correct answers)
- **Weak Areas**: Top weaknesses identified during the session
- **Coverage**: Requirements and domains covered
- **Difficulty Progression**: How difficulty changed over the session

**Example Questions:**
- Representative questions with outcomes (showing different result types)
- Includes difficulty, outcome, and confidence scores

**Recommendations:**
- Focus areas based on weaknesses
- Difficulty suggestions
- Coverage recommendations

**Export Options:**
- **Export as JSON**: Full session data for analysis
- **Export as Markdown**: Formatted summary for notes

The summary is grounded in actual session data - no hallucinated insights.

### Difficulty Progression

The system adapts difficulty automatically:
- **Escalates** after 2 consecutive correct answers
- **Descalates** after 2 consecutive incorrect answers
- **Partial** answers don't change difficulty

This ensures you're always challenged at an appropriate level.

### Examiner Personality

Choose how the interviewer behaves:

- **Strict**: 
  - High bar for correctness
  - Minimal feedback
  - Terse, direct communication
  - No hints or encouragement
  - Best for: Realistic interview simulation

- **Balanced** (default):
  - Realistic senior engineer interviewer
  - Fair, constructive feedback
  - Professional tone
  - Best for: Standard practice

- **Supportive**:
  - Teaching-oriented approach
  - Encouraging feedback
  - Acknowledges partial understanding
  - Best for: Learning-focused practice

**Note**: Personality affects feedback tone and question phrasing, but **not** scoring logic. All evaluations use the same grounded criteria.

## Advanced Features (Q&A Mode)

### Drill Mode

**Purpose**: Track conversation history for iterative practice sessions.

**How to use**:
1. Check the "Drill Mode" checkbox
2. Ask multiple questions in sequence
3. The system maintains context across questions
4. View recent context in the "Drill Mode Context" panel
5. Uncheck to end the session (saves automatically)

**Use cases**:
- Practice sessions with multiple related questions
- Building on previous answers
- Tracking your progress over time

### Weakness Tracking

**Purpose**: Automatically track concepts you struggle with.

**How it works**:
- When you provide a candidate answer and get evaluated, missed concepts are automatically tracked
- Weaknesses are stored in `data/weaknesses.json`
- View tracked weaknesses in the "Tracked Weaknesses" accordion panel
- Click "Refresh Weaknesses" to update the summary

**What gets tracked**:
- Concept name
- Number of occurrences (how many times you missed it)
- First and last seen dates
- Related questions
- Topic categories (TypeScript, React, PostgreSQL, etc.)

**Use cases**:
- Identify knowledge gaps
- Focus study efforts
- Track improvement over time

### Debug Mode

**Purpose**: Inspect system behavior for transparency.

**How to use**:
1. Check the "Debug Mode" checkbox
2. Ask a question
3. View additional information:
   - Similarity scores for retrieved chunks (color-coded)
   - Retrieval metadata (query, rewritten query, backend, counts)
   - Mode configuration (K values, filters)

**Use cases**:
- Understanding why certain chunks were retrieved
- Verifying system behavior
- Troubleshooting retrieval issues

## Understanding the Output

### Answer Display

- **Answer Text**: The generated answer (strictly grounded in retrieved chunks)
- **Confidence Level**: 🟢 HIGH, 🟡 MEDIUM, or 🔴 LOW
- **Cited Chunks**: Sources used, with chunk type badges and source URLs
- **Refusal Reason**: If the system refuses to answer, this explains why

### Retrieved Context Panel

Shows all chunks that were retrieved for the query:
- Chunk headline
- Chunk type badge
- Source URL (clickable)
- Summary preview
- Similarity score (if debug mode enabled)

### Evaluation Panel

Only appears when you provide a candidate answer:
- **Strengths**: ✅ What you got right
- **Gaps**: ⚠️ Areas for improvement
- **Missed Concepts**: ❌ Concepts you didn't mention
- **Follow-up Questions**: 💡 Suggested questions
- **Overall Assessment**: Summary with confidence score (1-5)

## Best Practices

### For Learning

1. Use **Explain Mode** for detailed explanations
2. Read the **Cited Chunks** to see sources
3. Check **Retrieved Context** to see what knowledge was available
4. Use **Drill Mode** for multi-question practice sessions

### For Practice

1. Use **Interviewer Mode** to simulate real interviews
2. Provide your own answers and get evaluated
3. Review **Missed Concepts** and study those areas
4. Use **Weakness Tracking** to identify patterns
5. Try **Rapid Fire Mode** for quick practice

### For System Design

1. Use **System Design Mode** for architecture questions
2. Focus on **tradeoffs** and **failure modes** mentioned
3. Review **Retrieved Context** for different perspectives

### For Company-Specific Prep

1. Use **Company-Aware Mode** for Eventyr-specific questions
2. Answers will reference Eventyr's constraints and context
3. Useful for understanding company-specific tradeoffs

## Troubleshooting

### System Refuses to Answer

**Why**: Insufficient context retrieved or low similarity scores.

**What to do**:
1. Check the **Refusal Reason** for explanation
2. Try rephrasing your question
3. Check **Retrieved Context** to see what was found
4. Enable **Debug Mode** to see similarity scores

### Low Confidence Answers

**Why**: Few chunks retrieved or low similarity.

**What to do**:
1. Check **Cited Chunks** - are there enough sources?
2. Review **Retrieved Context** - are chunks relevant?
3. Try a more specific question
4. Check if the topic is covered in the knowledge base

### Evaluation Not Appearing

**Why**: You didn't provide a candidate answer, or Evaluation Mode wasn't used.

**What to do**:
1. Make sure you entered text in "Your Answer"
2. For Evaluation Mode, both question and answer are required
3. For other modes, evaluation appears automatically when you provide an answer

## Who This Tool Is For

This tool is designed for:

- **Interview Preparation**: Practice answering technical interview questions with grounded, accurate information
- **Self-Assessment**: Evaluate your own answers against a knowledge base to identify gaps
- **Skill Gap Discovery**: Automatically track concepts you struggle with to focus study efforts
- **Adaptive Practice**: Interview Simulator adjusts difficulty to match your skill level
- **Company-Specific Prep**: Understand how to frame answers for specific companies (e.g., Eventyr)

The system emphasizes:
- **Grounded answers**: All information is traceable to sources
- **No hallucinations**: System refuses when context is insufficient
- **Transparency**: Full visibility into retrieval and evaluation
- **Privacy**: All data (sessions, weaknesses) stored locally

## Running RAG Evaluations

The RAG Evaluation system measures the quality of retrieval and answer generation. Evaluations are run **offline** (outside the UI) and generate artifacts that can be visualized in the RAG Evaluation Dashboard.

### Why Offline?

RAG evaluations are computationally expensive (multiple LLM calls per test case) and should be run intentionally, not automatically. This separation ensures:

- **Explicit Control**: Evaluations run only when explicitly requested
- **Reproducibility**: Each run is a complete, immutable snapshot
- **Resource Management**: Avoids accidental API costs or performance impact
- **Auditability**: Clear separation between evaluation execution and visualization

### Workflow

1. **Run Evaluation**: Execute the offline runner to generate an EvaluationRun artifact
2. **Generate Artifact**: Results are saved to `evaluation/runs/run_YYYYMMDD_HHMMSS.json`
3. **Inspect in UI**: Open the UI and navigate to the "RAG Evaluation" tab to view results

### Running an Evaluation

1. **Configure the runner** (optional):
   - Edit `evaluation/run_evaluation.py`
   - Modify configuration at the top of the file:
     - `TEST_SET_NAME`: Which test set to evaluate ("core", "system_design", "tradeoff", "all")
     - `RETRIEVAL_CONFIG`: Retrieval parameters (top_k, query rewriting)
     - `ANSWER_CONFIG`: Answer generation model and settings
     - `JUDGE_CONFIG`: Evaluation model and settings

2. **Execute the runner**:
   ```bash
   python evaluation/run_evaluation.py
   ```

3. **Monitor progress**: The script prints progress to stdout, including:
   - Test cases being evaluated
   - Completion status
   - Summary metrics when finished

4. **View results**: After completion:
   - Open the UI: `python ui/app.py`
   - Navigate to the **"RAG Evaluation"** tab
   - Select the run from the dropdown (runs are listed by timestamp)
   - Click **"Load Run"** to view:
     - Overall metrics (MRR, nDCG, Recall, Coverage, Confidence)
     - Weakest requirements ranking
     - Chunk type usage analysis
     - Retrieval-answer mismatches
     - Export analysis report

### Understanding Evaluation Metrics

- **Average Concept MRR**: Mean Reciprocal Rank - how highly ranked relevant chunks are
- **Average nDCG@10**: Normalized Discounted Cumulative Gain at rank 10 - ranking quality
- **Average Recall@10**: How many expected concepts are found in top-10 chunks
- **Average Concept Coverage**: Percentage of expected concepts found in retrieved chunks
- **Average Answer Confidence**: Average confidence score (1-5) from answer evaluation

### Comparing Runs

The RAG Evaluation Dashboard supports regression detection:

1. Select a **baseline run** (earlier evaluation)
2. Select a **current run** (later evaluation)
3. Click **"Compare Runs"** to see:
   - Metric changes (improvements, regressions, stable)
   - Per-requirement changes
   - Overall assessment

This helps track system performance over time and identify regressions.

### Notes

- **Safe to run multiple times**: Each run generates a new artifact with a unique timestamp
- **Deterministic**: Same configuration and data produce the same results
- **No UI modification**: The UI is read-only and does not execute evaluations
- **Artifact persistence**: All evaluation runs are saved as JSON files in `evaluation/runs/`

## Tips

### For Q&A Mode
- **Be specific**: More specific questions get better answers
- **Use citations**: Check cited chunks to verify information
- **Practice regularly**: Use weakness tracking to focus study
- **Try different modes**: Each mode has different strengths
- **Review context**: Understanding what knowledge is available helps frame questions

### For Interview Simulator
- **Answer honestly**: The system evaluates based on what you know, not what you guess
- **Request teaching when stuck**: Don't hesitate to use teaching options
- **Review missed concepts**: These are automatically tracked for you
- **Use focus areas**: Narrow down practice to specific topics
- **Check progress regularly**: Monitor your improvement over time
- **End sessions thoughtfully**: Review summaries to plan next practice session
