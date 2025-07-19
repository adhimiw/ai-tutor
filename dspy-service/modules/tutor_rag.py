"""
Enhanced RAG Module for AI Tutoring using DSPy
Replaces the current vectorMemoryService.js with optimizable DSPy components
"""

import dspy
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TutorResponse(BaseModel):
    """Structured response from the tutor"""
    response: str
    explanation: Optional[str] = None
    next_steps: Optional[List[str]] = None
    confidence: Optional[float] = None
    sources: Optional[List[str]] = None


class TutorRAG(dspy.Module):
    """
    Enhanced RAG module for AI tutoring that replaces manual prompt engineering
    with systematic DSPy optimization
    """
    
    def __init__(self, k: int = 5):
        super().__init__()
        self.k = k
        
        # Initialize retriever (will be configured with vector service)
        self.retrieve = None  # Will be set by vector service
        
        # Core tutoring module with structured output
        self.respond = dspy.ChainOfThought(
            "context, question, difficulty_level -> response, explanation, next_steps"
        )
        
        # Confidence assessment module
        self.assess_confidence = dspy.Predict(
            "question, response, context -> confidence: float"
        )
        
        # Source attribution module
        self.attribute_sources = dspy.Predict(
            "context, response -> sources: List[str]"
        )
    
    def set_retriever(self, retriever):
        """Set the retriever component"""
        self.retrieve = retriever
    
    def forward(self, question: str, context: List[Dict] = None, difficulty_level: str = "intermediate", **kwargs):
        """
        Forward pass through the tutoring pipeline
        
        Args:
            question: Student's question
            context: Previous conversation context
            difficulty_level: Student's current level (beginner, intermediate, advanced)
            **kwargs: Additional context parameters
        """
        
        # Retrieve relevant information if retriever is available
        retrieved_context = ""
        sources = []
        
        if self.retrieve:
            try:
                retrieval_results = self.retrieve(question, k=self.k)
                if hasattr(retrieval_results, 'passages'):
                    retrieved_context = "\n".join([
                        f"[{i+1}] {passage}" 
                        for i, passage in enumerate(retrieval_results.passages[:self.k])
                    ])
                    sources = [f"Source {i+1}" for i in range(len(retrieval_results.passages[:self.k]))]
            except Exception as e:
                print(f"Retrieval error: {e}")
                retrieved_context = ""
        
        # Prepare conversation context
        conversation_context = ""
        if context:
            conversation_context = "\n".join([
                f"Previous: {item.get('message', '')}" 
                for item in context[-3:]  # Last 3 exchanges
            ])
        
        # Combine all context
        full_context = f"""
Retrieved Information:
{retrieved_context}

Conversation History:
{conversation_context}

Student Level: {difficulty_level}
""".strip()
        
        # Generate structured response
        try:
            result = self.respond(
                context=full_context,
                question=question,
                difficulty_level=difficulty_level
            )
            
            # Assess confidence in the response
            confidence_result = self.assess_confidence(
                question=question,
                response=result.response,
                context=full_context
            )
            
            # Attribute sources if we have retrieved context
            if retrieved_context and sources:
                source_result = self.attribute_sources(
                    context=retrieved_context,
                    response=result.response
                )
                sources = source_result.sources if hasattr(source_result, 'sources') else sources
            
            return dspy.Prediction(
                response=result.response,
                explanation=getattr(result, 'explanation', None),
                next_steps=getattr(result, 'next_steps', '').split('\n') if hasattr(result, 'next_steps') else None,
                confidence=float(confidence_result.confidence) if hasattr(confidence_result, 'confidence') else None,
                sources=sources
            )
            
        except Exception as e:
            print(f"Response generation error: {e}")
            # Fallback response
            return dspy.Prediction(
                response=f"I understand you're asking about: {question}. Let me help you with that.",
                explanation="This is a fallback response due to processing error.",
                next_steps=["Please try rephrasing your question", "Provide more specific details"],
                confidence=0.5,
                sources=[]
            )


class ContextualTutorRAG(dspy.Module):
    """
    Advanced RAG module that adapts responses based on student performance history
    """
    
    def __init__(self, k: int = 5):
        super().__init__()
        self.k = k
        self.retrieve = None
        
        # Student assessment module
        self.assess_student = dspy.ChainOfThought(
            "conversation_history, current_question -> comprehension_level, learning_style, knowledge_gaps"
        )
        
        # Adaptive response generation
        self.adaptive_respond = dspy.ChainOfThought(
            "context, question, student_assessment -> response, explanation, personalized_next_steps"
        )
    
    def set_retriever(self, retriever):
        """Set the retriever component"""
        self.retrieve = retriever
    
    def forward(self, question: str, context: List[Dict] = None, user_id: str = None, **kwargs):
        """
        Generate adaptive response based on student's learning profile
        """
        
        # Retrieve relevant information
        retrieved_context = ""
        if self.retrieve:
            try:
                retrieval_results = self.retrieve(question, k=self.k)
                if hasattr(retrieval_results, 'passages'):
                    retrieved_context = "\n".join(retrieval_results.passages[:self.k])
            except Exception as e:
                print(f"Retrieval error: {e}")
        
        # Assess student based on conversation history
        conversation_history = ""
        if context:
            conversation_history = "\n".join([
                f"Q: {item.get('user_message', '')} A: {item.get('ai_response', '')}"
                for item in context[-5:]  # Last 5 exchanges
            ])
        
        student_assessment = self.assess_student(
            conversation_history=conversation_history,
            current_question=question
        )
        
        # Generate adaptive response
        result = self.adaptive_respond(
            context=retrieved_context,
            question=question,
            student_assessment=f"""
            Comprehension Level: {getattr(student_assessment, 'comprehension_level', 'intermediate')}
            Learning Style: {getattr(student_assessment, 'learning_style', 'visual')}
            Knowledge Gaps: {getattr(student_assessment, 'knowledge_gaps', 'none identified')}
            """
        )
        
        return dspy.Prediction(
            response=result.response,
            explanation=getattr(result, 'explanation', None),
            next_steps=getattr(result, 'personalized_next_steps', '').split('\n') if hasattr(result, 'personalized_next_steps') else None,
            student_assessment={
                'comprehension_level': getattr(student_assessment, 'comprehension_level', 'intermediate'),
                'learning_style': getattr(student_assessment, 'learning_style', 'visual'),
                'knowledge_gaps': getattr(student_assessment, 'knowledge_gaps', 'none identified')
            }
        )


class MultiModalTutorRAG(dspy.Module):
    """
    RAG module enhanced for multimodal inputs (text + images/documents)
    """
    
    def __init__(self, k: int = 5):
        super().__init__()
        self.k = k
        self.retrieve = None
        
        # Multimodal content analysis
        self.analyze_content = dspy.ChainOfThought(
            "text_content, file_descriptions, question -> content_summary, key_concepts, educational_focus"
        )
        
        # Multimodal response generation
        self.multimodal_respond = dspy.ChainOfThought(
            "context, content_analysis, question -> response, visual_explanations, practice_suggestions"
        )
    
    def set_retriever(self, retriever):
        """Set the retriever component"""
        self.retrieve = retriever
    
    def forward(self, question: str, files_content: List[Dict] = None, context: List[Dict] = None, **kwargs):
        """
        Generate response incorporating multimodal content
        """
        
        # Retrieve relevant information
        retrieved_context = ""
        if self.retrieve:
            try:
                retrieval_results = self.retrieve(question, k=self.k)
                if hasattr(retrieval_results, 'passages'):
                    retrieved_context = "\n".join(retrieval_results.passages[:self.k])
            except Exception as e:
                print(f"Retrieval error: {e}")
        
        # Analyze uploaded content
        content_analysis = None
        if files_content:
            file_descriptions = "\n".join([
                f"File: {file.get('name', 'unknown')} - Type: {file.get('type', 'unknown')} - Content: {file.get('content', 'No content')[:500]}..."
                for file in files_content
            ])
            
            content_analysis = self.analyze_content(
                text_content=retrieved_context,
                file_descriptions=file_descriptions,
                question=question
            )
        
        # Generate multimodal response
        result = self.multimodal_respond(
            context=retrieved_context,
            content_analysis=str(content_analysis) if content_analysis else "No file content provided",
            question=question
        )
        
        return dspy.Prediction(
            response=result.response,
            explanation=getattr(result, 'visual_explanations', None),
            next_steps=getattr(result, 'practice_suggestions', '').split('\n') if hasattr(result, 'practice_suggestions') else None,
            content_analysis=content_analysis
        )
