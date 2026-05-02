"""
Rule-Based Filter (Layer 1) - Basic structure check
Purpose: Quick pass/fail validation, NOT detailed scoring
Weight: 20% of final score
"""

import re
from typing import Dict


def extract_basic_features(response: str) -> Dict:
    """Extract only essential features for pass/fail determination"""
    
    response_lower = response.lower()
    words = response.split()
    
    features = {
        'word_count': len(words),
        'has_situation_markers': False,
        'has_task_markers': False,
        'has_action_markers': False,
        'has_result_markers': False,
        'star_component_count': 0,
        'has_first_person': False,
        'has_metrics': False
    }
    cyber_terms = [
    'siem', 'firewall', 'ids', 'ips', 'edr', 'xdr',
    'cve', 'cvss', 'threat', 'vulnerability', 'exploit',
    'mitre', 'nist', 'encryption', 'incident'
    ]

    features['cyber_term_count'] = sum(
    1 for term in cyber_terms if term in response_lower
    )
    leadership_words = [
    'led', 'managed', 'coordinated', 'mentored',
    'guided', 'directed', 'oversaw'
    ]

    features['leadership_indicators'] = sum(
    1 for word in leadership_words if word in response_lower
    )
    vague_words = ['some', 'things', 'stuff', 'various', 'many', 'several']

    features['vagueness'] = sum(
    1 for word in vague_words if word in response_lower
    )   
    
    # STAR component markers (simplified)
    situation_markers = ['when', 'during', 'at the time', 'in my role', 'encountered', 'situation']
    task_markers = ['needed to', 'had to', 'was responsible', 'tasked with', 'my goal', 'task']
    action_markers = ['i decided', 'i implemented', 'i created', 'i led', 'i managed', 'i coordinated', 'action']
    result_markers = ['result', 'outcome', 'achieved', 'successfully', 'impact', 'led to', 'resulted']
    
    features['has_situation_markers'] = any(marker in response_lower for marker in situation_markers)
    features['has_task_markers'] = any(marker in response_lower for marker in task_markers)
    features['has_action_markers'] = any(marker in response_lower for marker in action_markers)
    features['has_result_markers'] = any(marker in response_lower for marker in result_markers)
    
    features['star_component_count'] = sum([
        features['has_situation_markers'],
        features['has_task_markers'],
        features['has_action_markers'],
        features['has_result_markers']
    ])
    
    # First person check
    features['has_first_person'] = bool(re.search(r'\bI\b', response))
    
    # Metrics check
    features['has_metrics'] = bool(re.search(r'\d+\%|\$\d+|\d+ (days|weeks|months|hours)', response))
    
    return features


def rule_based_filter(response: str) -> Dict:
    """
    Layer 1: Basic structure check
    Returns: {pass: bool, score: 0-5, reason: str, features: dict}
    
    Scoring (0-5 scale):
    - 0: Disqualified (too short, no structure)
    - 1-2: Basic structure but weak
    - 3: Acceptable structure
    - 4-5: Good structure with metrics
    """
    
    features = extract_basic_features(response)
    
    # ==========================================
    # DISQUALIFICATION CHECKS (Score = 0)
    # ==========================================
    
    disqualification_reasons = []
    
    # Check 1: Too short
    if features['word_count'] < 40:
        return {
        'pass': False,
        'score': 0,
        'reason': "Too short (less than 40 words). Provide more detail.",
        'disqualified': True,

        "word_count": features['word_count'],
        "star_component_count": features['star_component_count'],
        "cyber_term_count": features['cyber_term_count'],
        "leadership_indicators": features['leadership_indicators'],
        "vagueness": features['vagueness']
    }
    
    # Check 2: No STAR structure at all
    if features['star_component_count'] == 0:
        return {
        'pass': True,
        'score': 1,
        'reason': "No clear STAR structure detected",
        'disqualified': False,

        "word_count": features['word_count'],
        "star_component_count": features['star_component_count'],
        "cyber_term_count": features['cyber_term_count'],
        "leadership_indicators": features['leadership_indicators'],
        "vagueness": features['vagueness']
    }

    # Check 3: No personal ownership and very brief
    if not features['has_first_person'] and features['word_count'] < 80:
        return {
        'pass': False,
        'score': 0,
        'reason': "No personal ownership detected. Use 'I' statements.",
        'disqualified': True,

        "word_count": features['word_count'],
        "star_component_count": features['star_component_count'],
        "cyber_term_count": features['cyber_term_count'],
        "leadership_indicators": features['leadership_indicators'],
        "vagueness": features['vagueness']
    }
    
    # ==========================================
    # PASSED BASIC CHECKS - Calculate Score
    # ==========================================
    
    # Base score for passing minimum requirements
    base_score = 2
    
    # Bonus for STAR completeness
    if features['star_component_count'] >= 3:
        base_score += 1
    if features['star_component_count'] >= 4:
        base_score += 0.5
    
    # Bonus for first person usage
    if features['has_first_person']:
        base_score += 0.5
    
    # Bonus for metrics
    if features['has_metrics']:
        base_score += 0.5
    
    # Bonus for good length (100-300 words is optimal)
    if 100 <= features['word_count'] <= 300:
        base_score += 0.5
    
    # Cap at 5
    final_score = min(5, base_score)
    
    # Generate reason
    star_desc = f"{features['star_component_count']}/4 STAR components"
    if features['star_component_count'] >= 3:
        reason = f"Good structure ({star_desc}). Passed basic validation."
    else:
        reason = f"Basic structure ({star_desc}). Consider adding more STAR elements."
    
    return {
    'pass': True,
    'score': round(final_score, 1),
    'reason': reason,
    'disqualified': False,

    "word_count": features['word_count'],
    "star_component_count": features['star_component_count'],
    "cyber_term_count": features['cyber_term_count'],
    "leadership_indicators": features['leadership_indicators'],
    "vagueness": features['vagueness']
}

