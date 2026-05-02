# backend/chatbot_engine.py

from enum import Enum
from typing import Dict, List, Optional
import json
from datetime import datetime
import random
from pathlib import Path
from hybrid_scorer import evaluate_response_three_layer
from llm_evaluator import generate_personalized_feedback

class InterviewState(Enum):
    """Interview states"""
    NOT_STARTED = "not_started"
    INTRODUCTION = "introduction"
    QUESTIONING = "questioning"
    FOLLOW_UP = "follow_up"
    COMPLETED = "completed"


class ConversationalInterviewBot:
    """
    Advanced conversational interview bot with adaptive questioning
    """
    
    DEFAULT_SKILLS = [
        "communication",
        "leadership",
        "decision_making",
        "critical_thinking"
    ]
    
    def __init__(self, candidate_name: str):
        self.candidate_name = candidate_name
        self.target_skills = self.DEFAULT_SKILLS
        self.state = InterviewState.NOT_STARTED
        self.conversation_history = []
        self.current_skill_index = 0
        self.skill_scores = {}
        self.questions_asked = []
        self.current_question = None
        self.session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        self.start_time = datetime.now()
        self.follow_up_asked = {}
        self.is_follow_up = False
        self.follow_up_skill = None
        
        # Load questions database
        self.questions_db = self._load_questions()
    
    
    def _load_questions(self) -> Dict:
        """Load questions from JSON file (robust, path-safe)"""

        backend_dir = Path(__file__).resolve().parent
        project_root = backend_dir.parent

        questions_path = project_root / "data" / "final 16.json"

        if questions_path.exists():
            with open(questions_path, "r", encoding="utf-8") as f:
                return json.load(f)

        print("[WARN] final 16.json not found, using fallback questions")
        return self._get_fallback_questions()

    def _get_fallback_questions(self) -> Dict:
        """Fallback questions if JSON not found"""
        return {
            "communication": [
                {
                    "id": "comm_001",
                    "text": "Describe a time when you had to explain a critical security vulnerability to non-technical executives.",
                    "difficulty": "standard",
                    "skill": "communication"
                }
            ],
            "leadership": [
                {
                    "id": "lead_001",
                    "text": "Tell me about a time when you had to lead your team through a major security incident.",
                    "difficulty": "standard",
                    "skill": "leadership"
                }
            ],
            "decision_making": [
                {
                    "id": "dec_001",
                    "text": "Describe a situation where you had to make a critical security decision with limited information.",
                    "difficulty": "standard",
                    "skill": "decision_making"
                }
            ],
            "critical_thinking": [
                {
                    "id": "crit_001",
                    "text": "Tell me about a time when you identified a security flaw that others had missed.",
                    "difficulty": "standard",
                    "skill": "critical_thinking"
                }
            ]
        }
    
    def start_interview(self) -> Dict:
        """Initialize interview with introduction"""
        self.state = InterviewState.INTRODUCTION
        
        skills_list = ", ".join([s.replace('_', ' ').title() for s in self.target_skills[:3]])
        if len(self.target_skills) > 3:
            skills_list += f" and {len(self.target_skills) - 3} more"
        
        message = {
            "type": "introduction",
            "content": f"Hello {self.candidate_name}!\n\n"
                      f"Welcome to CyberHire AI - your intelligent interview assistant.\n\n"
                      f"Today we'll be assessing {len(self.target_skills)} key skills: {skills_list}\n\n"
                      f"through behavioral questions using the STAR framework:\n\n"
                      f"- Situation: Describe the context\n"
                      f"- Task: Explain your responsibility\n"
                      f"- Action: Detail what you did\n"
                      f"- Result: Share the outcome\n\n"
                      f"Tips:\n"
                      f"- Take your time with each response\n"
                      f"- Be specific with examples\n"
                      f"- Include measurable results when possible\n\n"
                      f"Ready to begin? Type 'yes' when you're ready!",
            "session_id": self.session_id,
            "requires_response": True,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(message)
        return message
    
    def process_response(self, user_input: str) -> Dict:
        """
        Main response processing logic
        Routes to appropriate handler based on current state
        """
        
        # Log user input
        self._log_message("user", user_input)
        
        # Route based on state
        if self.state == InterviewState.INTRODUCTION:
            return self._handle_introduction_response(user_input)
        
        elif self.state == InterviewState.QUESTIONING:
            return self._handle_question_response(user_input)
        
        elif self.state == InterviewState.FOLLOW_UP:
            return self._handle_followup_response(user_input)
        
        elif self.state == InterviewState.COMPLETED:
            return self._get_completion_message()
        
        else:
            return {"error": "Invalid state"}
    
    def _handle_introduction_response(self, user_input: str) -> Dict:
        """Handle response to introduction"""
        
        # Check if user is ready (flexible matching)
        ready_keywords = ['yes', 'ready', 'sure', 'ok', 'let\'s go', 'start', 'begin']
        is_ready = any(keyword in user_input.lower() for keyword in ready_keywords)
        
        if is_ready:
            # Start questioning
            return self._ask_next_question()
        else:
            # Ask again
            return {
                "type": "clarification",
                "content": "No problem! Take your time. When you're ready to begin, just type 'yes' or 'ready'.",
                "requires_response": True
            }
    
    def _ask_next_question(self) -> Dict:
        """Ask the next interview question"""
        
        self.state = InterviewState.QUESTIONING
        
        # Get current skill (use follow_up_skill if this is a follow-up)
        if self.is_follow_up:
            current_skill = self.follow_up_skill
            question_num = len(self.questions_asked)
            total_display = len(self.target_skills) + sum(self.follow_up_asked.values())
        else:
            current_skill = self.target_skills[self.current_skill_index]
            if current_skill is None:
                current_skill = self.target_skills[0]
            question_num = self.current_skill_index + 1
            total_display = len(self.target_skills)
        
        # Select question
        skill_for_select = str(current_skill) if current_skill else "communication"
        question = self._select_question(skill_for_select)
        self.current_question = question
        
        # Create message
        skill_str = str(current_skill) if current_skill else "Unknown"
        skill_label = f"Follow-up: {skill_str.replace('_', ' ').title()}" if self.is_follow_up else skill_str.replace('_', ' ').title()
        message = {
            "type": "question",
            "skill": current_skill,
            "is_follow_up": self.is_follow_up,
            "question_id": question['id'],
            "content": f"Question {question_num} of {total_display}\n"
                      f"Skill: {skill_label}\n\n"
                      f"{question.get('question', question.get('text', ''))}\n\n"
                      f"Please structure your response using the STAR framework.",
            "requires_response": True,
            "metadata": {
                "skill": current_skill,
                "difficulty": question.get('difficulty', 'standard'),
                "question_number": self.current_skill_index + 1,
                "total_questions": len(self.target_skills)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.is_follow_up = False
        self.follow_up_skill = None
        
        self._log_message("assistant", message)
        return message
    
    def _select_question(self, skill: str) -> Dict:
        """Select appropriate question for the skill"""
        
        skill_key_map = {
            "communication": "communication_competency",
            "leadership": "leadership_competency", 
            "decision_making": "decision_making_competency",
            "critical_thinking": "critical_thinking_competency"
        }
        
        db_key = skill_key_map.get(skill, skill)
        
        skill_data = self.questions_db.get(db_key, {})
        questions_list = skill_data.get("questions", [])
        
        available_questions = [
            q for q in questions_list
            if q['id'] not in self.questions_asked
        ]
        
        if not available_questions:
            # Fallback if no questions available
            return {
                "id": f"{skill}_fallback",
                "text": f"Tell me about a time when you demonstrated strong {skill.replace('_', ' ')} skills in a cybersecurity context.",
                "difficulty": "standard",
                "skill": skill
            }
        
        # Select randomly
        selected = random.choice(available_questions)
        self.questions_asked.append(selected['id'])
        
        return selected
    
    def _handle_question_response(self, user_input: str) -> Dict:
        """Evaluate response using Three-Layer Hybrid System"""
        
        current_skill = self.target_skills[self.current_skill_index] if self.current_skill_index < len(self.target_skills) else "communication"
        current_question = self.current_question or {}
        question_id = current_question.get('id', '')
        question_text = current_question.get('question', '') or current_question.get('text', '')
        
        # Evaluate using Three-Layer System
        try:
            evaluation = evaluate_response_three_layer(
                response=user_input,
                skill=current_skill,
                question_id=question_id,
                question_text=question_text
            )
            red_flags = evaluation.get('red_flags', [])
            if not red_flags:
                red_flags = ["None identified"]

            # Store the score with full breakdown
            if current_skill not in self.skill_scores:
                self.skill_scores[current_skill] = []
            
            # Generate feedback for this response
            feedback = self._generate_enhanced_feedback(evaluation, current_skill)
            
            self.skill_scores[current_skill].append({
                "score": evaluation['final_score'],
                "percentage": evaluation['percentage'],
                "confidence": evaluation.get("confidence", 0.7),
                "passed": evaluation['passed'],
                "question_id": question_id,
                "question": question_text,
                "response": user_input,
                "feedback": feedback,
                "skill_name": current_skill,
                "word_count": len(user_input.split()),
                "timestamp": datetime.now().isoformat(),
                "layer_scores": evaluation.get('layer_scores', {}),
                "strengths": evaluation.get('strengths', []),
                "improvements": evaluation.get('improvements', [])
            })
            
            # Check for adaptive follow-up (score < 50% and not already asked)
            needs_follow_up = evaluation['percentage'] < 50 and not self.follow_up_asked.get(current_skill, False)
            
            if needs_follow_up:
                self.follow_up_asked[current_skill] = True
                self.follow_up_skill = current_skill
                self.is_follow_up = True
                
                next_question = self._ask_next_question()

                return {
                    "type": "feedback_and_next",
                    "feedback": feedback,
                    "evaluation": {
                        "score": evaluation['final_score'],
                        "percentage": evaluation['percentage'],
                        "max_score": 25,
                        "passed": evaluation['passed'],
                        "layer_breakdown": evaluation.get('layer_scores', {}),
                        "strengths": evaluation.get('strengths', [])[:5],
                        "improvements": evaluation.get('improvements', [])[:5],
                        "follow_up_triggered": True,
                        "follow_up_skill": current_skill,
                        "red_flags": red_flags,
                        "confidence": evaluation.get('confidence', 0.7),
                        "star_breakdown": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('star_breakdown', {}),
                        "hiring_recommendation": evaluation.get('hiring_recommendation', 'Unknown'),
                        "authenticity": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('authenticity', {'seems_real': True, 'evidence': 'Unable to assess'}),
                        "next_steps": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('next_steps', []),
                        "personalized_feedback": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('personalized_feedback', {}),
                        "positive_indicators": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('positive_indicators', []),
                    },
                    "next_question": next_question,
                    "follow_up_notice": f"Since your score was below 50% in {current_skill.replace('_', ' ').title()}, we'll ask an additional question to get a better assessment."
                }
            
            # Move to next question or complete
            self.current_skill_index += 1
            
            if self.current_skill_index < len(self.target_skills):
                # More questions to ask
                next_question = self._ask_next_question()

                return {
                    "type": "feedback_and_next",
                    "feedback": feedback,
                    "evaluation": {
                        "score": evaluation['final_score'],
                        "percentage": evaluation['percentage'],
                        "max_score": 25,
                        "passed": evaluation['passed'],
                        "layer_breakdown": evaluation.get('layer_scores', {}),
                        "strengths": evaluation.get('strengths', [])[:5],
                        "improvements": evaluation.get('improvements', [])[:5],
                        "red_flags": red_flags,
                        "confidence": evaluation.get('confidence', 0.7),
                        "star_breakdown": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('star_breakdown', {}),
                        "hiring_recommendation": evaluation.get('hiring_recommendation', 'Unknown'),
                        "authenticity": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('authenticity', {'seems_real': True, 'evidence': 'Unable to assess'}),
                        "next_steps": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('next_steps', []),
                        "personalized_feedback": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('personalized_feedback', {}),
                        "positive_indicators": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('positive_indicators', []),
                    },
                    "next_question": next_question
                }
            else:
                # Interview complete
                self.state = InterviewState.COMPLETED
                final_report = self._generate_final_report()
                
                return {
                    "type": "completion",
                    "feedback": feedback,
                    "evaluation": {
                        "score": evaluation['final_score'],
                        "percentage": evaluation['percentage'],
                        "max_score": 25,
                        "passed": evaluation['passed'],
                        "layer_breakdown": evaluation.get('layer_scores', {}),
                        "strengths": evaluation.get('strengths', [])[:5],
                        "improvements": evaluation.get('improvements', [])[:5],
                        "red_flags": red_flags,
                        "confidence": evaluation.get('confidence', 0.7),
                        "star_breakdown": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('star_breakdown', {}),
                        "hiring_recommendation": evaluation.get('hiring_recommendation', 'Unknown'),
                        "authenticity": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('authenticity', {'seems_real': True, 'evidence': 'Unable to assess'}),
                        "next_steps": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('next_steps', []),
                        "personalized_feedback": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('personalized_feedback', {}),
                        "positive_indicators": evaluation.get('layer_scores', {}).get('layer2_llm', {}).get('positive_indicators', []),
                    },
                    "completion_message": f"Excellent work, {self.candidate_name}!\n\n"
                                        f"You've completed all {len(self.target_skills)} skill assessments.\n"
                                        f"Generating your detailed report now...",
                    "final_report": final_report
                }
        
        except Exception as e:
            print(f"Error during three-layer evaluation: {e}")
            import traceback
            traceback.print_exc()
            return {
                "type": "error",
                "content": "I encountered an error evaluating your response. Let's continue with the next question.",
                "next_question": self._ask_next_question()
            }

    def _filter_generic_improvements(self, improvements: list, candidate_response: str = "") -> list:
        """Filter out generic improvements and make them specific to the answer"""
        if not improvements:
            return improvements
        
        generic_phrases = [
            "reduced by 30%",
            "increased by 40%",
            "within 3 months",
            "in 6 months",
            "more specific metrics",
            "provide more details",
            "add specific numbers",
            "concrete examples",
            "in general",
            "some time",
            "one time",
            "a situation",
            "one project"
        ]
        
        filtered = []
        response_lower = candidate_response.lower() if candidate_response else ""
        
        for imp in improvements:
            imp_str = str(imp).lower()
            
            # Check if improvement is too generic
            is_generic = any(phrase in imp_str for phrase in generic_phrases)
            
            # Check if it quotes their actual answer
            quotes_their_answer = any(word in imp_str for word in response_lower.split()[:20]) if response_lower else False
            
            # If generic and doesn't quote their answer, try to make it specific
            if is_generic and not quotes_their_answer:
                words = candidate_response.split() if candidate_response else []
                if len(words) > 5:
                    their_phrase = " ".join(words[:10])
                    improved = f"Your answer mentions: '{their_phrase}...' - IMPROVEMENT: Add specific metrics, timeline, and your personal contribution to this statement."
                    filtered.append(improved)
                    continue
            
            filtered.append(imp)
        
        return filtered
    
    def _get_score_intro(self, percentage: float) -> str:
        """Get appropriate feedback introduction based on score percentage"""
        if percentage >= 90:
            return "Exceptional response demonstrating deep expertise and real-world experience."
        elif percentage >= 80:
            return "Strong response showing clear competency with good depth."
        elif percentage >= 70:
            return "Good response with solid foundation, but room for improvement."
        elif percentage >= 60:
            return "Adequate response demonstrating basic competency, but lacks sufficient depth."
        elif percentage >= 50:
            return "Basic response needing more detail and specificity."
        else:
            return "Response needs significant development - see specific suggestions below."

    def _generate_enhanced_feedback(self, evaluation: Dict, skill: str) -> str:
        """Generate detailed, personalized feedback from three-layer evaluation"""
        
        score = evaluation.get('final_score', 0)
        percentage = evaluation.get('percentage', 0)
        passed = evaluation.get('passed', True)
        layer_scores = evaluation.get('layer_scores', {})
        
        # Get Layer 2 (LLM) evaluation data
        llm_eval = layer_scores.get('layer2_llm', {})
        
        # Build feedback using LLM's actual output
        feedback_parts = []
        
        # Score-based intro
        feedback_parts.append(self._get_score_intro(percentage))
        feedback_parts.append(f"(Score: {score:.1f}/25 - {percentage:.0f}%)")
        feedback_parts.append("")
        
        # Use LLM's personalized feedback fields if available
        personalized = llm_eval.get('personalized_feedback', {})
        
        if personalized:
            if personalized.get('what_went_well'):
                feedback_parts.append("WHAT WENT WELL:")
                feedback_parts.append(personalized['what_went_well'])
                feedback_parts.append("")
            
            if personalized.get('specific_quote'):
                feedback_parts.append("EVIDENCE FROM YOUR ANSWER:")
                feedback_parts.append(f'"{personalized["specific_quote"]}"')
                feedback_parts.append("")
        
        # Add strengths if available
        strengths = llm_eval.get('strengths', []) or evaluation.get('strengths', [])
        if strengths:
            feedback_parts.append("STRENGTHS:")
            for i, strength in enumerate(strengths[:4], 1):
                if isinstance(strength, dict):
                    title = strength.get('title', '')
                    quote = strength.get('quote', '')
                    if title:
                        feedback_parts.append(f"{i}. {title}")
                    if quote:
                        feedback_parts.append(f'   "{quote}"')
                else:
                    feedback_parts.append(f"{i}. {strength}")
            feedback_parts.append("")
        
        # Add improvements if available
        improvements = llm_eval.get('improvements', []) or evaluation.get('improvements', [])
        if improvements:
            feedback_parts.append("AREAS FOR IMPROVEMENT:")
            for i, imp in enumerate(improvements[:4], 1):
                if isinstance(imp, dict):
                    title = imp.get('title', '')
                    suggestion = imp.get('suggestion', imp.get('description', ''))
                    if title:
                        feedback_parts.append(f"{i}. {title}")
                    if suggestion:
                        feedback_parts.append(f"   {suggestion}")
                else:
                    feedback_parts.append(f"{i}. {imp}")
            feedback_parts.append("")
        
        # Show red flags if meaningful
        red_flags = llm_eval.get('red_flags', []) or evaluation.get('red_flags', [])
        meaningful_flags = [f for f in red_flags if f and f != 'None identified']
        
        feedback_parts.append("RED FLAGS:")
        if meaningful_flags:
            for flag in meaningful_flags[:5]:
                feedback_parts.append(f"- {flag}")
        else:
            feedback_parts.append("None identified")
        feedback_parts.append("")
        
        # Show hiring recommendation
        hiring_rec = evaluation.get('hiring_recommendation', 'Maybe')
        if hiring_rec and hiring_rec not in ['Unknown', '']:
            feedback_parts.append("HIRING RECOMMENDATION:")
            feedback_parts.append(hiring_rec)
            feedback_parts.append("")
        
        # Add layer breakdown
        expert_data = layer_scores.get('layer3_expert', {})
        matched = expert_data.get('matched_elements', [])
        missing = expert_data.get('missing_elements', [])
        
        feedback_parts.append("--- SCORE BREAKDOWN ---")
        feedback_parts.append(f"Structure (Rule-Based): {layer_scores.get('layer1_rule_based', {}).get('score', 'N/A')}/5")
        feedback_parts.append(f"Quality (LLM Evaluation): {layer_scores.get('layer2_llm', {}).get('score', 'N/A')}/5")
        feedback_parts.append(f"Expert Match: {layer_scores.get('layer3_expert', {}).get('score', 'N/A')}/5 (compared to ideal response)")
        
        if matched or missing:
            feedback_parts.append("")
            if matched:
                feedback_parts.append(f"  [+] Matched: {', '.join(matched[:3])}")
            if missing:
                feedback_parts.append(f"  [-] Missing: {', '.join(missing[:3])}")
        
        return "\n".join(feedback_parts)

    def _generate_final_report(self) -> Dict:
        """Generate comprehensive final report"""
        
        # Calculate overall metrics
        all_scores = []
        for skill, scores_list in self.skill_scores.items():
            all_scores.extend([s['score'] for s in scores_list])
        
        overall_average = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Skill breakdown
        skill_summary = {}
        for skill, scores_list in self.skill_scores.items():
            avg_score = sum(s['score'] for s in scores_list) / len(scores_list)
            avg_confidence = sum(s['confidence'] for s in scores_list) / len(scores_list)
            
            # Performance level
            if avg_score >= 20:
                level = "Excellent"
                color = "#10b981"
            elif avg_score >= 15:
                level = "Strong"
                color = "#3b82f6"
            elif avg_score >= 10:
                level = "Competent"
                color = "#f59e0b"
            else:
                level = "Developing"
                color = "#ef4444"
            
            skill_summary[skill] = {
                "skill_name": skill.replace('_', ' ').title(),
                "average_score": round(avg_score, 1),
                "max_score": 25,
                "percentage": round((avg_score / 25) * 100, 1),
                "confidence": round(avg_confidence, 2),
                "level": level,
                "color": color,
                "num_responses": len(scores_list),
                "responses": scores_list
            }
        
        # Interview duration
        duration_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        
        # Overall performance level
        if overall_average >= 20:
            overall_level = "Outstanding"
        elif overall_average >= 15:
            overall_level = "Strong Candidate"
        elif overall_average >= 10:
            overall_level = "Qualified"
        else:
            overall_level = "Needs Development"
        
        report = {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "interview_date": self.start_time.strftime("%Y-%m-%d"),
            "interview_time": self.start_time.strftime("%H:%M"),
            "duration_minutes": round(duration_minutes, 1),
            
            "overall_performance": {
                "average_score": round(overall_average, 1),
                "max_score": 25,
                "percentage": round((overall_average / 25) * 100, 1),
                "level": overall_level
            },
            
            "skill_breakdown": skill_summary,
            
            "responses": [resp for scores in self.skill_scores.values() for resp in scores],
            
            "statistics": {
                "total_questions": len(self.target_skills),
                "total_responses": len(all_scores),
                "avg_response_length": round(
                    sum(s['word_count'] for scores in self.skill_scores.values() for s in scores) / len(all_scores),
                    0
                ) if all_scores else 0
            },
            
            "recommendations": self._generate_recommendations(skill_summary, overall_average),
            
            "generated_at": datetime.now().isoformat()
        }
        
        return report
        
    def _generate_recommendations(self, skill_summary: Dict, overall_avg: float) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Skill-specific recommendations
        for skill, data in skill_summary.items():
            if data['average_score'] < 15:
                recommendations.append(
                    f"{data['skill_name']}: Consider practicing STAR-format responses "
                    f"with specific, measurable examples from your experience."
                )
        
        # Overall recommendations
        if overall_avg >= 20:
            recommendations.append(
                "Overall: Excellent performance! You're well-prepared for senior cybersecurity roles. "
                "Continue refining your ability to quantify impact."
            )
        elif overall_avg >= 15:
            recommendations.append(
                "Overall: Strong performance! Focus on adding more measurable outcomes to your responses."
            )
        else:
            recommendations.append(
                "Overall: Practice structuring responses with the STAR framework and include "
                "specific metrics wherever possible."
            )
        
        return recommendations
    
    def _handle_followup_response(self, user_input: str) -> Dict:
        """Handle follow-up question responses"""
        return self._handle_question_response(user_input)
    
    def _log_message(self, role: str, content):
        """Log message to conversation history"""
        
        if isinstance(content, dict):
            message = content
        else:
            message = {"role": role, "content": content}
        
        message["timestamp"] = datetime.now().isoformat()
        self.conversation_history.append(message)
    
    def _get_completion_message(self) -> Dict:
        """Return completion message if interview already completed"""
        return {
            "type": "completed",
            "content": "This interview has already been completed. Thank you!",
            "final_report": self._generate_final_report()
        }
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "state": self.state.value,
            "current_skill_index": self.current_skill_index,
            "total_skills": len(self.target_skills),
            "questions_asked": len(self.questions_asked),
            "start_time": self.start_time.isoformat()
        }
