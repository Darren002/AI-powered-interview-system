import json
import time
import re
from typing import Dict, List
from rule_based_filter import rule_based_filter
import requests
import os
from typing import Dict, Optional
from rule_based_filter import rule_based_filter
"""
Hybrid Scorer - Three-Layer System
Layer 1 (20%): Rule-based filter
Layer 2 (75%): LLM quality check
Layer 3 (5%): Expert guide comparison
"""

# Load expert answers for Layer 3
EXPERT_ANSWERS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'expert_answers.json')

def load_expert_answers() -> Dict:
    """Load expert answers from JSON file"""
    try:
        with open(EXPERT_ANSWERS_PATH, 'r') as f:
            data = json.load(f)
            return data.get('expert_answers', {})
    except Exception as e:
        print(f"Warning: Could not load expert answers: {e}")
        return {}


# Cache for expert answers
_expert_answers_cache = None

def get_expert_answers() -> Dict:
    """Get cached expert answers"""
    global _expert_answers_cache
    if _expert_answers_cache is None:
        _expert_answers_cache = load_expert_answers()
    return _expert_answers_cache
# ==========================================
# LAYER 2: LLM Quality Check (75%) - ENHANCED
# ==========================================

def llm_quality_check(response: str, skill: str, question: str = "", features: dict = None) -> Dict:
    """
    Layer 2: Enhanced LLM evaluation
    Uses the advanced evaluator from llm_evaluator.py
    """
    
    try:
        from llm_evaluator import enhanced_llm_evaluate
        
        result = enhanced_llm_evaluate(response, skill, question, features=features)
        
        return {
            'score': result.get('score', 3),
            'feedback': result.get('summary', ''),
            'strengths': result.get('strengths', []),
            'improvements': result.get('improvements', []),
            'star_breakdown': result.get('star_breakdown', {}),
            'technical_accuracy': result.get('technical_accuracy', 3),
            'relevance': result.get('relevance', 3),
            'communication_quality': result.get('communication_quality', 3),
            'hiring_recommendation': result.get('hiring_recommendation', 'Maybe'),
            'positive_indicators': result.get('positive_indicators', []),
            'red_flags': result.get('red_flags', []),
            'confidence': result.get('confidence', 0.7),
            'error': result.get('error', False),
            
            # NEW: Personalized feedback fields
            'personalized_feedback': result.get('personalized_feedback', {}),
            'star_analysis': result.get('star_analysis', {}),
            'strengths_evidence': result.get('strengths_evidence', []),
            'improvements_evidence': result.get('improvements_evidence', []),
            
            # NEW: Next steps and authenticity
            'next_steps': result.get('next_steps', []),
            'authenticity': result.get('authenticity', {}),
        }
        
    except ImportError:
        # Fallback to basic evaluation
        print("Warning: llm_evaluator not found, using basic evaluation")
        return basic_llm_evaluation(response, skill, question)


def basic_llm_evaluation(response: str, skill: str, question: str = "") -> Dict:
    """Basic LLM evaluation fallback"""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        return {
            'score': 3,
            'feedback': "LLM evaluation unavailable",
            'strengths': [],
            'improvements': [],
            'error': True
        }
    
    # Simple prompt
    prompt = f"""Score this interview response for {skill} on a scale of 1-5.
    
Question: {question}
Response: {response}

Return JSON: {{"score": 1-5, "feedback": "brief feedback"}}"""
    
    try:
        response_api = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response_api.status_code == 200:
            content = response_api.json()['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    'score': parsed.get('score', 3),
                    'feedback': parsed.get('feedback', ''),
                    'strengths': [],
                    'improvements': [],
                    'error': False
                }
    except Exception as e:
        pass
    
    return {
        'score': 3,
        'feedback': 'Evaluation completed',
        'strengths': [],
        'improvements': [],
        'error': True
    }


# ==========================================
# LAYER 3: Expert Guide Comparison (5%) - 
# ==========================================

def expert_comparison(response: str, question_id: str) -> Dict:
    """
    Layer 3: Compare candidate response to expert answer
    Uses enhanced comparator from expert_comparator.py
    """
    
    try:
        from expert_comparator import compare_to_expert
        
        result = compare_to_expert(response, question_id)
        
        return {
            'score': result.get('score', 3),
            'similarity': result.get('similarity', 0.5),
            'matched_elements': result.get('matched_elements', []),
            'missing_elements': result.get('missing_elements', []),
            'matched_concepts': result.get('matched_concepts', []),
            'element_match_percentage': result.get('element_match_percentage', 50),
            'concept_match_percentage': result.get('concept_match_percentage', 50),
            'feedback': result.get('feedback', ''),
            'star_comparison': result.get('star_comparison', {}),
            'available': result.get('available', False)
        }
        
    except ImportError:
        print("Warning: expert_comparator not found, using basic comparison")
        return basic_expert_comparison(response, question_id)


def basic_expert_comparison(response: str, question_id: str) -> Dict:
    """Basic expert comparison fallback"""
    
    expert_answers = get_expert_answers()
    
    if question_id not in expert_answers:
        return {
            'score': 3,
            'matched_elements': [],
            'missing_elements': [],
            'reason': "No expert answer available"
        }
    
    expert = expert_answers[question_id]
    expert_elements = expert.get('key_elements', [])
    
    response_lower = response.lower()
    
    matched = []
    missing = []
    
    for element in expert_elements:
        element_keywords = element.lower().split()
        if any(keyword in response_lower for keyword in element_keywords):
            matched.append(element)
        else:
            missing.append(element)
    
    score = 1 + (len(matched) / len(expert_elements) * 4) if expert_elements else 3
    
    return {
        'score': round(score, 1),
        'matched_elements': matched,
        'missing_elements': missing,
        'available': True
    }


# ==========================================
# FINAL THREE-LAYER SCORE CALCULATION
# ==========================================

def calculate_three_layer_score(
    layer1_result: Dict,
    layer2_result: Dict, 
    layer3_result: Dict
) -> Dict:
    """
    Combine all three layers into final score
    
    Weights:
    - Layer 1 (Rule-based): 20%
    - Layer 2 (LLM): 75%
    - Layer 3 (Expert): 5%
    """
    
    # If Layer 1 disqualified, return 0 immediately
    if not layer1_result.get('pass', True):
        return {
            'final_score': 0,
            'final_score_100': 0,
            'percentage': 0,
            'passed': False,
            'disqualified': True,
            'disqualification_reason': layer1_result.get('reason', 'Did not pass basic validation'),
            'overall_feedback': 'Response disqualified - does not meet minimum standards',
            'layer_scores': {
                'layer1_rule_based': {
                    'score': 0,
                    'weight': '20%',
                    'reason': layer1_result.get('reason', 'Disqualified')
                },
                'layer2_llm': {
                    'score': 0,
                    'weight': '75%',
                    'feedback': layer2_result.get('feedback', ''),
                    'strengths': [],
                    'improvements': layer2_result.get('improvements', ['A proper STAR response is required']),
                    'red_flags': layer2_result.get('red_flags', ['Non-answer response', 'Failed basic validation'])
                },
                'layer3_expert': {
                    'score': 0,
                    'weight': '5%',
                    'matched': [],
                    'missing': []
                }
            },
            'strengths': [],
            'improvements': layer2_result.get('improvements', ['A proper STAR response is required']),
            'red_flags': layer2_result.get('red_flags', ['Non-answer response', 'Failed basic validation']),
            'hiring_recommendation': 'No'
        }
    
    # Calculate weighted scores
    layer1_score = layer1_result['score'] / 5.0  # Normalize to 0-1
    layer2_score = layer2_result['score'] / 5.0
    layer3_score = layer3_result['score'] / 5.0
    
    # Apply weights
    weighted_score = (
        (layer1_score * 0.20) +
        (layer2_score * 0.75) +
        (layer3_score * 0.05)
    )
    
    # Convert to different scales
    final_score_25 = weighted_score * 25  # 0-25 scale
    final_score_100 = weighted_score * 100  # 0-100 scale
    
    # Determine overall feedback
    if weighted_score >= 0.8:
        overall_feedback = "Excellent response demonstrating strong expertise"
    elif weighted_score >= 0.6:
        overall_feedback = "Good response with room for improvement"
    elif weighted_score >= 0.4:
        overall_feedback = "Adequate response but missing key elements"
    else:
        overall_feedback = "Response needs significant improvement"
    
    # Compile all feedback
    all_strengths = layer2_result.get('strengths', [])
    all_improvements = layer2_result.get('improvements', [])
    missing_from_expert = layer3_result.get('missing_elements', [])
    
    # FIX 1: Use ONLY LLM's intelligent feedback - no generic additions
    # Expert gaps are already shown in layer3_expert breakdown for transparency
    # if missing_from_expert:
    #     all_improvements.extend([f"Consider addressing: {elem}" for elem in missing_from_expert[:3]])
    
    return {
        'final_score': round(final_score_25, 1),
        'final_score_100': round(final_score_100, 1),
        'percentage': round(weighted_score * 100, 1),
        'passed': True,
        'disqualified': False,
        'overall_feedback': overall_feedback,
        'layer_scores': {
            'layer1_rule_based': {
                'score': layer1_result['score'],
                'weight': '20%',
                'reason': layer1_result.get('reason', '')
            },
            'layer2_llm': {
                'score': layer2_result['score'],
                'weight': '75%',
                'feedback': layer2_result.get('feedback', ''),
                # Include personalized feedback fields
                'personalized_feedback': layer2_result.get('personalized_feedback', {}),
                'star_analysis': layer2_result.get('star_analysis', {}),
                'strengths_evidence': layer2_result.get('strengths_evidence', []),
                'improvements_evidence': layer2_result.get('improvements_evidence', []),
            },
            'layer3_expert': {
                'score': layer3_result['score'],
                'weight': '5%',
                'matched': layer3_result.get('matched_elements', []),
                'missing': layer3_result.get('missing_elements', [])
            }
        },
        'strengths': all_strengths[:5],
        'improvements': all_improvements[:5]
    }


# ==========================================
# MAIN EVALUATION FUNCTION
# ==========================================

def evaluate_response_three_layer(
    response: str,
    skill: str,
    question_id: str = "",
    question_text: str = ""
) -> Dict:
    """
    Main function: Run all three layers and return combined result
    """
    
    # Layer 1: Rule-based filter
    layer1 = rule_based_filter(response)
    
    # Layer 2: LLM quality check
    layer2 = llm_quality_check(response, skill, question_text, features=layer1)
    
    # Layer 3: Expert comparison
    layer3 = expert_comparison(response, question_id)
    
    # Calculate final score
    final_result = calculate_three_layer_score(layer1, layer2, layer3)
    
    return final_result


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set in environment variables")


LLM_CACHE = {}

def llm_score_response(response: str, skill: str, retries: int = 3) -> Dict:
    """
    Score response using LLM (Groq API) with caching and rate-limit handling
    """

    cache_key = hash(response)
    if cache_key in LLM_CACHE:
        return LLM_CACHE[cache_key]

    system_prompt = (
        "You are an expert cybersecurity interview evaluator. "
        "Score behavioural responses for senior cybersecurity roles. "
        "Use integer scores from 1 (very weak) to 5 (excellent). "
        "Base scores strictly on evidence in the response. "
        "Return STRICT JSON only."
    )

    user_prompt = f"""
Evaluate the following behavioural interview response.

Score each skill from 1 to 5:
- communication
- leadership
- decision_making
- critical_thinking

Then provide a brief justification (1–2 sentences).

Response:
\"\"\"{response}\"\"\"

Return STRICT JSON ONLY in this format:
{{
  "communication": <int>,
  "leadership": <int>,
  "decision_making": <int>,
  "critical_thinking": <int>,
  "justification": "<short explanation>"
}}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    for attempt in range(1, retries + 1):
        try:
            response_obj = requests.post(url, headers=headers, json=payload, timeout=30)
            response_obj.raise_for_status()

            data = response_obj.json()
            content = data["choices"][0]["message"]["content"]

            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in LLM output")

            scores = json.loads(content[start:end])

            required = [
                "communication",
                "leadership",
                "decision_making",
                "critical_thinking",
                "justification",
            ]
            for key in required:
                if key not in scores:
                    raise ValueError(f"Missing key: {key}")

            # ✅ Cache successful result
            LLM_CACHE[cache_key] = scores
            return scores

        except requests.exceptions.HTTPError as e:
            if response_obj.status_code == 429:
                wait = 5 * attempt
                print(f"  ⏳ Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"  LLM HTTP error: {e}")
                time.sleep(1)

        except Exception as e:
            print(f"  LLM attempt {attempt} failed: {e}")
            time.sleep(1)

    # ✅ Fallback (also cached to avoid repeated calls)
    fallback = {
        "communication": 3,
        "leadership": 3,
        "decision_making": 3,
        "critical_thinking": 3,
        "justification": "LLM inference failed; fallback applied."
    }

    LLM_CACHE[cache_key] = fallback
    return fallback
