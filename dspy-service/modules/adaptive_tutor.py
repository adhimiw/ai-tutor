"""
Adaptive Tutoring Module using DSPy
Personalizes learning based on student performance and learning patterns
"""

import dspy
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json


class StudentProfile(BaseModel):
    """Student learning profile"""
    comprehension_level: str = "intermediate"
    learning_style: str = "visual"
    knowledge_gaps: List[str] = []
    strengths: List[str] = []
    preferred_difficulty: str = "moderate"
    engagement_level: str = "medium"


class AdaptiveTutor(dspy.Module):
    """
    Adaptive tutoring module that personalizes responses based on student performance
    and learning patterns using DSPy's systematic optimization
    """
    
    def __init__(self):
        super().__init__()
        
        # Student assessment from conversation history
        self.assess_student = dspy.ChainOfThought(
            "conversation_history, performance_indicators -> comprehension_level, learning_style, knowledge_gaps, strengths"
        )
        
        # Learning path recommendation
        self.recommend_path = dspy.ChainOfThought(
            "student_profile, current_topic, learning_objectives -> personalized_path, difficulty_adjustment, focus_areas"
        )
        
        # Adaptive response generation
        self.adaptive_respond = dspy.ChainOfThought(
            "question, student_profile, context -> personalized_response, explanation_style, engagement_techniques"
        )
        
        # Progress tracking and adjustment
        self.track_progress = dspy.Predict(
            "previous_assessment, current_interaction, response_quality -> updated_profile, progress_indicators, next_adjustments"
        )
        
        # Motivation and engagement enhancement
        self.enhance_engagement = dspy.ChainOfThought(
            "student_profile, current_mood, topic_difficulty -> motivation_techniques, encouragement, gamification_elements"
        )
    
    def forward(self, question: str, context: List[Dict] = None, user_id: str = "anonymous", 
                current_topic: str = "general", **kwargs):
        """
        Generate adaptive tutoring response based on student's learning profile
        
        Args:
            question: Student's question
            context: Conversation history and context
            user_id: Student identifier for personalization
            current_topic: Current learning topic
        """
        
        try:
            # Prepare conversation history for analysis
            conversation_history = self._prepare_conversation_history(context)
            
            # Assess student's current state
            assessment = self.assess_student(
                conversation_history=conversation_history,
                performance_indicators=self._extract_performance_indicators(context)
            )
            
            # Create student profile
            student_profile = self._create_student_profile(assessment)
            
            # Get learning path recommendations
            learning_path = self.recommend_path(
                student_profile=str(student_profile),
                current_topic=current_topic,
                learning_objectives=kwargs.get('learning_objectives', 'general understanding')
            )
            
            # Generate adaptive response
            adaptive_response = self.adaptive_respond(
                question=question,
                student_profile=str(student_profile),
                context=conversation_history
            )
            
            # Enhance engagement based on student profile
            engagement = self.enhance_engagement(
                student_profile=str(student_profile),
                current_mood=kwargs.get('mood', 'neutral'),
                topic_difficulty=getattr(learning_path, 'difficulty_adjustment', 'moderate')
            )
            
            # Construct comprehensive response
            response = self._construct_adaptive_response(
                adaptive_response, learning_path, engagement, student_profile
            )
            
            # Track progress for future interactions
            progress_update = self.track_progress(
                previous_assessment=str(student_profile),
                current_interaction=f"Q: {question} A: {getattr(adaptive_response, 'personalized_response', '')}",
                response_quality=kwargs.get('response_quality', 'good')
            )
            
            return dspy.Prediction(
                response=response,
                explanation=getattr(adaptive_response, 'explanation_style', 'Standard explanation'),
                next_steps=self._generate_next_steps(learning_path, student_profile),
                student_profile=student_profile.dict(),
                learning_path=getattr(learning_path, 'personalized_path', 'Continue current topic'),
                engagement_techniques=getattr(engagement, 'engagement_techniques', 'Standard approach'),
                progress_update=getattr(progress_update, 'progress_indicators', 'No update available')
            )
            
        except Exception as e:
            print(f"Adaptive tutor error: {e}")
            return self._fallback_response(question, context)
    
    def _prepare_conversation_history(self, context: List[Dict]) -> str:
        """Prepare conversation history for analysis"""
        if not context:
            return "No previous conversation history available."
        
        history_parts = []
        for item in context[-10:]:  # Last 10 interactions
            user_msg = item.get('user_message', item.get('message', ''))
            ai_response = item.get('ai_response', item.get('response', ''))
            
            if user_msg and ai_response:
                history_parts.append(f"Student: {user_msg}")
                history_parts.append(f"Tutor: {ai_response[:200]}...")  # Truncate long responses
                history_parts.append("---")
        
        return '\n'.join(history_parts) if history_parts else "No conversation history available."
    
    def _extract_performance_indicators(self, context: List[Dict]) -> str:
        """Extract performance indicators from conversation context"""
        if not context:
            return "No performance data available."
        
        indicators = []
        
        # Analyze recent interactions for performance signals
        for item in context[-5:]:  # Last 5 interactions
            user_msg = item.get('user_message', '').lower()
            
            # Look for confusion indicators
            if any(word in user_msg for word in ['confused', 'don\'t understand', 'unclear', 'help']):
                indicators.append("Shows confusion or need for clarification")
            
            # Look for confidence indicators
            if any(word in user_msg for word in ['got it', 'understand', 'clear', 'makes sense']):
                indicators.append("Shows understanding and confidence")
            
            # Look for engagement indicators
            if any(word in user_msg for word in ['interesting', 'cool', 'more', 'another']):
                indicators.append("Shows high engagement")
            
            # Look for difficulty indicators
            if any(word in user_msg for word in ['hard', 'difficult', 'challenging', 'struggle']):
                indicators.append("Finds content challenging")
        
        return '; '.join(indicators) if indicators else "Neutral performance indicators"
    
    def _create_student_profile(self, assessment) -> StudentProfile:
        """Create structured student profile from assessment"""
        
        comprehension_level = getattr(assessment, 'comprehension_level', 'intermediate')
        learning_style = getattr(assessment, 'learning_style', 'visual')
        knowledge_gaps = getattr(assessment, 'knowledge_gaps', 'none identified')
        strengths = getattr(assessment, 'strengths', 'general problem solving')
        
        # Parse knowledge gaps and strengths into lists
        gaps_list = [gap.strip() for gap in knowledge_gaps.split(',') if gap.strip()]
        strengths_list = [strength.strip() for strength in strengths.split(',') if strength.strip()]
        
        return StudentProfile(
            comprehension_level=comprehension_level,
            learning_style=learning_style,
            knowledge_gaps=gaps_list,
            strengths=strengths_list,
            preferred_difficulty=self._map_comprehension_to_difficulty(comprehension_level),
            engagement_level="medium"  # Default, could be enhanced with more analysis
        )
    
    def _map_comprehension_to_difficulty(self, comprehension_level: str) -> str:
        """Map comprehension level to preferred difficulty"""
        mapping = {
            'beginner': 'easy',
            'elementary': 'easy',
            'intermediate': 'moderate',
            'advanced': 'challenging',
            'expert': 'challenging'
        }
        return mapping.get(comprehension_level.lower(), 'moderate')
    
    def _construct_adaptive_response(self, adaptive_response, learning_path, engagement, student_profile):
        """Construct comprehensive adaptive response"""
        
        personalized_response = getattr(adaptive_response, 'personalized_response', 'No response generated')
        explanation_style = getattr(adaptive_response, 'explanation_style', 'standard')
        engagement_techniques = getattr(engagement, 'engagement_techniques', 'standard approach')
        motivation_techniques = getattr(engagement, 'motivation_techniques', 'general encouragement')
        
        response_parts = [
            f"**Personalized Response** (adapted for {student_profile.learning_style} learner):",
            personalized_response,
            ""
        ]
        
        # Add learning style specific elements
        if student_profile.learning_style == 'visual':
            response_parts.extend([
                "**Visual Learning Tip:** Try drawing diagrams or creating visual representations of this concept.",
                ""
            ])
        elif student_profile.learning_style == 'auditory':
            response_parts.extend([
                "**Auditory Learning Tip:** Try explaining this concept out loud or discussing it with others.",
                ""
            ])
        elif student_profile.learning_style == 'kinesthetic':
            response_parts.extend([
                "**Hands-on Learning Tip:** Try to find practical applications or hands-on activities related to this topic.",
                ""
            ])
        
        # Add motivation if needed
        if motivation_techniques and motivation_techniques != 'general encouragement':
            response_parts.extend([
                f"**Encouragement:** {motivation_techniques}",
                ""
            ])
        
        # Add difficulty adjustment note
        difficulty_adjustment = getattr(learning_path, 'difficulty_adjustment', 'moderate')
        if difficulty_adjustment != 'moderate':
            response_parts.extend([
                f"**Note:** I've adjusted the explanation to be more {difficulty_adjustment} based on your learning profile.",
                ""
            ])
        
        return '\n'.join(response_parts)
    
    def _generate_next_steps(self, learning_path, student_profile: StudentProfile) -> List[str]:
        """Generate personalized next steps"""
        
        base_steps = []
        
        # Add steps based on learning path
        personalized_path = getattr(learning_path, 'personalized_path', '')
        if personalized_path:
            base_steps.append(f"Follow your personalized learning path: {personalized_path}")
        
        # Add steps based on knowledge gaps
        if student_profile.knowledge_gaps:
            base_steps.append(f"Focus on strengthening: {', '.join(student_profile.knowledge_gaps[:2])}")
        
        # Add steps based on learning style
        if student_profile.learning_style == 'visual':
            base_steps.append("Create visual aids or diagrams to reinforce understanding")
        elif student_profile.learning_style == 'auditory':
            base_steps.append("Practice explaining concepts verbally")
        elif student_profile.learning_style == 'kinesthetic':
            base_steps.append("Find hands-on activities or real-world applications")
        
        # Add general steps
        base_steps.extend([
            "Practice with similar problems at your current level",
            "Ask follow-up questions if anything is unclear"
        ])
        
        return base_steps[:5]  # Limit to 5 steps
    
    def _fallback_response(self, question: str, context: List[Dict] = None):
        """Fallback response when adaptive processing fails"""
        
        return dspy.Prediction(
            response=f"I understand you're asking: {question}\n\n"
                    "I'm working to provide you with a personalized learning experience. "
                    "While I analyze your learning patterns, let me help you with this question.\n\n"
                    "To better adapt to your learning style, please let me know:\n"
                    "- Do you prefer visual, auditory, or hands-on explanations?\n"
                    "- What's your current level with this topic?\n"
                    "- Are there specific areas you find challenging?",
            explanation="Adaptive tutoring system is learning about your preferences",
            next_steps=[
                "Share your preferred learning style",
                "Indicate your comfort level with the topic",
                "Ask specific questions about challenging areas",
                "Continue our conversation to help me understand your needs better"
            ],
            student_profile={
                "comprehension_level": "intermediate",
                "learning_style": "unknown",
                "knowledge_gaps": [],
                "strengths": [],
                "preferred_difficulty": "moderate"
            }
        )
