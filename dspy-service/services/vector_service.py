"""
Enhanced Vector Service using DSPy with Google Gemini
Replaces the Node.js vectorMemoryService with DSPy-optimized retrieval using only Google APIs
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import dspy
import google.generativeai as genai
from loguru import logger


class GeminiVectorService:
    """
    Enhanced vector service using DSPy retrievers with Google Gemini embeddings
    Provides better integration with DSPy modules using only Google APIs
    """

    def __init__(self):
        self.genai_client = None
        self.embedder = None
        self.retriever = None
        self.vector_store = {}  # In-memory store for now
        self.conversation_store = {}
        self.document_store = {}
        self.is_initialized = False

        # DSPy retrieval components
        self.query_optimizer = None
        self.context_ranker = None

    async def initialize(self):
        """Initialize the vector service with DSPy components and Google Gemini"""
        try:
            # Configure Google Generative AI
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")

            genai.configure(api_key=api_key)
            self.genai_client = genai

            # Skip DSPy embedder initialization for now - use simple fallback
            logger.info("Using simple hash-based embeddings for vector service")
            self.embedder = None
            self.retriever = None
            
            # Initialize query optimization
            self.query_optimizer = dspy.ChainOfThought(
                "original_query, context -> optimized_query, search_strategy"
            )
            
            # Initialize context ranking
            self.context_ranker = dspy.Predict(
                "query, retrieved_contexts -> ranked_contexts, relevance_scores"
            )
            
            self.is_initialized = True
            logger.info("Vector service initialized successfully with DSPy components")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            self.is_initialized = False
            raise
    
    async def store_conversation(self, conversation_id: str, user_message: str, 
                               ai_response: str, metadata: Dict[str, Any] = None):
        """Store conversation with enhanced metadata and embeddings"""
        
        if not self.is_initialized:
            logger.warning("Vector service not initialized, skipping conversation storage")
            return
        
        try:
            # Create conversation entry
            conversation_entry = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Generate embeddings for both user message and AI response
            user_embedding = await self._generate_embedding(user_message)
            response_embedding = await self._generate_embedding(ai_response)
            
            # Store in conversation store
            if conversation_id not in self.conversation_store:
                self.conversation_store[conversation_id] = []
            
            self.conversation_store[conversation_id].append({
                **conversation_entry,
                "user_embedding": user_embedding,
                "response_embedding": response_embedding
            })
            
            # Update retriever corpus with new content
            await self._update_retriever_corpus()
            
            logger.debug(f"Stored conversation for {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    async def get_conversation_context(self, conversation_id: str, user_id: str = None, 
                                     limit: int = 5) -> List[Dict[str, Any]]:
        """Get conversation context with relevance ranking"""
        
        if not conversation_id or conversation_id not in self.conversation_store:
            return []
        
        try:
            conversations = self.conversation_store[conversation_id]
            
            # Return recent conversations with metadata
            recent_conversations = conversations[-limit:] if conversations else []
            
            return [
                {
                    "user_message": conv["user_message"],
                    "ai_response": conv["ai_response"],
                    "timestamp": conv["timestamp"],
                    "metadata": conv.get("metadata", {})
                }
                for conv in recent_conversations
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving conversation context: {e}")
            return []
    
    async def retrieve_relevant_context(self, query: str, k: int = 5, 
                                      conversation_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve relevant context using DSPy optimization"""
        
        if not self.is_initialized:
            logger.warning("Vector service not initialized, returning empty context")
            return []
        
        try:
            # Optimize query for better retrieval
            optimized_query_result = self.query_optimizer(
                original_query=query,
                context=f"Conversation ID: {conversation_id}" if conversation_id else "General query"
            )
            
            optimized_query = getattr(optimized_query_result, 'optimized_query', query)
            
            # Perform retrieval
            if hasattr(self.retriever, 'forward'):
                retrieval_results = self.retriever.forward(optimized_query, k=k)
            else:
                retrieval_results = self.retriever(optimized_query, k=k)
            
            # Extract passages and rank them
            if hasattr(retrieval_results, 'passages'):
                passages = retrieval_results.passages
                
                # Rank contexts using DSPy
                ranking_result = self.context_ranker(
                    query=optimized_query,
                    retrieved_contexts='\n'.join([f"{i}: {p}" for i, p in enumerate(passages)])
                )
                
                # Return structured context
                return [
                    {
                        "content": passage,
                        "relevance_score": 0.8,  # Default score, could be enhanced
                        "source": "conversation_history",
                        "metadata": {}
                    }
                    for passage in passages[:k]
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            return []
    
    async def store_document(self, document_id: str, content: str, 
                           metadata: Dict[str, Any] = None):
        """Store document with embeddings for retrieval"""
        
        if not self.is_initialized:
            logger.warning("Vector service not initialized, skipping document storage")
            return
        
        try:
            # Generate embedding for document content
            embedding = await self._generate_embedding(content)
            
            # Store document
            self.document_store[document_id] = {
                "document_id": document_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Update retriever corpus
            await self._update_retriever_corpus()
            
            logger.debug(f"Stored document {document_id}")
            
        except Exception as e:
            logger.error(f"Error storing document: {e}")
    
    async def search_documents(self, query: str, document_id: str = None, 
                             k: int = 5) -> List[Dict[str, Any]]:
        """Search documents with semantic similarity"""
        
        if not self.is_initialized:
            return []
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in specific document or all documents
            search_docs = [self.document_store[document_id]] if document_id and document_id in self.document_store else list(self.document_store.values())
            
            # Calculate similarities
            results = []
            for doc in search_docs:
                if "embedding" in doc:
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [doc["embedding"]]
                    )[0][0]
                    
                    results.append({
                        "document_id": doc["document_id"],
                        "content": doc["content"],
                        "similarity": float(similarity),
                        "metadata": doc.get("metadata", {})
                    })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector service statistics"""
        
        total_conversations = sum(len(convs) for convs in self.conversation_store.values())
        total_documents = len(self.document_store)
        
        return {
            "is_initialized": self.is_initialized,
            "total_conversations": total_conversations,
            "total_conversation_threads": len(self.conversation_store),
            "total_documents": total_documents,
            "embedding_model": os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
            "vector_dimensions": int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
        }
    
    async def cleanup(self, days_old: int = 90):
        """Cleanup old conversations and documents"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Cleanup old conversations
            for conv_id in list(self.conversation_store.keys()):
                conversations = self.conversation_store[conv_id]
                # Keep conversations newer than cutoff
                self.conversation_store[conv_id] = [
                    conv for conv in conversations
                    if datetime.fromisoformat(conv["timestamp"]) > cutoff_date
                ]
                
                # Remove empty conversation threads
                if not self.conversation_store[conv_id]:
                    del self.conversation_store[conv_id]
            
            # Cleanup old documents
            for doc_id in list(self.document_store.keys()):
                doc = self.document_store[doc_id]
                if datetime.fromisoformat(doc["timestamp"]) <= cutoff_date:
                    del self.document_store[doc_id]
            
            # Update retriever corpus after cleanup
            await self._update_retriever_corpus()
            
            logger.info(f"Cleanup completed, removed data older than {days_old} days")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google's gemini-embedding-001 model"""

        try:
            # Use Google's latest embedding model directly
            result = self.genai_client.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document"
            )

            return result['embedding']

        except Exception as e:
            logger.error(f"Error generating Google embedding: {e}")
            # Return simple hash-based embedding as fallback
            return [float(hash(text[i:i+10]) % 1000) / 1000 for i in range(0, min(len(text), 768), 10)]
    
    async def _update_retriever_corpus(self):
        """Update the retriever corpus with current data"""
        
        try:
            # Collect all text content for corpus
            corpus = []
            
            # Add conversation content
            for conversations in self.conversation_store.values():
                for conv in conversations:
                    corpus.append(conv["user_message"])
                    corpus.append(conv["ai_response"])
            
            # Add document content
            for doc in self.document_store.values():
                corpus.append(doc["content"])
            
            # Update retriever if it supports corpus updates
            if hasattr(self.retriever, 'update_corpus'):
                self.retriever.update_corpus(corpus)
            elif hasattr(self.retriever, 'corpus'):
                self.retriever.corpus = corpus
            
            logger.debug(f"Updated retriever corpus with {len(corpus)} items")
            
        except Exception as e:
            logger.error(f"Error updating retriever corpus: {e}")


# Alias for backward compatibility
VectorService = GeminiVectorService
