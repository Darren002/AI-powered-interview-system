"""
Enhanced LLM Evaluator (Layer 2)
Purpose: High-quality evaluation using advanced prompts
Weight: 75% of final score
"""

import json
import re
import os
import requests
from typing import Dict, List, Optional

# Import prompts module for few-shot learning
from prompts import generate_ultimate_prompt


# ==========================================
# EVALUATION CRITERIA DEFINITIONS
# ==========================================

EVALUATION_RUBRIC = {
    5: {
        "label": "Excellent",
        "description": "Exceptional response demonstrating deep expertise",
        "criteria": [
            "Complete STAR structure with compelling narrative",
            "Specific, quantifiable results with business impact",
            "Demonstrates advanced cybersecurity knowledge",
            "Shows leadership, initiative, and problem-solving",
            "Would confidently hire this candidate"
        ]
    },
    4: {
        "label": "Good",
        "description": "Strong response showing competence",
        "criteria": [
            "Clear STAR structure with relevant details",
            "Some quantifiable outcomes",
            "Good cybersecurity understanding",
            "Shows ownership and accountability",
            "Would consider for next round"
        ]
    },
    3: {
        "label": "Average",
        "description": "Adequate but not memorable",
        "criteria": [
            "Basic STAR structure present",
            "General outcomes without specifics",
            "Adequate technical knowledge",
            "Some personal contribution unclear",
            "May advance but needs stronger responses"
        ]
    },
    2: {
        "label": "Below Average",
        "description": "Weak response lacking depth",
        "criteria": [
            "Incomplete STAR structure",
            "Vague outcomes, no metrics",
            "Limited technical depth",
            "Heavy use of 'we' instead of 'I'",
            "Would not advance without improvement"
        ]
    },
    1: {
        "label": "Poor",
        "description": "Does not demonstrate competency",
        "criteria": [
            "No clear STAR structure",
            "No relevant experience shown",
            "Generic or off-topic response",
            "No personal accountability",
            "Would not hire"
        ]
    }
}


# ==========================================
# SKILL-SPECIFIC EVALUATION CRITERIA
# ==========================================

SKILL_CRITERIA = {
    "communication": {
        "focus_areas": [
            "Ability to translate technical concepts for non-technical audiences",
            "Stakeholder management and influence",
            "Clarity and structure of communication",
            "Handling resistance or pushback",
            "Achieving buy-in through data/persuasion"
        ],
        "positive_indicators": [
            "tailored message to audience",
            "used data/metrics to support arguments",
            "achieved stakeholder buy-in",
            "resolved conflict through communication",
            "translated technical jargon to business terms"
        ],
        "red_flags": [
            "overly technical for audience",
            "no mention of stakeholder reaction",
            "communication failed to achieve goal",
            "defensive or blaming tone"
        ]
    },
    
    "leadership": {
        "focus_areas": [
            "Team motivation and morale building",
            "Leading without direct authority",
            "Mentorship and development of others",
            "Decision-making under pressure",
            "Building and sustaining culture"
        ],
        "positive_indicators": [
            "inspired or motivated team",
            "took ownership of outcomes",
            "developed or mentored others",
            "led through influence not authority",
            "built sustainable processes"
        ],
        "red_flags": [
            "took credit for team's work",
            "blamed others for failures",
            "no evidence of developing others",
            "autocratic leadership style"
        ]
    },
    
    "decision_making": {
        "focus_areas": [
            "Risk assessment and analysis",
            "Balancing competing priorities",
            "Decision-making under uncertainty",
            "Stakeholder consultation",
            "Accountability for outcomes"
        ],
        "positive_indicators": [
            "weighed multiple options",
            "consulted relevant stakeholders",
            "documented risk acceptance",
            "made timely decision under pressure",
            "learned from decision outcome"
        ],
        "red_flags": [
            "no clear rationale for decision",
            "avoided making decision",
            "ignored stakeholder input",
            "no accountability for result"
        ]
    },
    
    "critical_thinking": {
        "focus_areas": [
            "Root cause analysis",
            "Pattern recognition and anomaly detection",
            "Questioning assumptions",
            "Data-driven investigation",
            "Systemic vs symptomatic thinking"
        ],
        "positive_indicators": [
            "dug deeper than surface level",
            "challenged assumptions",
            "found root cause not symptoms",
            "used data to validate hypothesis",
            "identified systemic issues"
        ],
        "red_flags": [
            "accepted things at face value",
            "did not investigate thoroughly",
            "jumped to conclusions",
            "no evidence of analytical thinking"
        ]
    }
}


# ==========================================
# ENHANCED LLM PROMPT GENERATOR
# ==========================================

def generate_evaluation_prompt(response: str, skill: str, question: str) -> str:
    """Generate enhanced evaluation prompt with specific instructions"""
    
    skill_lower = skill.lower().replace(" ", "_")
    skill_criteria = SKILL_CRITERIA.get(skill_lower, SKILL_CRITERIA["communication"])
    
    prompt = f"""You are a senior cybersecurity talent acquisition manager with 15+ years of experience recruiting for CISO, Security Director, and Security Architect roles at Fortune 500 companies.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an AI pre-screening assessment tool for HR teams. This is NOT a live interview.
You are providing WRITTEN EVALUATION for HR to decide whether to advance candidates.
You CANNOT ask follow-up questions. This is a one-time assessment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVALUATION TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Evaluate this {skill.upper().replace('_', ' ')} behavioral interview response.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{response}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORING RUBRIC (1-5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5 = EXCEPTIONAL: Complete STAR, specific metrics, deep expertise, real experience
4 = STRONG: Clear STAR, some metrics, good knowledge, shows ownership
3 = ADEQUATE: Basic STAR, general outcomes, some vagueness
2 = WEAK: Incomplete STAR, no metrics, heavy "we", generic
1 = POOR: No STAR, generic/hypothetical, no competency shown

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY EVALUATION REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. QUOTE EXACT PHRASES
   ✓ DO: "You demonstrated stakeholder management: 'I created tailored guidance for each group'"
   ✗ DON'T: "You showed good communication skills"

2. GIVE CONCRETE EXAMPLES (NOT GENERIC)
   ✓ DO: "Add specific metrics: 'Phishing reports increased from 12/month to 180/month (1400%), click-rate dropped from 18% to 3% within 60 days'"
   ✗ DON'T: "Provide more specific metrics"

3. EXPLAIN WHY IT MATTERS
   ✓ DO: "Quantified results demonstrate ROI to executives - critical for CISOs who must justify security budgets"
   ✗ DON'T: "This would strengthen your response"

4. CHECK FOR RED FLAGS
   • Heavy "we" instead of "I" (unclear contribution)
   • No specific tools/technologies/metrics
   • Generic scenario (could apply to any industry)
   • Suspiciously perfect (no challenges)
   • Very brief (< 100 words)

5. ASSESS AUTHENTICITY
   Does this sound like real experience or a template?
   What evidence supports your assessment?

6. USE PROFESSIONAL TONE
   ✗ NO: "Great job!", "I appreciate...", "Can you tell me more..."
   ✓ YES: "Demonstrates competency", "Recommendation: Hire", "Next steps:"

You are providing WRITTEN EVALUATION for HR review, NOT having a conversation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL-SPECIFIC CRITERIA FOR {skill.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Focus Areas:
{chr(10).join(f"- {area}" for area in skill_criteria['focus_areas'])}

Positive Indicators:
{chr(10).join(f"- {ind}" for ind in skill_criteria['positive_indicators'])}

Red Flags:
{chr(10).join(f"- {flag}" for flag in skill_criteria['red_flags'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RETURN JSON FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no code blocks):

{{
  "overall_score": 1-5,
  "star_breakdown": {{
    "situation": 1-5,
    "task": 1-5,
    "action": 1-5,
    "result": 1-5
  }},
  "strengths": ["strength 1 with quote and why it matters", "strength 2..."],
  "improvements": ["improvement 1 with CURRENT/ADD/WHY", "improvement 2..."],
  "positive_indicators": ["indicator 1", "indicator 2"],
  "red_flags": ["flag 1 if detected", "flag 2..."],
  "hiring_recommendation": "Strong Hire / Hire / Maybe / Pass",
  "authenticity_check": {{
    "seems_real": true/false,
    "evidence": "reasoning based on specificity and details"
  }},
  "next_steps_for_hr": ["step 1", "step 2"],
  "summary": "1-2 sentence overall assessment for HR",
  "personalized_feedback": {{
    "what_went_well": "Detailed explanation with quotes",
    "what_to_improve": "Specific improvements with concrete examples",
    "interviewer_perspective": "PROFESSIONAL assessment for HR (NO fake interview conversation)"
  }},
  "strengths_evidence": [
    {{
      "quote": "exact phrase from their answer",
      "why_good": "why this is strong"
    }}
  ],
  "improvements_evidence": [
    {{
      "improvement": "what's missing",
      "how_to_fix": "CONCRETE example: 'Add: Reduced incidents 40% in 6 months'"
    }}
  ]
}}

BE SPECIFIC. QUOTE THEIR WORDS. GIVE CONCRETE EXAMPLES. EXPLAIN WHY. DETECT BS. HELP HR DECIDE.
"""
    
    return prompt


# ==========================================
# LLM API CALL WITH RETRY
# ==========================================

def call_llm_api(prompt: str, max_retries: int = 3) -> Optional[Dict]:
    """Call LLM API with retry logic"""
    
    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment")
        return None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 3500,
                    "top_p": 0.9,
                    "frequency_penalty": 0.2
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return parse_llm_response(content)
            elif response.status_code == 429:  # Rate limit
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                print(f"API error: {response.status_code} - {response.text[:200]}")
                break
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    
    return None


def parse_llm_response(content: str) -> Dict:
    """Parse JSON from LLM response"""
    
    # Try direct parse first
    try:
        return json.loads(content)
    except:
        pass
    
    # Try to extract JSON from response
    json_patterns = [
        r'\{[\s\S]*\}',  # Anything between { }
        r'```json\s*([\s\S]*?)\s*```',  # JSON in code block
        r'```\s*([\s\S]*?)\s*```',  # Any code block
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, content)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except:
                continue
    
    # Return default if parsing fails
    return {
        "overall_score": 3,
        "error": "Could not parse LLM response",
        "raw_content": content[:500]
    }


# ==========================================
# MAIN EVALUATION FUNCTION
# ==========================================

def enhanced_llm_evaluate(response: str, skill: str, question: str = "", features: dict = None) -> Dict:
    """
    Enhanced LLM evaluation for Layer 2
    
    Args:
        response: Candidate's response text
        skill: The competency being evaluated
        question: The interview question asked
    
    Returns:
        Dict with score, breakdown, strengths, improvements
    """
    
    # ========== FIX 3: FILTER NON-ANSWERS ==========
    # Hard filter for non-answers and junk responses
    response_lower = response.strip().lower()
    response_words = response.split()
    
    # List of explicit non-answers
    non_answers = [
        'idk', 'i dont know', 'i don\'t know', 'i do not know',
        'no idea', 'skip', 'pass', 'none', 'n/a', 'na',
        'not sure', 'dunno', 'whatever', ''
    ]
    
    # Check for non-answers
    if response_lower in non_answers:
        return {
            'score': 0,
            'star_breakdown': {'situation': 0, 'task': 0, 'action': 0, 'result': 0},
            'technical_accuracy': 0,
            'relevance': 0,
            'communication_quality': 0,
            'strengths': [],
            'improvements': ['A proper STAR response is required. No competency demonstrated.'],
            'positive_indicators': [],
            'red_flags': ['Non-answer response', 'Did not attempt to answer question'],
            'hiring_recommendation': 'No',
            'summary': 'Candidate did not provide a valid response',
            'authenticity': {'seems_real': False, 'evidence': 'No attempt to answer'},
            'next_steps': ['Candidate did not demonstrate competency in this area'],
            'personalized_feedback': {
                'what_went_well': 'N/A - no valid response provided',
                'what_to_improve': 'Provide a complete STAR response with specific examples',
                'interviewer_perspective': 'No competency demonstrated'
            },
            'error': False,
            'confidence': 1.0
        }
    
    # Check for extremely short responses (less than 5 words)
    if len(response_words) < 5:
        return {
            'score': 0,
            'star_breakdown': {'situation': 0, 'task': 0, 'action': 0, 'result': 0},
            'technical_accuracy': 0,
            'relevance': 0,
            'communication_quality': 0,
            'strengths': [],
            'improvements': ['Response is too brief. A complete STAR response is required.'],
            'positive_indicators': [],
            'red_flags': ['Extremely brief response', 'Insufficient detail to evaluate'],
            'hiring_recommendation': 'No',
            'summary': 'Response too brief to evaluate competency',
            'authenticity': {'seems_real': False, 'evidence': 'Response lacks sufficient content'},
            'next_steps': ['Candidate needs to provide detailed behavioral examples'],
            'personalized_feedback': {
                'what_went_well': 'N/A - response too brief',
                'what_to_improve': 'Provide detailed response with specific situation, actions, and results',
                'interviewer_perspective': 'Unable to assess competency from brief response'
            },
            'error': False,
            'confidence': 1.0
        }
    # ========== END FIX 3 ==========
    
    # Generate ultimate prompt with few-shot examples
    prompt = generate_ultimate_prompt(response, skill, question, features)
    
    # Call LLM
    llm_result = call_llm_api(prompt)
    
    if llm_result is None or llm_result.get('error'):
        # Fallback to simple evaluation
        return simple_evaluation(response, skill)
    
    # Extract and structure results
    personalized = llm_result.get('personalized_feedback', {})
    authenticity = llm_result.get('authenticity_check', {})
    
    result = {
        'score': llm_result.get('overall_score', 3),
        'star_breakdown': llm_result.get('star_breakdown', {}),
        'technical_accuracy': llm_result.get('technical_accuracy', 3),
        'relevance': llm_result.get('relevance', 3),
        'communication_quality': llm_result.get('communication_quality', 3),
        'strengths': llm_result.get('strengths', [])[:5],
        'improvements': llm_result.get('improvements', [])[:5],
        'positive_indicators': llm_result.get('positive_indicators_found', []),
        'red_flags': llm_result.get('red_flags', []),
        'hiring_recommendation': llm_result.get('hiring_recommendation', 'Maybe'),
        'summary': llm_result.get('summary', ''),
        
        # NEW: Authenticity check
        'authenticity': {
            'seems_real': authenticity.get('seems_real', True),
            'evidence': authenticity.get('evidence', 'Unable to assess')
        },
        
        # NEW: Next steps for HR
        'next_steps': llm_result.get('next_steps', []),
        
        # NEW: Personalized feedback fields
        'personalized_feedback': {
            'what_went_well': personalized.get('what_went_well', ''),
            'what_to_improve': personalized.get('what_to_improve', ''),
            'specific_quote': personalized.get('specific_quote', ''),
            'interviewer_perspective': personalized.get('interviewer_perspective', ''),
        },
        
        # NEW: STAR analysis
        'star_analysis': llm_result.get('star_analysis', {}),
        
        # NEW: Detailed evidence
        'strengths_evidence': llm_result.get('strengths_evidence', []),
        'improvements_evidence': llm_result.get('improvements_evidence', []),
        
        'error': False
    }
    
    # Calculate confidence based on score distribution
    star_scores = list(result['star_breakdown'].values()) if result['star_breakdown'] else [3]
    score_variance = max(star_scores) - min(star_scores) if len(star_scores) > 1 else 0
    result['confidence'] = max(0.5, 1.0 - (score_variance * 0.1))
    
    return result


def simple_evaluation(response: str, skill: str, question: str = "") -> Dict:
    """Fallback evaluation when LLM unavailable - generates basic analysis"""
    
    word_count = len(response.split())
    response_lower = response.lower()
    
    # Basic scoring
    score = 2
    
    # Word count factors
    if word_count >= 100:
        score += 0.5
    if word_count >= 200:
        score += 0.5
    if word_count >= 300:
        score += 0.5
    
    # Personal ownership
    i_count = response.count(' I ')
    we_count = response.count(' we ')
    if i_count > we_count:
        score += 0.5
    elif we_count > i_count * 2:
        score -= 0.5
    
    # Specificity indicators
    has_metrics = any(c in response for c in ['%', '$', '/', 'hours', 'days', 'weeks', 'months', 'years'])
    has_tools = any(t in response_lower for t in ['tool', 'system', 'software', 'platform', 'framework', 'cve', 'cvss', 'siem', 'firewall', 'ids', 'ips'])
    has_outcome = any(w in response_lower for w in ['result', 'outcome', 'achieved', 'reduced', 'increased', 'improved', 'prevented'])
    
    if has_metrics:
        score += 0.5
    if has_tools:
        score += 0.5
    if has_outcome:
        score += 0.5
    
    score = min(5, max(1, score))
    
    # Generate basic analysis
    strengths = []
    improvements = []
    red_flags = []
    
    # Analyze STAR structure
    has_situation = any(w in response_lower for w in ['when', 'during', 'at', 'in my role', 'previous', 'project'])
    has_task = any(w in response_lower for w in ['my task', 'my responsibility', 'i needed', 'i had to', 'goal was'])
    has_action = any(w in response_lower for w in ['i created', 'i developed', 'i implemented', 'i led', 'i did', 'i analyzed', 'i conducted'])
    has_result = any(w in response_lower for w in ['result', 'outcome', 'achieved', 'as a result', 'therefore'])
    
    if has_situation and has_task and has_action and has_result:
        strengths.append("Complete STAR structure present")
    elif has_situation and has_action:
        strengths.append("Clear STAR structure with situation and action")
    else:
        improvements.append("Add more complete STAR structure with clear situation, task, action, and result")
    
    # Personal ownership
    if i_count > we_count:
        strengths.append(f"Demonstrates personal ownership ({i_count} 'I' vs {we_count} 'we')")
    elif we_count > i_count:
        red_flags.append(f"Heavy 'we' usage ({we_count} vs {i_count} 'I') - unclear personal contribution")
    
    # Specificity
    if not has_metrics:
        improvements.append("Add specific metrics and numbers to demonstrate impact")
    if not has_tools:
        improvements.append("Mention specific tools, technologies, or frameworks used")
    
    # Generic language
    generic_phrases = ['some issues', 'some problems', 'a situation', 'one time', 'things', 'stuff']
    for phrase in generic_phrases:
        if phrase in response_lower:
            improvements.append(f"Replace generic language '{phrase}' with specific details")
            break
    
    score_label = "Exceptional" if score >= 4.5 else "Strong" if score >= 3.5 else "Adequate" if score >= 2.5 else "Basic" if score >= 1.5 else "Needs Development"
    
    return {
        'score': round(score, 1),
        'star_breakdown': {
            'situation': 3 if has_situation else 2,
            'task': 3 if has_task else 2,
            'action': 3 if has_action else 2,
            'result': 3 if has_result else 2
        },
        'strengths': strengths if strengths else ["Response provided"],
        'improvements': improvements if improvements else ["Consider adding more specific metrics and outcomes"],
        'positive_indicators': [],
        'red_flags': red_flags,
        'hiring_recommendation': 'Hire' if score >= 3 else 'Maybe',
        'summary': f'{score_label} response with {"some" if strengths else "limited"} specific details. {"Good STAR structure" if has_situation and has_action else "Needs better STAR structure"}.',
        'personalized_feedback': {
            'what_went_well': f'Shows {word_count} words with {"good specificity" if has_metrics else "limited metrics"}.',
            'what_to_improve': ' '.join(improvements[:2]) if improvements else 'Add more specific metrics and outcomes.',
            'interviewer_perspective': f'Adequate {"demonstration" if score >= 3 else "attempt"} of {skill.replace("_", " ")} competency.'
        },
        'authenticity_check': {
            'seems_real': score >= 2.5,
            'evidence': f'{"Specific details present" if has_metrics else "Lacks specific details"}. {"Clear personal ownership" if i_count > we_count else "Heavy team focus, unclear individual contribution"}.'
        },
        'error': False,
        'confidence': 0.6
    }


# ==========================================
# TEST FUNCTION
# ==========================================

def test_enhanced_llm():
    """Test the enhanced LLM evaluator"""
    
    print("=" * 60)
    print("Testing Enhanced LLM Evaluator (Layer 2)")
    print("=" * 60)
    
    test_response = """During a routine vulnerability scan, I discovered a critical SQL injection 
    vulnerability in our production e-commerce platform two weeks before Black Friday. The CTO 
    and VP of Sales were pushing back against any downtime, arguing the risk was minimal since 
    no breach had occurred.
    
    As the Security Architect, I needed to communicate the severity to non-technical executives 
    in a way that would help them understand the business risk. My goal was to get buy-in for 
    emergency patching while respecting their business concerns.
    
    I created an executive dashboard that translated technical risk into business impact. I used 
    CVSS scores combined with EPSS to show 78% likelihood of exploitation in the next 30 days. 
    I quantified potential impact as $500,000 per hour of downtime plus $2M in PCI-DSS fines. 
    I presented three remediation options with trade-offs: immediate patch, virtual patching via 
    WAF, or risk acceptance. I framed the conversation around business continuity, not security 
    compliance.
    
    The executives approved emergency patching. We deployed with minimal disruption, zero 
    incidents. This led to establishing monthly risk reviews and a 30% security budget increase."""
    
    result = enhanced_llm_evaluate(
        response=test_response,
        skill="communication",
        question="Describe a time when you had to communicate a critical security vulnerability to non-technical executives who wanted to delay patching."
    )
    
    print(f"\n Overall Score: {result['score']}/5")
    print(f" Confidence: {result.get('confidence', 0) * 100:.0f}%")
    print(f" Hiring Recommendation: {result.get('hiring_recommendation', 'N/A')}")
    
    if result.get('star_breakdown'):
        print(f"\nSTAR Breakdown:")
        for component, score in result['star_breakdown'].items():
            print(f"  - {component.title()}: {score}/5")
    
    if result.get('strengths'):
        print(f"\n Strengths:")
        for s in result['strengths'][:3]:
            print(f"  + {s}")
    
    if result.get('improvements'):
        print(f"\n Improvements:")
        for i in result['improvements'][:3]:
            print(f"  - {i}")
    
    if result.get('positive_indicators'):
        print(f"\n Positive Indicators Found:")
        for p in result['positive_indicators'][:3]:
            print(f"  ✓ {p}")
    
    if result.get('red_flags'):
        print(f"\n Red Flags:")
        for r in result['red_flags']:
            print(f"  - {r}")
    
    if result.get('authenticity'):
        auth = result['authenticity']
        print(f"\n Authenticity: {auth.get('seems_real', 'Unknown')}")
        print(f"  Evidence: {auth.get('evidence', 'N/A')}")
    
    if result.get('next_steps'):
        print(f"\n Next Steps for HR:")
        for step in result['next_steps']:
            print(f"  - {step}")
    
    print(f"\n Summary: {result.get('summary', 'N/A')}")


# ==========================================
# PERSONALIZED FEEDBACK GENERATOR
# ==========================================

def generate_personalized_feedback(evaluation_result: Dict, skill: str) -> str:
    """
    Generate highly personalized, detailed feedback based on evaluation.
    
    This creates feedback that:
    - Quotes specific words from candidate's response
    - Explains WHY those words demonstrate the skill (or lack thereof)
    - Provides specific, actionable improvement suggestions
    """
    
    pf = evaluation_result.get('personalized_feedback', {})
    star = evaluation_result.get('star_breakdown', {})
    strengths = evaluation_result.get('strengths', [])
    improvements = evaluation_result.get('improvements', [])
    strengths_evidence = evaluation_result.get('strengths_evidence', [])
    improvements_evidence = evaluation_result.get('improvements_evidence', [])
    
    score = evaluation_result.get('score', 0)
    percentage = (score / 5) * 100
    
    # Build the feedback message
    feedback = []
    
    # Header with score
    if score >= 4:
        feedback.append("EXCELLENT RESPONSE")
    elif score >= 3:
        feedback.append("GOOD RESPONSE")
    elif score >= 2:
        feedback.append("NEEDS IMPROVEMENT")
    else:
        feedback.append("BELOW EXPECTATIONS")
    
    feedback.append(f"Score: {score}/5 ({percentage:.0f}%) for {skill.replace('_', ' ').title()}\n")
    
    # Personalized "What Went Well" with quotes
    if pf.get('what_went_well'):
        feedback.append("WHAT YOU DID WELL:")
        feedback.append(f"{pf['what_went_well']}\n")
    
    # Add specific quotes if available
    if strengths_evidence:
        feedback.append("EVIDENCE FROM YOUR RESPONSE:")
        for evidence in strengths_evidence[:2]:
            if evidence.get('quote'):
                feedback.append(f'"{evidence["quote"]}"')
                feedback.append(f"   This shows: {evidence.get('why_good', '')}")
        feedback.append("")
    
    # Personalized "What to Improve" 
    if pf.get('what_to_improve'):
        feedback.append("AREAS TO IMPROVE:")
        feedback.append(f"{pf['what_to_improve']}\n")
    
    # Add specific improvement suggestions
    if improvements_evidence:
        feedback.append("SPECIFIC IMPROVEMENTS:")
        for evidence in improvements_evidence[:2]:
            improvement = evidence.get('improvement', '')
            how_to = evidence.get('how_to_fix', '')
            if improvement or how_to:
                feedback.append(f"- {improvement}: {how_to}")
        feedback.append("")
    
    # STAR Analysis
    if star:
        feedback.append("STAR BREAKDOWN:")
        star_map = {
            'situation': 'Situation (Context)',
            'task': 'Task (Your Responsibility)',
            'action': 'Action (What YOU Did)',
            'result': 'Result (Outcomes)'
        }
        for key, label in star_map.items():
            score_val = star.get(key, 0)
            bars = "=" * score_val + "-" * (5 - score_val)
            feedback.append(f"   {label}: {bars} {score_val}/5")
    
    # Professional HR recommendation (NOT fake interview)
    if pf.get('interviewer_perspective'):
        perspective = pf['interviewer_perspective']
        if not any(phrase in perspective.lower() for phrase in ['i appreciate', 'can you tell', 'tell me more', 'great job', 'nice', 'good job']):
            feedback.append(f"\nHiring Recommendation:")
            feedback.append(f"{perspective}")
    
    # Closing
    if score >= 4:
        feedback.append("\nThis response demonstrates strong competency.")
    elif score >= 3:
        feedback.append("\nSolid response. With some refinement, you can make it excellent.")
    else:
        feedback.append("\nFocus on the specific suggestions above to strengthen your response.")
    
    return "\n".join(feedback)


if __name__ == "__main__":
    test_enhanced_llm()