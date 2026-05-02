"""
Expert Answer Comparator (Layer 3)
Purpose: Compare candidate responses to expert answers
Weight: 5% of final score
"""

import json
import os
import re
from typing import Dict, List, Tuple
from collections import Counter


# ==========================================
# LOAD EXPERT ANSWERS
# ==========================================

EXPERT_ANSWERS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'expert_answers.json')
_expert_cache = None

def load_expert_answers() -> Dict:
    """Load expert answers with caching"""
    global _expert_cache
    if _expert_cache is None:
        try:
            with open(EXPERT_ANSWERS_PATH, 'r') as f:
                data = json.load(f)
                _expert_cache = data.get('expert_answers', {})
        except Exception as e:
            print(f"Error loading expert answers: {e}")
            _expert_cache = {}
    return _expert_cache


# ==========================================
# KEYWORD EXTRACTION
# ==========================================

# Important cybersecurity terms to look for
CYBERSECURITY_VOCAB = {
    # Vulnerability & Risk
    'vulnerability', 'exploit', 'cve', 'zero-day', 'patch', 'remediation',
    'cvss', 'epss', 'risk', 'threat', 'attack', 'breach',
    
    # Security Tools
    'siem', 'soc', 'edr', 'ids', 'ips', 'firewall', 'waf',
    'siem', 'siem', 'forensics', 'pentest', 'scanner',
    
    # Compliance & Governance
    'gdpr', 'pci-dss', 'soc 2', 'compliance', 'audit', 'regulation',
    'policy', 'framework', 'nist', 'iso',
    
    # Attack Types
    'phishing', 'ransomware', 'malware', 'ddos', 'injection',
    'xss', 'sql injection', 'lateral movement', 'exfiltration',
    
    # Security Concepts
    'authentication', 'authorization', 'encryption', 'access control',
    'incident response', 'threat intelligence', 'apt', 'ioc',
    
    # Business Terms
    'roi', 'budget', 'stakeholder', 'executive', 'board',
    'business impact', 'risk acceptance', 'sla'
}

# STAR framework keywords
STAR_KEYWORDS = {
    'situation': [
        'when', 'during', 'at the time', 'in my role', 'encountered',
        'situation', 'context', 'background', 'previously'
    ],
    'task': [
        'needed to', 'had to', 'was responsible', 'tasked with',
        'my goal', 'objective', 'challenge', 'problem'
    ],
    'action': [
        'i decided', 'i implemented', 'i created', 'i led', 'i managed',
        'i coordinated', 'i developed', 'i established', 'i deployed'
    ],
    'result': [
        'result', 'outcome', 'achieved', 'successfully', 'impact',
        'led to', 'resulted in', 'delivered', 'reduced', 'improved'
    ]
}

# Professional/leadership keywords
LEADERSHIP_KEYWORDS = [
    'led', 'managed', 'directed', 'coordinated', 'oversaw',
    'mentored', 'developed', 'established', 'built', 'created'
]

# Metrics/quantification keywords
METRICS_KEYWORDS = [
    r'\d+%', r'\$\d+', r'\d+ (days?|weeks?|months?|hours?|minutes?)',
    r'\d+ (users?|customers?|systems?|servers?|applications?)',
    r'increased? by', r'decreased? by', r'reduced? by'
]


def extract_keywords(text: str) -> Dict[str, List[str]]:
    """Extract all types of keywords from text"""
    
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]+\b', text_lower)
    
    result = {
        'all_words': words,
        'cyber_terms': [],
        'star_components': {'situation': [], 'task': [], 'action': [], 'result': []},
        'leadership_terms': [],
        'metrics': []
    }
    
    # Cybersecurity terms
    for term in CYBERSECURITY_VOCAB:
        if term in text_lower:
            result['cyber_terms'].append(term)
    
    # STAR components
    for component, keywords in STAR_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                result['star_components'][component].append(kw)
    
    # Leadership terms
    for term in LEADERSHIP_KEYWORDS:
        if term in text_lower:
            result['leadership_terms'].append(term)
    
    # Metrics
    for pattern in METRICS_KEYWORDS:
        matches = re.findall(pattern, text_lower)
        result['metrics'].extend(matches)
    
    return result


# ==========================================
# SIMILARITY CALCULATIONS
# ==========================================

def calculate_keyword_overlap(candidate_keywords: List[str], expert_keywords: List[str]) -> float:
    """Calculate overlap between keyword sets"""
    
    if not expert_keywords:
        return 0.5
    
    candidate_set = set(k.lower() for k in candidate_keywords)
    expert_set = set(k.lower() for k in expert_keywords)
    
    if not candidate_set:
        return 0.0
    
    overlap = len(candidate_set & expert_set)
    return overlap / len(expert_set)


def calculate_semantic_similarity(candidate: str, expert: str) -> float:
    """
    Calculate semantic similarity using multiple methods
    Returns score 0-1
    """
    
    # Method 1: Keyword overlap
    cand_keywords = extract_keywords(candidate)
    exp_keywords = extract_keywords(expert)
    
    cyber_overlap = calculate_keyword_overlap(
        cand_keywords['cyber_terms'],
        exp_keywords['cyber_terms']
    )
    
    # Method 2: STAR structure comparison
    star_scores = []
    for component in ['situation', 'task', 'action', 'result']:
        cand_has = len(cand_keywords['star_components'][component]) > 0
        exp_has = len(exp_keywords['star_components'][component]) > 0
        
        if exp_has and cand_has:
            star_scores.append(1.0)
        elif not exp_has:
            star_scores.append(0.5)  # Don't penalize if expert doesn't have
        else:
            star_scores.append(0.0)
    
    star_score = sum(star_scores) / len(star_scores)
    
    # Method 3: Length appropriateness
    cand_len = len(candidate.split())
    exp_len = len(expert.split())
    
    if exp_len > 0:
        len_ratio = min(cand_len / exp_len, exp_len / cand_len) if cand_len > 0 else 0
        length_score = len_ratio if len_ratio > 0.3 else 0.3
    else:
        length_score = 0.5
    
    # Method 4: Metrics presence
    cand_metrics = len(cand_keywords['metrics'])
    exp_metrics = len(exp_keywords['metrics'])
    
    if exp_metrics > 0:
        metrics_score = min(cand_metrics / exp_metrics, 1.0)
    else:
        metrics_score = 0.5
    
    # Weighted combination
    weights = {
        'cyber_overlap': 0.35,
        'star_structure': 0.30,
        'length': 0.15,
        'metrics': 0.20
    }
    
    overall = (
        cyber_overlap * weights['cyber_overlap'] +
        star_score * weights['star_structure'] +
        length_score * weights['length'] +
        metrics_score * weights['metrics']
    )
    
    return overall


# ==========================================
# EXPERT COMPARISON FUNCTION
# ==========================================

def compare_to_expert(
    candidate_response: str,
    question_id: str
) -> Dict:
    """
    Compare candidate response to expert answer
    
    Args:
        candidate_response: The candidate's answer
        question_id: ID of the question (e.g., 'comm_001')
    
    Returns:
        Dict with score, matched elements, feedback
    """
    
    expert_answers = load_expert_answers()
    
    if question_id not in expert_answers:
        return {
            'score': 3.0,
            'similarity': 0.5,
            'matched_elements': [],
            'missing_elements': [],
            'matched_concepts': [],
            'feedback': "No expert answer available for comparison",
            'available': False
        }
    
    expert = expert_answers[question_id]
    expert_answer = expert.get('expert_answer', '')
    expert_elements = expert.get('key_elements', [])
    expert_concepts = expert.get('cybersecurity_concepts', [])
    
    # Extract keywords from both
    cand_keywords = extract_keywords(candidate_response)
    exp_keywords = extract_keywords(expert_answer)
    
    # Calculate semantic similarity
    similarity = calculate_semantic_similarity(candidate_response, expert_answer)
    
    # Find matched and missing elements
    matched_elements = []
    missing_elements = []
    
    for element in expert_elements:
        element_lower = element.lower()
        # Check if element keywords appear in candidate response
        element_words = element_lower.split()
        if any(word in candidate_response.lower() for word in element_words if len(word) > 3):
            matched_elements.append(element)
        else:
            missing_elements.append(element)
    
    # Find matched concepts
    matched_concepts = []
    for concept in expert_concepts:
        if concept.lower() in candidate_response.lower():
            matched_concepts.append(concept)
    
    # Calculate element match percentage
    element_match_pct = len(matched_elements) / len(expert_elements) if expert_elements else 0.5
    concept_match_pct = len(matched_concepts) / len(expert_concepts) if expert_concepts else 0.5
    
    # Calculate final score (1-5 scale)
    # Combination of similarity and element matching
    combined_score = (similarity * 0.6) + (element_match_pct * 0.4)
    score = 1 + (combined_score * 4)  # Convert to 1-5
    
    # Generate feedback
    if score >= 4:
        feedback = "Strong alignment with expert response"
    elif score >= 3:
        feedback = "Good response with some expert-level elements"
    elif score >= 2:
        feedback = "Basic response missing key elements"
    else:
        feedback = "Response lacks alignment with best practices"
    
    # STAR comparison
    star_comparison = {}
    for component in ['situation', 'task', 'action', 'result']:
        cand_count = len(cand_keywords['star_components'][component])
        exp_count = len(exp_keywords['star_components'][component])
        
        star_comparison[component] = {
            'candidate_has': cand_count > 0,
            'expert_has': exp_count > 0,
            'match': cand_count > 0 and exp_count > 0
        }
    
    return {
        'score': round(score, 1),
        'similarity': round(similarity, 3),
        'matched_elements': matched_elements,
        'missing_elements': missing_elements[:5],  # Limit to 5
        'matched_concepts': matched_concepts,
        'element_match_percentage': round(element_match_pct * 100, 1),
        'concept_match_percentage': round(concept_match_pct * 100, 1),
        'feedback': feedback,
        'star_comparison': star_comparison,
        'available': True,
        'expert_strength': expert.get('star_strength', 'unknown')
    }


# ==========================================
# BATCH COMPARISON
# ==========================================

def compare_multiple_responses(
    responses: List[Dict[str, str]]
) -> List[Dict]:
    """
    Compare multiple responses to their expert answers
    
    Args:
        responses: List of {'question_id': str, 'response': str}
    
    Returns:
        List of comparison results
    """
    
    results = []
    
    for item in responses:
        question_id = item.get('question_id', '')
        response = item.get('response', '')
        
        comparison = compare_to_expert(response, question_id)
        comparison['question_id'] = question_id
        
        results.append(comparison)
    
    return results


# ==========================================
# TEST FUNCTION
# ==========================================

def test_expert_comparator():
    """Test the expert comparator"""
    
    print("=" * 60)
    print("Testing Expert Comparator (Layer 3)")
    print("=" * 60)
    
    # Test response that should score well
    test_response = """During a routine vulnerability scan, I discovered a critical SQL injection 
    vulnerability in our production e-commerce platform two weeks before Black Friday. 
    The CTO and VP of Sales were pushing back against any downtime.
    
    As the Security Architect, I needed to communicate the severity to non-technical executives.
    My goal was to get buy-in for emergency patching while respecting business concerns.
    
    I created an executive dashboard that translated technical risk into business impact.
    I used CVSS scores combined with EPSS to show 78% exploitation likelihood.
    I quantified impact as $500K per hour downtime plus $2M PCI-DSS fines.
    I presented three remediation options with trade-offs.
    
    The executives approved emergency patching. We deployed with zero incidents.
    This led to monthly risk reviews and a 30% security budget increase."""
    
    result = compare_to_expert(test_response, 'comm_001')
    
    print(f"\n📊 Score: {result['score']}/5")
    print(f"📈 Similarity: {result['similarity'] * 100:.1f}%")
    print(f"✅ Expert Available: {result['available']}")
    print(f"💪 Expert Strength: {result.get('expert_strength', 'N/A')}")
    
    print(f"\n🎯 Element Match: {result['element_match_percentage']}%")
    print(f"📚 Concept Match: {result['concept_match_percentage']}%")
    
    if result['matched_elements']:
        print(f"\n✅ Matched Elements ({len(result['matched_elements'])}):")
        for e in result['matched_elements'][:5]:
            print(f"   ✓ {e}")
    
    if result['missing_elements']:
        print(f"\n❌ Missing Elements ({len(result['missing_elements'])}):")
        for e in result['missing_elements'][:5]:
            print(f"   ✗ {e}")
    
    if result['matched_concepts']:
        print(f"\n🔐 Matched Concepts ({len(result['matched_concepts'])}):")
        for c in result['matched_concepts']:
            print(f"   • {c}")
    
    print(f"\n💬 Feedback: {result['feedback']}")
    
    if result.get('star_comparison'):
        print(f"\n⭐ STAR Comparison:")
        for component, data in result['star_comparison'].items():
            status = "✓" if data['match'] else "✗"
            print(f"   {status} {component.title()}: Candidate={data['candidate_has']}, Expert={data['expert_has']}")


if __name__ == "__main__":
    test_expert_comparator()
