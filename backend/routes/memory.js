import express from 'express';
import vectorMemoryService from '../services/vectorMemoryService.js';
import Conversation from '../models/Conversation.js';

const router = express.Router();

// Get conversation history
router.get('/conversations', async (req, res) => {
  try {
    const { userId, limit = 20 } = req.query;
    
    let conversations;
    if (userId) {
      conversations = await Conversation.findByUserId(userId, parseInt(limit));
    } else {
      conversations = await Conversation.findRecentConversations(parseInt(limit));
    }
    
    res.json({
      success: true,
      conversations
    });
  } catch (error) {
    console.error('Error fetching conversations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch conversations'
    });
  }
});

// Get specific conversation details
router.get('/conversations/:conversationId', async (req, res) => {
  try {
    const { conversationId } = req.params;
    const { limit = 20 } = req.query;
    
    // Get conversation metadata
    const conversation = await Conversation.findOne({ conversationId });
    
    // Get conversation history from vector memory
    const history = await vectorMemoryService.getConversationHistory(
      conversationId, 
      parseInt(limit)
    );
    
    res.json({
      success: true,
      conversation,
      history
    });
  } catch (error) {
    console.error('Error fetching conversation details:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch conversation details'
    });
  }
});

// Search conversations
router.post('/search', async (req, res) => {
  try {
    const { query, conversationId, limit = 10 } = req.body;
    
    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Query is required'
      });
    }
    
    const results = await vectorMemoryService.retrieveRelevantContext(
      query,
      parseInt(limit),
      conversationId
    );
    
    res.json({
      success: true,
      results
    });
  } catch (error) {
    console.error('Error searching conversations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search conversations'
    });
  }
});

// Delete conversation
router.delete('/conversations/:conversationId', async (req, res) => {
  try {
    const { conversationId } = req.params;
    
    // Delete from vector memory
    await vectorMemoryService.deleteConversation(conversationId);
    
    // Delete from MongoDB
    await Conversation.deleteOne({ conversationId });
    
    res.json({
      success: true,
      message: 'Conversation deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting conversation:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete conversation'
    });
  }
});

// Archive conversation
router.patch('/conversations/:conversationId/archive', async (req, res) => {
  try {
    const { conversationId } = req.params;
    
    const conversation = await Conversation.findOneAndUpdate(
      { conversationId },
      { isArchived: true },
      { new: true }
    );
    
    if (!conversation) {
      return res.status(404).json({
        success: false,
        error: 'Conversation not found'
      });
    }
    
    res.json({
      success: true,
      conversation
    });
  } catch (error) {
    console.error('Error archiving conversation:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to archive conversation'
    });
  }
});

// Update conversation tags
router.patch('/conversations/:conversationId/tags', async (req, res) => {
  try {
    const { conversationId } = req.params;
    const { tags } = req.body;
    
    const conversation = await Conversation.findOneAndUpdate(
      { conversationId },
      { tags },
      { new: true }
    );
    
    if (!conversation) {
      return res.status(404).json({
        success: false,
        error: 'Conversation not found'
      });
    }
    
    res.json({
      success: true,
      conversation
    });
  } catch (error) {
    console.error('Error updating conversation tags:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update conversation tags'
    });
  }
});

// Get memory statistics
router.get('/stats', async (req, res) => {
  try {
    const vectorStats = await vectorMemoryService.getStats();
    const conversationCount = await Conversation.countDocuments({ isArchived: false });
    const archivedCount = await Conversation.countDocuments({ isArchived: true });
    
    res.json({
      success: true,
      stats: {
        ...vectorStats,
        activeConversations: conversationCount,
        archivedConversations: archivedCount,
        totalConversations: conversationCount + archivedCount
      }
    });
  } catch (error) {
    console.error('Error fetching memory stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch memory statistics'
    });
  }
});

// Cleanup old conversations
router.post('/cleanup', async (req, res) => {
  try {
    const { daysOld = 90 } = req.body;
    
    // Archive old conversations in MongoDB
    const archiveResult = await Conversation.archiveOldConversations(daysOld);
    
    // Cleanup vector memory (basic implementation)
    await vectorMemoryService.cleanup(daysOld);
    
    res.json({
      success: true,
      message: `Cleanup completed. Archived ${archiveResult.modifiedCount} conversations.`
    });
  } catch (error) {
    console.error('Error during cleanup:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to cleanup old conversations'
    });
  }
});

export default router;
