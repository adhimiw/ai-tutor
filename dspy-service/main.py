"""
DSPy AI Tutor Service
Enhanced tutoring service using DSPy framework for systematic AI optimization
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import dspy
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
from loguru import logger

from modules.tutor_rag import TutorRAG
from modules.math_tutor import MathTutor
from modules.code_tutor import CodeTutor
from modules.adaptive_tutor import AdaptiveTutor
from services.vector_service import VectorService
from services.optimization_service import OptimizationService
from utils.metrics import EducationalMetrics

# Load environment variables
load_dotenv()

# Global services
vector_service: Optional[VectorService] = None
optimization_service: Optional[OptimizationService] = None
educational_metrics: Optional[EducationalMetrics] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    global vector_service, optimization_service, educational_metrics
    
    try:
        # Initialize DSPy configuration with Google Gemini
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        # Configure Google Generative AI directly
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        lm = dspy.LM(
            model=os.getenv("DEFAULT_LM_MODEL", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        dspy.configure(lm=lm)

        logger.info(f"Initialized DSPy with model: {os.getenv('DEFAULT_LM_MODEL', 'gemini/gemini-2.5-flash')}")
        
        # Initialize services
        vector_service = VectorService()
        await vector_service.initialize()
        
        optimization_service = OptimizationService()
        educational_metrics = EducationalMetrics()
        
        logger.info("DSPy AI Tutor Service initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        if vector_service:
            await vector_service.cleanup()
        logger.info("DSPy AI Tutor Service shutdown complete")

# FastAPI app
app = FastAPI(
    title="DSPy AI Tutor Service",
    description="Enhanced AI tutoring service using DSPy framework",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="Student's question or message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field("anonymous", description="User ID for personalization")
    subject: Optional[str] = Field("general", description="Subject area (math, programming, general)")
    difficulty_level: Optional[str] = Field("intermediate", description="Difficulty level")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI tutor's response")
    explanation: Optional[str] = Field(None, description="Detailed explanation")
    next_steps: Optional[List[str]] = Field(None, description="Suggested next learning steps")
    confidence: Optional[float] = Field(None, description="Response confidence score")
    sources: Optional[List[str]] = Field(None, description="Information sources used")
    conversation_id: str = Field(..., description="Conversation ID")

class OptimizationRequest(BaseModel):
    module_name: str = Field(..., description="Module to optimize")
    training_examples: List[Dict[str, Any]] = Field(..., description="Training examples")
    metric_name: str = Field("educational_effectiveness", description="Optimization metric")

# Initialize tutor modules
tutor_modules = {
    "general": TutorRAG(),
    "math": MathTutor(),
    "programming": CodeTutor(),
    "adaptive": AdaptiveTutor()
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DSPy AI Tutor",
        "version": "1.0.0",
        "dspy_version": dspy.__version__
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for AI tutoring"""
    try:
        # Select appropriate tutor module
        module_key = request.subject if request.subject in tutor_modules else "general"
        tutor_module = tutor_modules[module_key]
        
        # Get conversation context
        context = await vector_service.get_conversation_context(
            request.conversation_id,
            request.user_id
        ) if request.conversation_id else []

        # Check if memory context is provided from backend
        memory_context = request.context.get('memory_context', []) if request.context else []
        is_memory_query = request.context.get('is_memory_query', False) if request.context else False

        # If it's a memory query and we have memory context, use it
        if is_memory_query and memory_context:
            logger.info(f"Using memory context for query: {len(memory_context)} items")
            # Combine memory context with regular context
            combined_context = memory_context + context

            # Create a memory-aware response
            memory_info = "\n".join([f"Previous context: {item.get('content', '')}" for item in memory_context[:5]])
            memory_response = f"Yes, I can recall our previous conversations about this topic. Here's what I remember:\n\n{memory_info}\n\nBased on our previous discussions, "

            # Generate response using DSPy module with memory context
            if hasattr(tutor_module, 'forward'):
                result = tutor_module.forward(
                    question=request.message,
                    context=combined_context,
                    difficulty_level=request.difficulty_level,
                    memory_context=memory_info,
                    **request.context
                )
            else:
                result = tutor_module(
                    question=request.message,
                    context=combined_context,
                    difficulty_level=request.difficulty_level
                )

            # Prepend memory information to the response
            if hasattr(result, 'response'):
                result.response = memory_response + result.response
            else:
                result = memory_response + str(result)
        else:
            # Generate response using DSPy module normally
            if hasattr(tutor_module, 'forward'):
                result = tutor_module.forward(
                    question=request.message,
                    context=context,
                    difficulty_level=request.difficulty_level,
                    **request.context
                )
            else:
                result = tutor_module(
                    question=request.message,
                    context=context,
                    difficulty_level=request.difficulty_level
                )
        
        # Store conversation for future context
        conversation_id = request.conversation_id or f"conv_{hash(request.message)}_{request.user_id}"
        await vector_service.store_conversation(
            conversation_id=conversation_id,
            user_message=request.message,
            ai_response=result.response if hasattr(result, 'response') else str(result),
            metadata={
                "user_id": request.user_id,
                "subject": request.subject,
                "difficulty_level": request.difficulty_level
            }
        )
        
        return ChatResponse(
            response=result.response if hasattr(result, 'response') else str(result),
            explanation=getattr(result, 'explanation', None),
            next_steps=getattr(result, 'next_steps', None),
            confidence=getattr(result, 'confidence', None),
            sources=getattr(result, 'sources', None),
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")

@app.post("/optimize")
async def optimize_module(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """Optimize a specific tutor module"""
    try:
        if request.module_name not in tutor_modules:
            raise HTTPException(status_code=404, detail=f"Module '{request.module_name}' not found")
        
        # Run optimization in background
        background_tasks.add_task(
            optimization_service.optimize_module,
            request.module_name,
            tutor_modules[request.module_name],
            request.training_examples,
            request.metric_name
        )
        
        return {"message": f"Optimization started for module '{request.module_name}'"}
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start optimization: {str(e)}")

@app.get("/modules")
async def list_modules():
    """List available tutor modules"""
    return {
        "modules": list(tutor_modules.keys()),
        "descriptions": {
            "general": "General purpose tutoring with RAG",
            "math": "Specialized math problem solving",
            "programming": "Code review and programming help",
            "adaptive": "Adaptive tutoring based on student performance"
        }
    }

@app.get("/metrics/{conversation_id}")
async def get_conversation_metrics(conversation_id: str):
    """Get educational effectiveness metrics for a conversation"""
    try:
        metrics = await educational_metrics.calculate_conversation_metrics(conversation_id)
        return metrics
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("SERVICE_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVICE_PORT", 8001)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
