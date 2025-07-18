import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createServer } from 'http';

import connectDB from './config/db.js';
import memoryRoutes from './routes/memory.js';
import fileRoutes from './routes/files.js';
import geminiService from './services/geminiService.js';
import fileProcessingService from './services/fileProcessingService.js';
import multer from 'multer';

// Configure multer for chat file uploads
const chatUpload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 20 * 1024 * 1024, // 20MB for inline processing
    files: 3 // Maximum 3 files per chat message
  }
});

// Load environment variables
dotenv.config();

const app = express();
const server = createServer(app);

const PORT = process.env.PORT || 5000;

// Connect to MongoDB
let dbConnected = false;

const attemptDbConnection = async () => {
  try {
    await connectDB();
    console.log('MongoDB connected successfully');
    dbConnected = true;
  } catch (err) {
    console.error('MongoDB connection error:', err);
    console.log('Server will continue running, but database operations will fail');
  }
};

// Attempt initial connection
attemptDbConnection();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    database: dbConnected ? 'Connected' : 'Disconnected',
    environment: process.env.NODE_ENV || 'development'
  });
});

// API Routes
app.use('/api/memory', memoryRoutes);
app.use('/api/files', fileRoutes);

app.get('/api', (req, res) => {
  res.json({
    message: 'AI Tutor API is running!',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      chat: '/api/chat',
      tutorial: '/api/tutorial',
      quiz: '/api/quiz',
      memory: '/api/memory',
      files: '/api/files'
    }
  });
});

// Enhanced chat endpoint with vector memory and file support
app.post('/api/chat', chatUpload.array('files', 3), async (req, res) => {
  try {
    const { message, conversationId, userId } = req.body;

    if (!message) {
      return res.status(400).json({
        success: false,
        error: 'Message is required'
      });
    }

    console.log('Received message:', message);
    console.log('Files attached:', req.files ? req.files.length : 0);

    let result;

    // Check if files are attached
    if (req.files && req.files.length > 0) {
      // Process files for multimodal input
      const processedFiles = [];

      for (const file of req.files) {
        try {
          const fileData = {
            name: file.originalname,
            buffer: file.buffer,
            mimeType: file.mimetype,
            size: file.size
          };

          // Determine file type and extract content
          if (file.mimetype.startsWith('image/')) {
            fileData.type = 'image';
          } else if (file.mimetype === 'application/pdf') {
            fileData.type = 'document';
            // PDF content extraction would be handled by file processing service
          } else if (file.mimetype === 'text/plain' || file.mimetype === 'text/markdown') {
            fileData.type = 'text';
            fileData.content = file.buffer.toString('utf-8');
          } else {
            console.warn(`Unsupported file type: ${file.mimetype}`);
            continue;
          }

          processedFiles.push(fileData);
        } catch (error) {
          console.error(`Error processing file ${file.originalname}:`, error);
        }
      }

      // Generate response with files
      result = await geminiService.generateResponseWithFiles(message, processedFiles, {
        conversationId,
        userId
      });
    } else {
      // Generate response without files
      result = await geminiService.generateResponse(message, {
        conversationId,
        userId
      });
    }

    res.json({
      success: true,
      response: result.response,
      conversationId: result.conversationId,
      timestamp: new Date().toISOString(),
      filesProcessed: req.files ? req.files.length : 0
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to process message'
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : {}
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    message: 'Route not found',
    path: req.originalUrl
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 AI Tutor Server running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
  console.log(`💾 Database: ${dbConnected ? 'Connected' : 'Disconnected'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

export default app;
