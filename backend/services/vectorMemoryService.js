import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

class VectorMemoryService {
  constructor() {
    this.genAI = null;
    this.embeddingModel = null;
    this.isInitialized = false;
    this.vectorStore = new Map(); // Simple in-memory vector store
    this.idCounter = 0;
  }

  async initialize() {
    try {
      // Initialize Google Generative AI for embeddings
      if (!process.env.GOOGLE_API_KEY) {
        console.warn('GOOGLE_API_KEY not found, vector memory disabled');
        this.isInitialized = false;
        return;
      }

      this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
      this.embeddingModel = this.genAI.getGenerativeModel({ model: 'text-embedding-004' });

      // Initialize simple in-memory vector store
      this.vectorStore.clear();
      this.idCounter = 0;

      this.isInitialized = true;
      console.log('Vector Memory Service initialized successfully with Google Gemini embeddings (in-memory store)');
    } catch (error) {
      console.error('Failed to initialize Vector Memory Service:', error);
      console.warn('Vector Memory Service will operate in fallback mode');
      this.isInitialized = false;
    }
  }

  async generateEmbedding(text) {
    if (!this.embeddingModel) {
      throw new Error('Embedding model not initialized');
    }

    try {
      const result = await this.embeddingModel.embedContent(text);
      return result.embedding.values;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw error;
    }
  }

  // Simple cosine similarity calculation
  cosineSimilarity(vecA, vecB) {
    if (vecA.length !== vecB.length) {
      throw new Error('Vectors must have the same length');
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
      normA += vecA[i] * vecA[i];
      normB += vecB[i] * vecB[i];
    }

    normA = Math.sqrt(normA);
    normB = Math.sqrt(normB);

    if (normA === 0 || normB === 0) {
      return 0;
    }

    return dotProduct / (normA * normB);
  }

  async storeConversation(conversationId, userMessage, aiResponse, metadata = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // If vector memory is not available, just log and return
    if (!this.isInitialized) {
      console.log(`Vector memory not available, skipping storage for ${conversationId}`);
      return;
    }

    try {
      const timestamp = new Date().toISOString();

      // Store user message
      const userEmbedding = await this.generateEmbedding(userMessage);
      const userId = `${conversationId}_user_${this.idCounter++}`;
      this.vectorStore.set(userId, {
        id: userId,
        embedding: userEmbedding,
        document: userMessage,
        metadata: {
          type: 'user_message',
          conversationId,
          timestamp,
          ...metadata
        }
      });

      // Store AI response
      const aiEmbedding = await this.generateEmbedding(aiResponse);
      const aiId = `${conversationId}_ai_${this.idCounter++}`;
      this.vectorStore.set(aiId, {
        id: aiId,
        embedding: aiEmbedding,
        document: aiResponse,
        metadata: {
          type: 'ai_response',
          conversationId,
          timestamp,
          ...metadata
        }
      });

      console.log(`Stored conversation for ${conversationId} (${this.vectorStore.size} total documents)`);
    } catch (error) {
      console.error('Error storing conversation:', error);
      // Don't throw error, just log it to prevent breaking the chat
      console.warn('Continuing without vector storage');
    }
  }

  async retrieveRelevantContext(query, limit = 5, conversationId = null) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // If vector memory is not available, return empty array
    if (!this.isInitialized) {
      console.log('Vector memory not available, returning empty context');
      return [];
    }

    try {
      const queryEmbedding = await this.generateEmbedding(query);
      const results = [];

      // Calculate similarity for all stored documents
      for (const [id, doc] of this.vectorStore.entries()) {
        // Filter by conversation ID if specified
        if (conversationId && doc.metadata.conversationId !== conversationId) {
          continue;
        }

        const similarity = this.cosineSimilarity(queryEmbedding, doc.embedding);
        results.push({
          content: doc.document,
          metadata: doc.metadata,
          similarity: similarity,
          distance: 1 - similarity // Convert similarity to distance
        });
      }

      // Sort by similarity (highest first) and limit results
      results.sort((a, b) => b.similarity - a.similarity);
      return results.slice(0, limit);
    } catch (error) {
      console.error('Error retrieving context:', error);
      // Return empty array instead of throwing error
      console.warn('Returning empty context due to error');
      return [];
    }
  }

  async getConversationHistory(conversationId, limit = 10) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // If vector memory is not available, return empty array
    if (!this.isInitialized) {
      console.log('Vector memory not available, returning empty history');
      return [];
    }

    try {
      const results = [];

      // Get all documents for this conversation
      for (const doc of this.vectorStore.values()) {
        if (doc.metadata.conversationId === conversationId) {
          results.push({
            content: doc.document,
            metadata: doc.metadata
          });
        }
      }

      // Sort by timestamp and limit results
      results.sort((a, b) => new Date(a.metadata.timestamp) - new Date(b.metadata.timestamp));
      return results.slice(0, limit * 2); // Get both user and AI messages
    } catch (error) {
      console.error('Error getting conversation history:', error);
      // Return empty array instead of throwing error
      console.warn('Returning empty history due to error');
      return [];
    }
  }

  async storeDocumentChunk(documentId, chunk, chunkIndex, metadata = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const embedding = await this.generateEmbedding(chunk);
      await this.collection.add({
        ids: [`${documentId}_chunk_${chunkIndex}`],
        embeddings: [embedding],
        documents: [chunk],
        metadatas: [{
          type: 'document_chunk',
          documentId,
          chunkIndex,
          timestamp: new Date().toISOString(),
          ...metadata
        }]
      });

      console.log(`Stored document chunk ${chunkIndex} for ${documentId}`);
    } catch (error) {
      console.error('Error storing document chunk:', error);
      throw error;
    }
  }

  async searchDocuments(query, documentId = null, limit = 5) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const queryEmbedding = await this.generateEmbedding(query);
      
      const whereClause = documentId ? 
        { documentId: { $eq: documentId }, type: { $eq: 'document_chunk' } } : 
        { type: { $eq: 'document_chunk' } };

      const results = await this.collection.query({
        queryEmbeddings: [queryEmbedding],
        nResults: limit,
        where: whereClause
      });

      return results.documents[0].map((doc, index) => ({
        content: doc,
        metadata: results.metadatas[0][index],
        distance: results.distances[0][index]
      }));
    } catch (error) {
      console.error('Error searching documents:', error);
      throw error;
    }
  }

  async deleteConversation(conversationId) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      await this.collection.delete({
        where: { conversationId: { $eq: conversationId } }
      });
      console.log(`Deleted conversation ${conversationId}`);
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  async cleanup(olderThanDays = 30) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);
      
      // Note: ChromaDB doesn't support date comparisons directly
      // This is a simplified cleanup - in production, you might want to
      // implement a more sophisticated cleanup strategy
      console.log(`Cleanup initiated for data older than ${olderThanDays} days`);
    } catch (error) {
      console.error('Error during cleanup:', error);
      throw error;
    }
  }

  async storeDocument(documentId, content, metadata = {}) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // If vector memory is not available, just log and return
    if (!this.isInitialized) {
      console.log(`Vector memory not available, skipping document storage for ${documentId}`);
      return;
    }

    try {
      const embedding = await this.generateEmbedding(content);
      this.vectorStore.set(documentId, {
        id: documentId,
        embedding: embedding,
        document: content,
        metadata: {
          type: 'document',
          timestamp: new Date().toISOString(),
          ...metadata
        }
      });

      console.log(`Stored document ${documentId} (${this.vectorStore.size} total documents)`);
    } catch (error) {
      console.error('Error storing document:', error);
      console.warn('Continuing without document storage');
    }
  }

  async getStats() {
    if (!this.isInitialized) {
      await this.initialize();
    }

    try {
      return {
        totalDocuments: this.vectorStore.size,
        storageType: 'in-memory',
        isInitialized: this.isInitialized
      };
    } catch (error) {
      console.error('Error getting stats:', error);
      throw error;
    }
  }
}

export default new VectorMemoryService();
