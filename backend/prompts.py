# backend/prompts.py
"""
Prompt generation module with few-shot learning examples.
INTELLIGENT VERSION - Cybersecurity domain expertise, adaptive feedback
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

# Path to few-shot examples
BASE_DIR = Path(__file__).resolve().parent.parent
FEW_SHOT_PATH = BASE_DIR / "data" / "few_shot_examples.json"

# Cache for loaded examples
_cached_examples: Optional[Dict] = None


def load_few_shot_examples() -> Optional[Dict]:
    """Load few-shot examples from JSON file."""
    global _cached_examples
    
    if _cached_examples is not None:
        return _cached_examples
    
    if not FEW_SHOT_PATH.exists():
        print(f"Warning: Few-shot examples file not found at {FEW_SHOT_PATH}")
        _cached_examples = {}
        return _cached_examples
    
    with open(FEW_SHOT_PATH, 'r', encoding='utf-8') as f:
        _cached_examples = json.load(f)
    
    return _cached_examples


def get_few_shot_example(skill: str) -> Optional[Dict]:
    """Get the few-shot example for a specific skill."""
    examples = load_few_shot_examples()
    if not examples:
        return None
    
    skill_lower = skill.lower().replace(" ", "_").replace("-", "_")
    
    if skill_lower in examples:
        return examples[skill_lower]
    
    skill_clean = skill_lower.replace("_", "")
    for key in examples:
        if key.replace("_", "") == skill_clean:
            return examples[key]
    
    return None


def format_example_as_text(example: Dict, skill: str) -> str:
    """Format a few-shot example as text for the prompt."""
    answer = example.get('example_answer', '')
    evaluation = example.get('evaluation', {})
    
    overall_score = evaluation.get('overall_score', 5)
    star = evaluation.get('star_breakdown', {})
    strengths = evaluation.get('strengths', [])
    improvements = evaluation.get('improvements', [])
    authenticity = evaluation.get('authenticity_check', {})
    recommendation = evaluation.get('hiring_recommendation', 'Hire')
    next_steps = evaluation.get('next_steps_for_hr', [])
    summary = evaluation.get('summary', '')
    
    strengths_text = ""
    for s in strengths:
        strengths_text += f"""    - {s.get('title', '')}: "{s.get('quote', '')}" - {s.get('explanation', '')}
"""
    
    improvements_text = ""
    for imp in improvements:
        improvements_text += f"""    - {imp.get('issue', '')}: {imp.get('how_to_fix', '')}
"""
    if not improvements_text:
        improvements_text = "    (None - this is an excellent response)\n"
    
    red_flags = evaluation.get('red_flags', [])
    red_flags_text = "\n".join([f"    - {r}" for r in red_flags]) if red_flags else "    (None detected)"
    
    next_steps_text = "\n".join([f"    - {step}" for step in next_steps]) if next_steps else "    (None)"
    
    formatted = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE EVALUATION (Score: {overall_score}/5 - {skill})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CANDIDATE ANSWER:
{answer}

EXCELLENT EVALUATION:

STAR Breakdown:
    Situation: {star.get('situation', 5)}/5
    Task: {star.get('task', 5)}/5
    Action: {star.get('action', 5)}/5
    Result: {star.get('result', 5)}/5

Strengths:
{strengths_text}
Improvements:
{improvements_text}
Red Flags:
{red_flags_text}

Authenticity Assessment: {authenticity.get('seems_real', True)}
Evidence: {authenticity.get('evidence', 'N/A')}

Recommendation: {recommendation}

Next Steps for HR:
{next_steps_text}

Summary: {summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOW EVALUATE THE FOLLOWING CANDIDATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return formatted


def generate_ultimate_prompt(response: str, skill: str, question: str, features: dict = None) -> str:
    """Final optimized prompt with adaptive, explainable, non-template feedback."""
    
    skill_clean = skill.upper().replace("_", " ")

    # Optional feature signals (for adaptive feedback)
    feature_signals = ""
    if features:
        feature_signals = f"""
FEATURE SIGNALS (for internal reasoning ONLY - do not mention directly):
- Word count: {features.get('word_count', 0)}
- STAR completeness: {features.get('star_component_count', 0)}/4
- Technical indicators: {features.get('cyber_term_count', 0)}
- Leadership indicators: {features.get('leadership_indicators', 0)}
- Vagueness score: {features.get('vagueness', 'N/A')}
"""

    prompt = f"""
You are a senior cybersecurity hiring manager with 15+ years of experience evaluating candidates for leadership roles (Security Lead, Architect, CISO track).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an AI-assisted pre-screening system for HR.
You are NOT having a conversation. You are producing a structured evaluation report.

You must behave like a STRICT and SKEPTICAL evaluator:
- Prioritize evidence over claims
- Penalize vague answers
- Reward specific technical reasoning
- Do NOT assume competence unless demonstrated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Evaluate this {skill_clean} behavioral interview response.

QUESTION:
{question}

CANDIDATE ANSWER:
{response}

{feature_signals}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVALUATION FRAMEWORK (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

First, internally classify the response gaps into ONE or TWO of these categories:

1. Technical Depth Gap (missing tools, frameworks, methods)
2. Decision Reasoning Gap (what was done but not why)
3. Impact Gap (no measurable or observable outcome)
4. Communication Gap (unclear explanation or structure)

⚠️ Only select the MOST important gaps (max 2). Do NOT list everything.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO WRITE FEEDBACK (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write like a real senior cybersecurity interviewer giving evaluation notes.

Your feedback must feel:
- specific to this exact answer
- grounded in what the candidate actually said
- varied in tone and structure (NOT repetitive)

For each improvement:

• Reference a specific part of the candidate’s answer  
• Clearly explain what is missing or weak  
• Suggest how it could be improved in a realistic way  
• Explain why this matters in a real-world cybersecurity context  

⚠️ IMPORTANT:
- Do NOT follow a rigid template for every point
- Do NOT repeat the same sentence structure
- Do NOT always suggest frameworks unless clearly relevant
- Only suggest frameworks if the candidate’s scenario naturally requires them. Avoid forcing cybersecurity frameworks into every answer.
- Do NOT default to generic advice like "add more detail"

Instead, vary your phrasing naturally. Examples of acceptable styles:

• Analytical:
  "This response identifies the issue but doesn’t explain how the risk was actually assessed..."

• Technical:
  "There’s no indication of what tools or controls were used to validate or mitigate the vulnerability..."

• Strategic:
  "The decision-making process is implied but not clearly articulated, particularly how trade-offs were evaluated..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEATURE UTILIZATION (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You MUST explicitly reflect feature signals in your feedback. If structure is weak, mention missing structure. If technical depth is low, highlight lack of technical detail. Do not ignore these signals.
You MUST use the provided feature signals to guide your evaluation.

- If STAR completeness is low → explicitly mention missing components  
- If technical indicators are low → highlight lack of technical depth  
- If vagueness is high → point out unclear or generic phrasing  

Do NOT mention raw numbers directly (e.g., "2/4"), but reflect them naturally:

Example:
❌ "STAR completeness is 2/4"
✅ "The response outlines the situation and actions but lacks a clearly defined result"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANTI-TEMPLATE ENFORCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before finalizing your response, check:

- Are all improvements written in the same structure? → If yes, rewrite
- Are suggestions repetitive across points? → If yes, diversify
- Does the feedback sound generic? → If yes, make it more specific

Your goal is to produce feedback that feels like it was written by a human expert, not generated from a template.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CYBERSECURITY SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strong indicators:
- Mentions frameworks (MITRE ATT&CK, NIST)
- Uses risk thinking (likelihood × impact)
- References tools (SIEM, EDR, etc.)
- Shows structured incident handling

Weak indicators:
- Vague language ("handled issue")
- No technical grounding
- No explanation of decisions
- No outcome clarity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORING (1–5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5 = Exceptional (deep reasoning, strong technical clarity)
4 = Strong (good structure, some depth)
3 = Adequate (basic but lacks depth)
2 = Weak (generic, limited detail)
1 = Poor (no meaningful competency)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (STRICT JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON:

{{
  "overall_score": 1-5,
  "star_breakdown": {{
    "situation": 1-5,
    "task": 1-5,
    "action": 1-5,
    "result": 1-5
  }},
  "strengths": [
    "Quote: '...' - explanation"
  ],
  "improvements": [
  "Specific, contextual improvement based on the candidate's response, clearly explaining what is missing, how to improve it, and why it matters."
]
  "red_flags": ["..."],
  "authenticity_check": {{
    "seems_real": true/false,
    "evidence": "..."
  }},
  "hiring_recommendation": "Strong Hire / Hire / Maybe / No",
  "summary": "Concise expert evaluation"
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before responding, ensure:

- Feedback is specific to THIS answer (not generic)
- Improvements are realistic and domain-relevant
- No repeated phrasing patterns
- Suggestions reflect senior-level expectations
- Output is fully consistent with evaluation

"""

    return prompt


if __name__ == "__main__":
    examples = load_few_shot_examples()
    if examples:
        print(f"Loaded {len(examples)} few-shot examples")
        print(f"Skills: {list(examples.keys())}")
    else:
        print("No few-shot examples loaded")
    
    test_prompt = generate_ultimate_prompt(
        response="Test response",
        skill="communication",
        question="Tell me about a time you communicated security risk."
    )
    print(f"\nPrompt length: {len(test_prompt)} characters")
    print(f"Contains example: {'EXAMPLE EVALUATION' in test_prompt}")