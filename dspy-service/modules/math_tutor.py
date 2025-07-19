"""
Specialized Math Tutoring Module using DSPy
Handles mathematical problem solving with step-by-step explanations and verification
"""

import dspy
import re
import ast
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class MathSolution(BaseModel):
    """Structured math solution response"""
    solution_steps: List[str]
    final_answer: str
    verification_code: Optional[str] = None
    is_verified: bool = False
    difficulty_assessment: str = "intermediate"
    practice_problems: Optional[List[str]] = None


class MathTutor(dspy.Module):
    """
    Specialized DSPy module for mathematical problem solving and tutoring
    Uses Program of Thought approach for verifiable solutions
    """
    
    def __init__(self):
        super().__init__()
        
        # Problem classification
        self.classify_problem = dspy.Predict(
            "problem -> problem_type, difficulty_level, required_concepts"
        )
        
        # Step-by-step solution generation (simplified)
        self.solve_step_by_step = dspy.ChainOfThought(
            "problem, problem_type -> solution_steps, final_answer"
        )
        
        # Solution verification
        self.verify_solution = dspy.Predict(
            "problem, solution_steps, verification_code -> is_correct, explanation, corrections"
        )
        
        # Practice problem generation
        self.generate_practice = dspy.ChainOfThought(
            "solved_problem, difficulty_level, concepts -> similar_problems, progressive_difficulty"
        )
        
        # Explanation enhancement for different learning levels
        self.adapt_explanation = dspy.ChainOfThought(
            "solution_steps, student_level -> simplified_explanation, visual_aids_suggestions, mnemonics"
        )
    
    def forward(self, question: str, difficulty_level: str = "intermediate", student_level: str = "intermediate", **kwargs):
        """
        Solve mathematical problems with step-by-step explanations
        
        Args:
            question: Mathematical problem or question
            difficulty_level: Problem difficulty (beginner, intermediate, advanced)
            student_level: Student's mathematical level
        """
        
        try:
            # Classify the mathematical problem
            classification = self.classify_problem(problem=question)
            
            problem_type = getattr(classification, 'problem_type', 'general')
            assessed_difficulty = getattr(classification, 'difficulty_level', difficulty_level)
            required_concepts = getattr(classification, 'required_concepts', 'basic math')
            
            # Generate step-by-step solution
            solution = self.solve_step_by_step(
                problem=question,
                problem_type=problem_type,
                difficulty_level=assessed_difficulty
            )
            
            # Extract solution components
            solution_steps = self._parse_solution_steps(getattr(solution, 'solution_steps', ''))
            verification_code = getattr(solution, 'verification_code', '')
            final_answer = getattr(solution, 'final_answer', 'Unable to determine')
            
            # Verify the solution if code is provided
            is_verified = False
            verification_explanation = ""
            
            if verification_code:
                try:
                    verification = self.verify_solution(
                        problem=question,
                        solution_steps='\n'.join(solution_steps),
                        verification_code=verification_code
                    )
                    is_verified = getattr(verification, 'is_correct', False)
                    verification_explanation = getattr(verification, 'explanation', '')
                except Exception as e:
                    print(f"Verification error: {e}")
                    verification_explanation = "Could not verify solution automatically"
            
            # Adapt explanation to student level
            adapted_explanation = self.adapt_explanation(
                solution_steps='\n'.join(solution_steps),
                student_level=student_level
            )
            
            # Generate practice problems
            practice_problems = []
            try:
                practice = self.generate_practice(
                    solved_problem=question,
                    difficulty_level=assessed_difficulty,
                    concepts=required_concepts
                )
                practice_problems = self._parse_practice_problems(
                    getattr(practice, 'similar_problems', '')
                )
            except Exception as e:
                print(f"Practice generation error: {e}")
            
            # Construct comprehensive response
            response_parts = [
                f"**Problem Analysis:** {problem_type} problem involving {required_concepts}",
                f"**Difficulty Level:** {assessed_difficulty}",
                "",
                "**Step-by-Step Solution:**"
            ]
            
            for i, step in enumerate(solution_steps, 1):
                response_parts.append(f"{i}. {step}")
            
            response_parts.extend([
                "",
                f"**Final Answer:** {final_answer}",
                ""
            ])
            
            if verification_explanation:
                response_parts.extend([
                    f"**Verification:** {'✅ Verified' if is_verified else '⚠️ Needs Review'}",
                    verification_explanation,
                    ""
                ])
            
            # Add adapted explanation
            simplified_explanation = getattr(adapted_explanation, 'simplified_explanation', '')
            if simplified_explanation and student_level in ['beginner', 'elementary']:
                response_parts.extend([
                    "**Simplified Explanation:**",
                    simplified_explanation,
                    ""
                ])
            
            # Add visual aids suggestions
            visual_aids = getattr(adapted_explanation, 'visual_aids_suggestions', '')
            if visual_aids:
                response_parts.extend([
                    "**Visual Learning Tips:**",
                    visual_aids,
                    ""
                ])
            
            return dspy.Prediction(
                response='\n'.join(response_parts),
                explanation=simplified_explanation,
                next_steps=practice_problems[:3] if practice_problems else [
                    "Try solving similar problems",
                    "Review the concepts used in this solution",
                    "Practice the calculation steps"
                ],
                solution_steps=solution_steps,
                final_answer=final_answer,
                is_verified=is_verified,
                difficulty_assessment=assessed_difficulty,
                practice_problems=practice_problems
            )
            
        except Exception as e:
            print(f"Math tutor error: {e}")
            return self._fallback_response(question)
    
    def _parse_solution_steps(self, solution_text: str) -> List[str]:
        """Parse solution steps from generated text"""
        if not solution_text:
            return ["Unable to generate solution steps"]
        
        # Try to extract numbered steps
        steps = []
        lines = solution_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('Step')):
                # Remove step numbering
                clean_step = re.sub(r'^\d+\.?\s*|^Step\s*\d+:?\s*', '', line)
                if clean_step:
                    steps.append(clean_step)
            elif line and not steps:
                # If no numbered steps found, treat each non-empty line as a step
                steps.append(line)
        
        return steps if steps else [solution_text]
    
    def _parse_practice_problems(self, practice_text: str) -> List[str]:
        """Parse practice problems from generated text"""
        if not practice_text:
            return []
        
        problems = []
        lines = practice_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or '?' in line or '=' in line):
                # Clean up problem formatting
                clean_problem = re.sub(r'^\d+\.?\s*', '', line)
                if clean_problem:
                    problems.append(clean_problem)
        
        return problems[:5]  # Limit to 5 practice problems
    
    def _fallback_response(self, question: str):
        """Fallback response when main processing fails"""
        return dspy.Prediction(
            response=f"I understand you're working on this math problem: {question}\n\n"
                    "Let me help you approach this step by step:\n"
                    "1. First, let's identify what type of problem this is\n"
                    "2. Then we'll break it down into manageable steps\n"
                    "3. Finally, we'll solve it together\n\n"
                    "Could you provide any additional context or specify what part you're struggling with?",
            explanation="This is a general approach to mathematical problem solving.",
            next_steps=[
                "Identify the problem type",
                "Break down into steps",
                "Apply relevant mathematical concepts"
            ],
            solution_steps=["Analyze the problem", "Apply mathematical principles", "Verify the solution"],
            final_answer="Pending detailed analysis",
            is_verified=False,
            difficulty_assessment="unknown"
        )


class AdvancedMathTutor(MathTutor):
    """
    Advanced math tutor with calculus, linear algebra, and advanced topics support
    """
    
    def __init__(self):
        super().__init__()
        
        # Advanced problem classification
        self.classify_advanced = dspy.Predict(
            "problem -> math_field, complexity_level, prerequisites, solution_approach"
        )
        
        # Concept explanation for advanced topics
        self.explain_concepts = dspy.ChainOfThought(
            "math_field, concepts, student_background -> conceptual_explanation, intuitive_understanding, applications"
        )
    
    def forward(self, question: str, math_field: str = "general", **kwargs):
        """Enhanced forward method for advanced mathematics"""
        
        # First classify as advanced problem
        advanced_classification = self.classify_advanced(problem=question)
        
        # Get conceptual explanation
        concepts_explanation = self.explain_concepts(
            math_field=getattr(advanced_classification, 'math_field', math_field),
            concepts=getattr(advanced_classification, 'prerequisites', 'basic concepts'),
            student_background=kwargs.get('student_level', 'intermediate')
        )
        
        # Call parent method for solution
        result = super().forward(question, **kwargs)
        
        # Enhance with conceptual understanding
        conceptual_explanation = getattr(concepts_explanation, 'conceptual_explanation', '')
        intuitive_understanding = getattr(concepts_explanation, 'intuitive_understanding', '')
        applications = getattr(concepts_explanation, 'applications', '')
        
        enhanced_response = result.response + f"""

**Conceptual Understanding:**
{conceptual_explanation}

**Intuitive Explanation:**
{intuitive_understanding}

**Real-World Applications:**
{applications}
"""
        
        return dspy.Prediction(
            response=enhanced_response,
            explanation=result.explanation,
            next_steps=result.next_steps,
            solution_steps=result.solution_steps,
            final_answer=result.final_answer,
            is_verified=result.is_verified,
            difficulty_assessment=result.difficulty_assessment,
            conceptual_explanation=conceptual_explanation,
            applications=applications
        )
