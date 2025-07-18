import express from 'express';
import multer from 'multer';
import fileProcessingService from '../services/fileProcessingService.js';
import geminiService from '../services/geminiService.js';
import File from '../models/File.js';

const router = express.Router();

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB
    files: 5 // Maximum 5 files per request
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif',
      'application/pdf'
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${file.mimetype}`), false);
    }
  }
});

// Upload single file
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file provided'
      });
    }

    const { userId, conversationId, tags } = req.body;

    // Process the file
    const processedFile = await fileProcessingService.processFile(req.file);

    // Save file metadata to database
    const fileDoc = new File({
      fileId: processedFile.id,
      originalName: processedFile.originalName,
      fileName: processedFile.fileName,
      filePath: processedFile.filePath,
      thumbnailPath: processedFile.thumbnailPath,
      mimeType: processedFile.mimeType,
      size: processedFile.size,
      type: processedFile.type,
      userId: userId || null,
      conversationId: conversationId || null,
      metadata: processedFile.metadata,
      content: processedFile.content || {},
      processingStatus: 'completed',
      tags: tags ? tags.split(',').map(tag => tag.trim()) : []
    });

    await fileDoc.save();

    res.json({
      success: true,
      file: {
        id: processedFile.id,
        originalName: processedFile.originalName,
        type: processedFile.type,
        size: processedFile.size,
        mimeType: processedFile.mimeType,
        metadata: processedFile.metadata,
        uploadedAt: processedFile.uploadedAt
      }
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to upload file'
    });
  }
});

// Upload multiple files
router.post('/upload-multiple', upload.array('files', 5), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'No files provided'
      });
    }

    const { userId, conversationId, tags } = req.body;
    const uploadedFiles = [];
    const errors = [];

    for (const file of req.files) {
      try {
        const processedFile = await fileProcessingService.processFile(file);

        const fileDoc = new File({
          fileId: processedFile.id,
          originalName: processedFile.originalName,
          fileName: processedFile.fileName,
          filePath: processedFile.filePath,
          thumbnailPath: processedFile.thumbnailPath,
          mimeType: processedFile.mimeType,
          size: processedFile.size,
          type: processedFile.type,
          userId: userId || null,
          conversationId: conversationId || null,
          metadata: processedFile.metadata,
          content: processedFile.content || {},
          processingStatus: 'completed',
          tags: tags ? tags.split(',').map(tag => tag.trim()) : []
        });

        await fileDoc.save();

        uploadedFiles.push({
          id: processedFile.id,
          originalName: processedFile.originalName,
          type: processedFile.type,
          size: processedFile.size,
          mimeType: processedFile.mimeType,
          metadata: processedFile.metadata,
          uploadedAt: processedFile.uploadedAt
        });
      } catch (error) {
        errors.push({
          fileName: file.originalname,
          error: error.message
        });
      }
    }

    res.json({
      success: true,
      uploadedFiles,
      errors: errors.length > 0 ? errors : undefined
    });
  } catch (error) {
    console.error('Error uploading multiple files:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to upload files'
    });
  }
});

// Get file metadata
router.get('/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    
    const file = await File.findOne({ fileId });
    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    await file.updateLastAccessed();

    res.json({
      success: true,
      file
    });
  } catch (error) {
    console.error('Error getting file metadata:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get file metadata'
    });
  }
});

// Download file
router.get('/:fileId/download', async (req, res) => {
  try {
    const { fileId } = req.params;
    
    const file = await File.findOne({ fileId });
    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    const buffer = await fileProcessingService.getFileBuffer(fileId, file.fileName);
    await file.updateLastAccessed();

    res.set({
      'Content-Type': file.mimeType,
      'Content-Disposition': `attachment; filename="${file.originalName}"`,
      'Content-Length': buffer.length
    });

    res.send(buffer);
  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to download file'
    });
  }
});

// Analyze file with AI
router.post('/:fileId/analyze', async (req, res) => {
  try {
    const { fileId } = req.params;
    const { prompt, userId, conversationId } = req.body;
    
    const file = await File.findOne({ fileId });
    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    const buffer = await fileProcessingService.getFileBuffer(fileId, file.fileName);
    let analysis;

    if (file.type === 'image') {
      analysis = await geminiService.analyzeImage(
        buffer, 
        file.mimeType, 
        prompt || 'Analyze this image and provide educational insights.'
      );
    } else if (file.type === 'document') {
      analysis = await geminiService.processDocument(
        buffer, 
        file.mimeType, 
        prompt || 'Analyze this document and provide a comprehensive summary.'
      );
    } else {
      return res.status(400).json({
        success: false,
        error: 'Unsupported file type for analysis'
      });
    }

    await file.updateLastAccessed();

    res.json({
      success: true,
      analysis,
      fileInfo: {
        id: file.fileId,
        name: file.originalName,
        type: file.type
      }
    });
  } catch (error) {
    console.error('Error analyzing file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to analyze file'
    });
  }
});

// Search document content
router.post('/:fileId/search', async (req, res) => {
  try {
    const { fileId } = req.params;
    const { query, limit = 5 } = req.body;
    
    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Search query is required'
      });
    }

    const file = await File.findOne({ fileId, type: 'document' });
    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'Document not found'
      });
    }

    const results = await fileProcessingService.searchDocumentContent(
      query, 
      fileId, 
      parseInt(limit)
    );

    await file.updateLastAccessed();

    res.json({
      success: true,
      results,
      fileInfo: {
        id: file.fileId,
        name: file.originalName,
        pages: file.metadata.get('pages')
      }
    });
  } catch (error) {
    console.error('Error searching document:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search document'
    });
  }
});

// List files
router.get('/', async (req, res) => {
  try {
    const { userId, conversationId, type, limit = 20, page = 1 } = req.query;
    
    const query = {};
    if (userId) query.userId = userId;
    if (conversationId) query.conversationId = conversationId;
    if (type) query.type = type;
    
    const skip = (parseInt(page) - 1) * parseInt(limit);
    
    const files = await File.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit));
    
    const total = await File.countDocuments(query);

    res.json({
      success: true,
      files,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    console.error('Error listing files:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to list files'
    });
  }
});

// Delete file
router.delete('/:fileId', async (req, res) => {
  try {
    const { fileId } = req.params;
    
    const file = await File.findOne({ fileId });
    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    await file.deleteOne();

    res.json({
      success: true,
      message: 'File deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete file'
    });
  }
});

export default router;
