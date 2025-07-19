"""
Specialized Programming/Code Tutoring Module using DSPy
Handles code review, debugging, and programming education
"""

import dspy
import re
import ast
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CodeAnalysis(BaseModel):
    """Structured code analysis response"""
    code_quality: str
    issues_found: List[str]
    suggestions: List[str]
    improved_code: Optional[str] = None
    explanation: str
    learning_resources: List[str]


class CodeTutor(dspy.Module):
    """
    Specialized DSPy module for programming tutoring and code review
    Uses ReAct approach for systematic code analysis and improvement
    """
    
    def __init__(self):
        super().__init__()
        
        # Code analysis and classification
        self.analyze_code = dspy.ChainOfThought(
            "code, language, context -> code_quality, complexity_level, main_concepts, potential_issues"
        )
        
        # Code review and improvement suggestions
        self.review_code = dspy.ChainOfThought(
            "code, analysis, requirements -> detailed_review, improvement_suggestions, best_practices"
        )
        
        # Code improvement generation
        self.improve_code = dspy.ChainOfThought(
            "original_code, issues, suggestions -> improved_code, explanation_of_changes, learning_points"
        )
        
        # Programming concept explanation
        self.explain_concepts = dspy.ChainOfThought(
            "code_concepts, student_level, programming_language -> concept_explanation, examples, practice_exercises"
        )
        
        # Debugging assistance
        self.debug_code = dspy.ChainOfThought(
            "code, error_message, expected_behavior -> debugging_steps, root_cause, solution"
        )
    
    def forward(self, question: str, code: str = "", language: str = "python", 
                context: str = "", error_message: str = "", **kwargs):
        """
        Provide programming tutoring and code assistance
        
        Args:
            question: Programming question or request
            code: Code snippet to analyze (if provided)
            language: Programming language
            context: Additional context about the code's purpose
            error_message: Error message if debugging
        """
        
        try:
            # Determine the type of assistance needed
            assistance_type = self._determine_assistance_type(question, code, error_message)
            
            if assistance_type == "debugging" and error_message:
                return self._handle_debugging(question, code, error_message, language)
            elif assistance_type == "code_review" and code:
                return self._handle_code_review(question, code, language, context)
            elif assistance_type == "concept_explanation":
                return self._handle_concept_explanation(question, language, kwargs.get('student_level', 'intermediate'))
            else:
                return self._handle_general_programming(question, code, language, context)
                
        except Exception as e:
            print(f"Code tutor error: {e}")
            return self._fallback_response(question, code)
    
    def _determine_assistance_type(self, question: str, code: str, error_message: str) -> str:
        """Determine what type of programming assistance is needed"""
        question_lower = question.lower()
        
        if error_message or "error" in question_lower or "debug" in question_lower:
            return "debugging"
        elif code and ("review" in question_lower or "improve" in question_lower or "better" in question_lower):
            return "code_review"
        elif not code and ("explain" in question_lower or "what is" in question_lower or "how does" in question_lower):
            return "concept_explanation"
        else:
            return "general_programming"
    
    def _handle_debugging(self, question: str, code: str, error_message: str, language: str):
        """Handle debugging assistance"""
        
        # Analyze the code first
        analysis = self.analyze_code(
            code=code,
            language=language,
            context=f"Debugging: {error_message}"
        )
        
        # Debug the specific issue
        debug_result = self.debug_code(
            code=code,
            error_message=error_message,
            expected_behavior=question
        )
        
        debugging_steps = getattr(debug_result, 'debugging_steps', 'No debugging steps generated')
        root_cause = getattr(debug_result, 'root_cause', 'Unable to determine root cause')
        solution = getattr(debug_result, 'solution', 'No solution provided')
        
        response = f"""**Debugging Analysis**

**Error:** {error_message}

**Root Cause:**
{root_cause}

**Debugging Steps:**
{debugging_steps}

**Solution:**
{solution}

**Code Quality Assessment:**
- Complexity: {getattr(analysis, 'complexity_level', 'Unknown')}
- Main Concepts: {getattr(analysis, 'main_concepts', 'Not analyzed')}
"""
        
        return dspy.Prediction(
            response=response,
            explanation=f"The error occurs because: {root_cause}",
            next_steps=[
                "Apply the suggested solution",
                "Test the fixed code",
                "Review similar error patterns",
                "Practice defensive programming"
            ],
            debugging_steps=debugging_steps.split('\n') if isinstance(debugging_steps, str) else [debugging_steps],
            root_cause=root_cause,
            solution=solution
        )
    
    def _handle_code_review(self, question: str, code: str, language: str, context: str):
        """Handle code review and improvement"""
        
        # Analyze the code
        analysis = self.analyze_code(
            code=code,
            language=language,
            context=context
        )
        
        # Perform detailed review
        review = self.review_code(
            code=code,
            analysis=str(analysis),
            requirements=question
        )
        
        # Generate improved code
        improvement = self.improve_code(
            original_code=code,
            issues=getattr(analysis, 'potential_issues', 'No issues identified'),
            suggestions=getattr(review, 'improvement_suggestions', 'No suggestions')
        )
        
        code_quality = getattr(analysis, 'code_quality', 'Good')
        detailed_review = getattr(review, 'detailed_review', 'No detailed review available')
        improvement_suggestions = getattr(review, 'improvement_suggestions', 'No suggestions')
        improved_code = getattr(improvement, 'improved_code', 'No improved version generated')
        explanation_of_changes = getattr(improvement, 'explanation_of_changes', 'No explanation available')
        
        response = f"""**Code Review Results**

**Overall Quality:** {code_quality}

**Detailed Analysis:**
{detailed_review}

**Improvement Suggestions:**
{improvement_suggestions}

**Improved Code:**
```{language}
{improved_code}
```

**Explanation of Changes:**
{explanation_of_changes}
"""
        
        return dspy.Prediction(
            response=response,
            explanation=explanation_of_changes,
            next_steps=[
                "Review the improved code",
                "Understand the changes made",
                "Apply similar patterns in future code",
                "Practice the suggested improvements"
            ],
            code_quality=code_quality,
            improved_code=improved_code,
            suggestions=improvement_suggestions.split('\n') if isinstance(improvement_suggestions, str) else [improvement_suggestions]
        )
    
    def _handle_concept_explanation(self, question: str, language: str, student_level: str):
        """Handle programming concept explanations"""
        
        # Extract concepts from the question
        concepts = self._extract_concepts(question)
        
        # Explain the concepts
        explanation = self.explain_concepts(
            code_concepts=concepts,
            student_level=student_level,
            programming_language=language
        )
        
        concept_explanation = getattr(explanation, 'concept_explanation', 'No explanation available')
        examples = getattr(explanation, 'examples', 'No examples provided')
        practice_exercises = getattr(explanation, 'practice_exercises', 'No exercises provided')
        
        response = f"""**Programming Concept Explanation**

**Topic:** {concepts}

**Explanation:**
{concept_explanation}

**Examples:**
{examples}

**Practice Exercises:**
{practice_exercises}
"""
        
        return dspy.Prediction(
            response=response,
            explanation=concept_explanation,
            next_steps=[
                "Try the practice exercises",
                "Experiment with the examples",
                "Apply the concept in a small project",
                "Ask follow-up questions if needed"
            ],
            concepts=concepts,
            examples=examples,
            practice_exercises=practice_exercises.split('\n') if isinstance(practice_exercises, str) else [practice_exercises]
        )
    
    def _handle_general_programming(self, question: str, code: str, language: str, context: str):
        """Handle general programming questions"""
        
        if code:
            # Analyze provided code
            analysis = self.analyze_code(
                code=code,
                language=language,
                context=context
            )
            
            response = f"""**Programming Assistance**

**Your Question:** {question}

**Code Analysis:**
- Quality: {getattr(analysis, 'code_quality', 'Not assessed')}
- Complexity: {getattr(analysis, 'complexity_level', 'Unknown')}
- Main Concepts: {getattr(analysis, 'main_concepts', 'Not identified')}

**Guidance:**
Based on your code and question, here's how I can help you improve and understand the programming concepts involved.

**Next Steps:**
1. Review the code structure and logic
2. Consider best practices for {language}
3. Think about edge cases and error handling
4. Practice similar problems to reinforce learning
"""
        else:
            response = f"""**Programming Guidance**

**Your Question:** {question}

**Approach:**
Let me help you understand this programming concept step by step.

**Recommended Learning Path:**
1. Start with the basic concepts
2. Look at simple examples
3. Practice with hands-on coding
4. Build small projects to apply knowledge

**Language Focus:** {language}

Would you like me to provide specific examples or code snippets to illustrate the concepts?
"""
        
        return dspy.Prediction(
            response=response,
            explanation="General programming guidance based on your question",
            next_steps=[
                "Provide more specific details about what you're trying to achieve",
                "Share any code you're working with",
                "Ask about specific programming concepts",
                "Request examples or practice problems"
            ]
        )
    
    def _extract_concepts(self, question: str) -> str:
        """Extract programming concepts from the question"""
        # Simple keyword extraction - could be enhanced with NLP
        concepts = []
        keywords = [
            'function', 'variable', 'loop', 'array', 'object', 'class', 'method',
            'recursion', 'algorithm', 'data structure', 'inheritance', 'polymorphism',
            'exception', 'async', 'promise', 'callback', 'closure', 'scope'
        ]
        
        question_lower = question.lower()
        for keyword in keywords:
            if keyword in question_lower:
                concepts.append(keyword)
        
        return ', '.join(concepts) if concepts else 'general programming'
    
    def _fallback_response(self, question: str, code: str = ""):
        """Fallback response when main processing fails"""
        return dspy.Prediction(
            response=f"I understand you're asking about: {question}\n\n"
                    "I'm here to help with programming questions, code review, debugging, and concept explanations.\n\n"
                    "To provide the best assistance, please let me know:\n"
                    "- What programming language you're using\n"
                    "- What specific problem you're trying to solve\n"
                    "- Any error messages you're encountering\n"
                    "- Your current skill level\n\n"
                    + (f"I can see you've provided some code. Let me analyze it for you." if code else ""),
            explanation="This is a general programming assistance response.",
            next_steps=[
                "Provide more specific details about your programming question",
                "Share the code you're working with",
                "Specify the programming language",
                "Describe what you're trying to achieve"
            ]
        )
