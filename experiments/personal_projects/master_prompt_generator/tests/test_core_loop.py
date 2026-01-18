"""
Simple test script to verify the core generation loop works.

This demonstrates the end-to-end workflow:
Generate → Evaluate → (Refine) → Approve
"""

import os
from dotenv import load_dotenv
from core import PromptOrchestrator

# Load environment variables
load_dotenv()

def test_core_loop():
    """Test the complete prompt generation loop."""
    print("=" * 60)
    print("Testing Master Prompt Generator - Core Loop")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = PromptOrchestrator(
        quality_threshold=7.5,  # Lower threshold for testing
        max_refinement_iterations=2
    )
    
    # Test case: Simple email writing prompt
    print("\n1. Generating prompt...")
    final_prompt, version_history, evaluation_history = orchestrator.generate_and_approve(
        use_case="Write a professional follow-up email after a client meeting",
        category="business",
        complexity_tier=2,
        context="The meeting discussed project timeline and deliverables. Need to follow up with action items.",
        requirements=[
            "Professional tone",
            "Include action items",
            "Request confirmation"
        ],
        target_model="claude-sonnet-4-5-20250929",
        auto_approve=True
    )
    
    print(f"\n2. Generation complete!")
    print(f"   Versions created: {len(version_history)}")
    print(f"   Evaluations performed: {len(evaluation_history)}")
    print(f"   Final state: {final_prompt.lifecycle_state}")
    print(f"   Final version: {final_prompt.version}")
    print(f"   Final score: {final_prompt.evaluation_score_after}/10")
    
    print(f"\n3. Version History:")
    for i, version in enumerate(version_history, 1):
        print(f"   v{version.version}: {version.lifecycle_state} "
              f"(score: {version.evaluation_score_after or 'N/A'})")
        if version.parent_prompt_id:
            print(f"      Parent: {version.parent_prompt_id[:8]}...")
    
    print(f"\n4. Final Prompt Preview:")
    print(f"   {'-' * 60}")
    print(f"   {final_prompt.full_prompt[:200]}...")
    print(f"   {'-' * 60}")
    
    print(f"\n5. Metadata Summary:")
    print(f"   - Use Case: {final_prompt.use_case}")
    print(f"   - Category: {final_prompt.category}")
    print(f"   - Complexity: Tier {final_prompt.complexity_tier}")
    print(f"   - Target Model: {final_prompt.target_model}")
    print(f"   - Input Tokens: ~{final_prompt.estimated_input_tokens}")
    print(f"   - Output Tokens: ~{final_prompt.estimated_output_tokens}")
    print(f"   - Cost ({final_prompt.target_model}): "
          f"${final_prompt.estimated_cost_per_run.get(final_prompt.target_model, 0):.4f}")
    print(f"   - Anti-patterns: {len(final_prompt.anti_patterns_detected)}")
    print(f"   - Model Adaptations: {len(final_prompt.model_adaptations_applied)}")
    
    if final_prompt.lifecycle_state == "approved":
        print(f"\n✅ SUCCESS: Prompt approved and ready for use!")
    else:
        print(f"\n⚠️  Prompt in state: {final_prompt.lifecycle_state}")
        if evaluation_history:
            last_eval = evaluation_history[-1]
            can_approve, blockers = orchestrator.approval_logic.check_approval_readiness(
                final_prompt, last_eval, version_history[0] if len(version_history) > 1 else None
            )
            if blockers:
                print(f"   Blockers: {', '.join(blockers)}")
    
    print("\n" + "=" * 60)
    return final_prompt, version_history, evaluation_history


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")
        print("   The test will fail if no model client is available.")
    
    try:
        test_core_loop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
