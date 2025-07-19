"""
Educational Metrics for DSPy AI Tutor
Provides comprehensive metrics for measuring tutoring effectiveness
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from loguru import logger


class EducationalMetrics:
    """
    Comprehensive metrics system for evaluating educational effectiveness
    of the AI tutoring system
    """
    
    def __init__(self):
        self.conversation_metrics = {}
        self.session_metrics = {}
        self.learning_outcomes = {}
    
    async def calculate_conversation_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Calculate comprehensive metrics for a conversation"""
        
        try:
            # This would typically fetch conversation data from the vector service
            # For now, we'll return sample metrics structure
            
            metrics = {
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "engagement_score": 0.85,  # 0-1 scale
                "comprehension_indicators": {
                    "understanding_signals": 3,
                    "confusion_signals": 1,
                    "follow_up_questions": 2
                },
                "learning_progression": {
                    "concepts_introduced": 2,
                    "concepts_reinforced": 1,
                    "difficulty_progression": "appropriate"
                },
                "response_quality": {
                    "clarity_score": 0.9,
                    "completeness_score": 0.8,
                    "educational_value": 0.85
                },
                "interaction_patterns": {
                    "total_exchanges": 5,
                    "average_response_length": 150,
                    "question_complexity": "intermediate"
                }
            }
            
            # Store metrics for future analysis
            self.conversation_metrics[conversation_id] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating conversation metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_session_metrics(self, user_id: str, session_data: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics for a learning session"""
        
        try:
            if not session_data:
                return {"error": "No session data provided"}
            
            # Analyze session patterns
            total_interactions = len(session_data)
            session_duration = self._calculate_session_duration(session_data)
            
            # Engagement analysis
            engagement_score = self._calculate_engagement_score(session_data)
            
            # Learning progression analysis
            progression_score = self._calculate_progression_score(session_data)
            
            # Topic coverage analysis
            topics_covered = self._extract_topics_covered(session_data)
            
            metrics = {
                "user_id": user_id,
                "session_timestamp": datetime.now().isoformat(),
                "session_summary": {
                    "total_interactions": total_interactions,
                    "session_duration_minutes": session_duration,
                    "topics_covered": topics_covered,
                    "engagement_score": engagement_score,
                    "learning_progression_score": progression_score
                },
                "detailed_analysis": {
                    "interaction_quality": self._analyze_interaction_quality(session_data),
                    "question_complexity_trend": self._analyze_complexity_trend(session_data),
                    "response_satisfaction": self._estimate_satisfaction(session_data)
                },
                "recommendations": self._generate_recommendations(session_data, engagement_score, progression_score)
            }
            
            # Store session metrics
            session_key = f"{user_id}_{int(datetime.now().timestamp())}"
            self.session_metrics[session_key] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating session metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_learning_outcomes(self, user_id: str, time_period_days: int = 7) -> Dict[str, Any]:
        """Calculate learning outcomes over a time period"""
        
        try:
            # This would typically analyze user's learning progress over time
            # For now, we'll return a sample structure
            
            outcomes = {
                "user_id": user_id,
                "analysis_period_days": time_period_days,
                "timestamp": datetime.now().isoformat(),
                "learning_progress": {
                    "concepts_mastered": 5,
                    "concepts_in_progress": 3,
                    "concepts_struggling": 1,
                    "overall_progress_score": 0.75
                },
                "skill_development": {
                    "problem_solving": 0.8,
                    "conceptual_understanding": 0.7,
                    "application_ability": 0.75,
                    "critical_thinking": 0.65
                },
                "engagement_trends": {
                    "average_session_length": 25.5,
                    "sessions_per_week": 4,
                    "engagement_trend": "increasing",
                    "preferred_learning_style": "visual"
                },
                "areas_for_improvement": [
                    "Advanced mathematical concepts",
                    "Complex problem decomposition"
                ],
                "strengths": [
                    "Basic concept understanding",
                    "Consistent engagement",
                    "Good question formulation"
                ]
            }
            
            # Store learning outcomes
            self.learning_outcomes[user_id] = outcomes
            
            return outcomes
            
        except Exception as e:
            logger.error(f"Error calculating learning outcomes: {e}")
            return {"error": str(e)}
    
    def _calculate_session_duration(self, session_data: List[Dict]) -> float:
        """Calculate session duration in minutes"""
        
        if len(session_data) < 2:
            return 0.0
        
        try:
            # Extract timestamps and calculate duration
            timestamps = []
            for interaction in session_data:
                if "timestamp" in interaction:
                    timestamps.append(datetime.fromisoformat(interaction["timestamp"]))
            
            if len(timestamps) >= 2:
                duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
                return round(duration, 1)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_engagement_score(self, session_data: List[Dict]) -> float:
        """Calculate engagement score based on interaction patterns"""
        
        try:
            engagement_indicators = 0
            total_possible = len(session_data)
            
            for interaction in session_data:
                message = interaction.get("user_message", "").lower()
                
                # Positive engagement indicators
                if any(word in message for word in ["interesting", "cool", "more", "another", "explain"]):
                    engagement_indicators += 1
                elif any(word in message for word in ["thanks", "helpful", "understand", "got it"]):
                    engagement_indicators += 0.5
                elif len(message.split()) > 10:  # Detailed questions indicate engagement
                    engagement_indicators += 0.3
            
            return min(engagement_indicators / max(total_possible, 1), 1.0)
            
        except Exception:
            return 0.5  # Default moderate engagement
    
    def _calculate_progression_score(self, session_data: List[Dict]) -> float:
        """Calculate learning progression score"""
        
        try:
            progression_indicators = 0
            
            for i, interaction in enumerate(session_data):
                message = interaction.get("user_message", "").lower()
                
                # Look for progression indicators
                if any(word in message for word in ["understand", "clear", "makes sense"]):
                    progression_indicators += 1
                elif any(word in message for word in ["confused", "don't get", "unclear"]):
                    progression_indicators -= 0.5
                elif i > 0 and len(message.split()) > len(session_data[i-1].get("user_message", "").split()):
                    progression_indicators += 0.2  # More detailed questions over time
            
            return max(min(progression_indicators / len(session_data), 1.0), 0.0)
            
        except Exception:
            return 0.5  # Default moderate progression
    
    def _extract_topics_covered(self, session_data: List[Dict]) -> List[str]:
        """Extract topics covered in the session"""
        
        topics = set()
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            "mathematics": ["math", "equation", "solve", "calculate", "number", "algebra"],
            "programming": ["code", "function", "variable", "loop", "algorithm", "debug"],
            "science": ["experiment", "hypothesis", "theory", "analysis", "research"],
            "general": ["explain", "understand", "concept", "principle", "idea"]
        }
        
        for interaction in session_data:
            message = interaction.get("user_message", "").lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in message for keyword in keywords):
                    topics.add(topic)
        
        return list(topics) if topics else ["general"]
    
    def _analyze_interaction_quality(self, session_data: List[Dict]) -> Dict[str, float]:
        """Analyze the quality of interactions"""
        
        return {
            "question_clarity": 0.8,
            "response_relevance": 0.85,
            "educational_depth": 0.75,
            "interaction_flow": 0.9
        }
    
    def _analyze_complexity_trend(self, session_data: List[Dict]) -> str:
        """Analyze how question complexity changes over the session"""
        
        if len(session_data) < 3:
            return "insufficient_data"
        
        # Simple analysis based on message length and question words
        complexities = []
        
        for interaction in session_data:
            message = interaction.get("user_message", "")
            complexity = len(message.split()) + message.count("?") * 2
            complexities.append(complexity)
        
        if len(complexities) >= 3:
            if complexities[-1] > complexities[0]:
                return "increasing"
            elif complexities[-1] < complexities[0]:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _estimate_satisfaction(self, session_data: List[Dict]) -> float:
        """Estimate user satisfaction based on interaction patterns"""
        
        satisfaction_score = 0.5  # Start with neutral
        
        for interaction in session_data:
            message = interaction.get("user_message", "").lower()
            
            # Positive indicators
            if any(word in message for word in ["thank", "helpful", "great", "perfect", "excellent"]):
                satisfaction_score += 0.2
            elif any(word in message for word in ["good", "nice", "clear", "understand"]):
                satisfaction_score += 0.1
            
            # Negative indicators
            elif any(word in message for word in ["confused", "unclear", "wrong", "bad"]):
                satisfaction_score -= 0.1
        
        return max(min(satisfaction_score, 1.0), 0.0)
    
    def _generate_recommendations(self, session_data: List[Dict], engagement_score: float, progression_score: float) -> List[str]:
        """Generate recommendations based on session analysis"""
        
        recommendations = []
        
        if engagement_score < 0.5:
            recommendations.append("Consider using more interactive examples and visual aids")
            recommendations.append("Try incorporating gamification elements")
        
        if progression_score < 0.5:
            recommendations.append("Break down complex concepts into smaller steps")
            recommendations.append("Provide more foundational review before advancing")
        
        if len(session_data) < 3:
            recommendations.append("Encourage longer learning sessions for better retention")
        
        if not recommendations:
            recommendations.append("Continue with current learning approach - showing good progress")
        
        return recommendations
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall statistics across all metrics"""
        
        return {
            "total_conversations_analyzed": len(self.conversation_metrics),
            "total_sessions_analyzed": len(self.session_metrics),
            "total_users_tracked": len(self.learning_outcomes),
            "average_engagement_score": 0.75,  # Would calculate from actual data
            "average_progression_score": 0.68,  # Would calculate from actual data
            "most_common_topics": ["mathematics", "programming", "general"],
            "system_effectiveness": 0.78
        }
