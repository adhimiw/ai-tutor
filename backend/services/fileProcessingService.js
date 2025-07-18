import fs from 'fs/promises';
import path from 'path';
import sharp from 'sharp';
import vectorMemoryService from './vectorMemoryService.js';
import { v4 as uuidv4 } from 'uuid';
import { createRequire } from 'module';

// Use require for CommonJS modules
const require = createRequire(import.meta.url);
let pdfParse;
try {
  pdfParse = require('pdf-parse');
} catch (error) {
  console.warn('pdf-parse not available, PDF processing will be limited:', error.message);
}

class FileProcessingService {
  constructor() {
    this.uploadDir = process.env.UPLOAD_DIR || './uploads';
    this.maxFileSize = 50 * 1024 * 1024; // 50MB
    this.supportedImageTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
    this.supportedDocumentTypes = ['application/pdf', 'text/plain', 'text/markdown'];
    this.chunkSize = 1000; // Characters per chunk for vector storage
  }

  async ensureUploadDir() {
    try {
      await fs.access(this.uploadDir);
    } catch {
      await fs.mkdir(this.uploadDir, { recursive: true });
    }
  }

  validateFile(file) {
    const errors = [];
    
    if (!file) {
      errors.push('No file provided');
      return errors;
    }
    
    if (file.size > this.maxFileSize) {
      errors.push(`File size exceeds maximum limit of ${this.maxFileSize / (1024 * 1024)}MB`);
    }
    
    const allSupportedTypes = [...this.supportedImageTypes, ...this.supportedDocumentTypes];
    if (!allSupportedTypes.includes(file.mimetype)) {
      errors.push(`Unsupported file type: ${file.mimetype}`);
    }
    
    return errors;
  }

  async processImage(file) {
    try {
      await this.ensureUploadDir();
      
      const fileId = uuidv4();
      const fileName = `${fileId}_${file.originalname}`;
      const filePath = path.join(this.uploadDir, fileName);
      
      // Save original file
      await fs.writeFile(filePath, file.buffer);
      
      // Process image with sharp
      const metadata = await sharp(file.buffer).metadata();
      
      // Create thumbnail
      const thumbnailBuffer = await sharp(file.buffer)
        .resize(300, 300, { fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: 80 })
        .toBuffer();
      
      const thumbnailPath = path.join(this.uploadDir, `thumb_${fileName}.jpg`);
      await fs.writeFile(thumbnailPath, thumbnailBuffer);
      
      const imageData = {
        id: fileId,
        originalName: file.originalname,
        fileName: fileName,
        filePath: filePath,
        thumbnailPath: thumbnailPath,
        mimeType: file.mimetype,
        size: file.size,
        type: 'image',
        metadata: {
          width: metadata.width,
          height: metadata.height,
          format: metadata.format,
          channels: metadata.channels,
          hasAlpha: metadata.hasAlpha
        },
        uploadedAt: new Date().toISOString()
      };
      
      return imageData;
    } catch (error) {
      console.error('Error processing image:', error);
      throw new Error('Failed to process image');
    }
  }

  async processPDF(file) {
    try {
      await this.ensureUploadDir();
      
      const fileId = uuidv4();
      const fileName = `${fileId}_${file.originalname}`;
      const filePath = path.join(this.uploadDir, fileName);
      
      // Save original file
      await fs.writeFile(filePath, file.buffer);
      
      // Extract text from PDF
      if (!pdfParse) {
        throw new Error('PDF processing not available');
      }
      const pdfData = await pdfParse(file.buffer);
      
      // Split text into chunks for vector storage
      const chunks = this.splitTextIntoChunks(pdfData.text);
      
      // Store chunks in vector memory
      for (let i = 0; i < chunks.length; i++) {
        await vectorMemoryService.storeDocumentChunk(
          fileId,
          chunks[i],
          i,
          {
            fileName: file.originalname,
            pageNumber: Math.floor(i / 3) + 1, // Approximate page mapping
            totalPages: pdfData.numpages,
            chunkIndex: i,
            totalChunks: chunks.length
          }
        );
      }
      
      const documentData = {
        id: fileId,
        originalName: file.originalname,
        fileName: fileName,
        filePath: filePath,
        mimeType: file.mimetype,
        size: file.size,
        type: 'document',
        metadata: {
          pages: pdfData.numpages,
          textLength: pdfData.text.length,
          chunks: chunks.length,
          hasVectorStorage: true
        },
        content: {
          fullText: pdfData.text,
          info: pdfData.info,
          metadata: pdfData.metadata
        },
        uploadedAt: new Date().toISOString()
      };
      
      return documentData;
    } catch (error) {
      console.error('Error processing PDF:', error);
      throw new Error('Failed to process PDF');
    }
  }

  splitTextIntoChunks(text, chunkSize = this.chunkSize) {
    const chunks = [];
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    
    let currentChunk = '';
    
    for (const sentence of sentences) {
      const trimmedSentence = sentence.trim();
      
      if (currentChunk.length + trimmedSentence.length + 1 <= chunkSize) {
        currentChunk += (currentChunk ? '. ' : '') + trimmedSentence;
      } else {
        if (currentChunk) {
          chunks.push(currentChunk + '.');
        }
        currentChunk = trimmedSentence;
      }
    }
    
    if (currentChunk) {
      chunks.push(currentChunk + '.');
    }
    
    return chunks;
  }

  async processTextFile(file) {
    try {
      await this.ensureUploadDir();

      const fileId = uuidv4();
      const fileName = `${fileId}_${file.originalname}`;
      const filePath = path.join(this.uploadDir, fileName);

      // Save the file
      await fs.writeFile(filePath, file.buffer);

      // Extract text content
      const textContent = file.buffer.toString('utf-8');

      // Create chunks for vector storage
      const chunks = this.createTextChunks(textContent);

      // Store chunks in vector memory
      for (let i = 0; i < chunks.length; i++) {
        const chunkId = `${fileId}_chunk_${i}`;
        await vectorMemoryService.storeDocument(chunkId, chunks[i], {
          fileId,
          fileName: file.originalname,
          chunkIndex: i,
          totalChunks: chunks.length,
          fileType: 'text',
          uploadDate: new Date().toISOString()
        });
      }

      return {
        fileId,
        fileName: file.originalname,
        filePath,
        fileSize: file.size,
        fileType: 'text',
        chunksStored: chunks.length,
        textContent: textContent.substring(0, 500) + (textContent.length > 500 ? '...' : ''), // Preview
        uploadDate: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error processing text file:', error);
      throw new Error('Failed to process text file');
    }
  }

  async processFile(file) {
    const validationErrors = this.validateFile(file);
    if (validationErrors.length > 0) {
      throw new Error(`File validation failed: ${validationErrors.join(', ')}`);
    }

    if (this.supportedImageTypes.includes(file.mimetype)) {
      return await this.processImage(file);
    } else if (file.mimetype === 'application/pdf') {
      return await this.processPDF(file);
    } else if (file.mimetype === 'text/plain' || file.mimetype === 'text/markdown') {
      return await this.processTextFile(file);
    } else {
      throw new Error(`Unsupported file type: ${file.mimetype}`);
    }
  }

  async getFileBuffer(fileId, fileName) {
    try {
      const filePath = path.join(this.uploadDir, fileName);
      const buffer = await fs.readFile(filePath);
      return buffer;
    } catch (error) {
      console.error('Error reading file:', error);
      throw new Error('File not found');
    }
  }

  async deleteFile(fileId, fileName) {
    try {
      const filePath = path.join(this.uploadDir, fileName);
      await fs.unlink(filePath);
      
      // Try to delete thumbnail if it exists
      try {
        const thumbnailPath = path.join(this.uploadDir, `thumb_${fileName}.jpg`);
        await fs.unlink(thumbnailPath);
      } catch {
        // Thumbnail might not exist, ignore error
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting file:', error);
      throw new Error('Failed to delete file');
    }
  }

  async searchDocumentContent(query, documentId, limit = 5) {
    try {
      return await vectorMemoryService.searchDocuments(query, documentId, limit);
    } catch (error) {
      console.error('Error searching document content:', error);
      throw new Error('Failed to search document content');
    }
  }

  async cleanupOldFiles(daysOld = 7) {
    try {
      const files = await fs.readdir(this.uploadDir);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - daysOld);
      
      let deletedCount = 0;
      
      for (const file of files) {
        const filePath = path.join(this.uploadDir, file);
        const stats = await fs.stat(filePath);
        
        if (stats.mtime < cutoffDate) {
          await fs.unlink(filePath);
          deletedCount++;
        }
      }
      
      return { deletedCount, message: `Cleaned up ${deletedCount} old files` };
    } catch (error) {
      console.error('Error during file cleanup:', error);
      throw new Error('Failed to cleanup old files');
    }
  }

  getFileStats() {
    return {
      uploadDir: this.uploadDir,
      maxFileSize: this.maxFileSize,
      supportedImageTypes: this.supportedImageTypes,
      supportedDocumentTypes: this.supportedDocumentTypes,
      chunkSize: this.chunkSize
    };
  }
}

export default new FileProcessingService();
