import mongoose from 'mongoose';

const fileSchema = new mongoose.Schema({
  fileId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  originalName: {
    type: String,
    required: true,
    maxlength: 255
  },
  fileName: {
    type: String,
    required: true,
    maxlength: 255
  },
  filePath: {
    type: String,
    required: true
  },
  thumbnailPath: {
    type: String,
    required: false
  },
  mimeType: {
    type: String,
    required: true,
    maxlength: 100
  },
  size: {
    type: Number,
    required: true,
    min: 0
  },
  type: {
    type: String,
    required: true,
    enum: ['image', 'document'],
    index: true
  },
  userId: {
    type: String,
    required: false, // Optional for anonymous users
    index: true
  },
  conversationId: {
    type: String,
    required: false,
    index: true
  },
  metadata: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    default: {}
  },
  content: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    default: {}
  },
  processingStatus: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending',
    index: true
  },
  processingError: {
    type: String,
    maxlength: 1000
  },
  tags: [{
    type: String,
    maxlength: 50
  }],
  isPublic: {
    type: Boolean,
    default: false
  },
  downloadCount: {
    type: Number,
    default: 0,
    min: 0
  },
  lastAccessed: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for better query performance
fileSchema.index({ userId: 1, type: 1, createdAt: -1 });
fileSchema.index({ conversationId: 1, createdAt: -1 });
fileSchema.index({ processingStatus: 1, createdAt: -1 });
fileSchema.index({ mimeType: 1, type: 1 });
fileSchema.index({ tags: 1 });

// Virtual for file age
fileSchema.virtual('ageInDays').get(function() {
  return Math.floor((Date.now() - this.createdAt) / (1000 * 60 * 60 * 24));
});

// Virtual for file size in human readable format
fileSchema.virtual('humanReadableSize').get(function() {
  const bytes = this.size;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
});

// Static methods
fileSchema.statics.findByUserId = function(userId, type = null, limit = 20) {
  const query = { userId };
  if (type) query.type = type;
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(limit);
};

fileSchema.statics.findByConversationId = function(conversationId, limit = 10) {
  return this.find({ conversationId })
    .sort({ createdAt: -1 })
    .limit(limit);
};

fileSchema.statics.findRecentFiles = function(limit = 10, type = null) {
  const query = { processingStatus: 'completed' };
  if (type) query.type = type;
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(limit);
};

fileSchema.statics.findOldFiles = function(daysOld = 30) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysOld);
  
  return this.find({
    createdAt: { $lt: cutoffDate },
    processingStatus: { $ne: 'processing' }
  });
};

fileSchema.statics.getStorageStats = function() {
  return this.aggregate([
    {
      $group: {
        _id: '$type',
        count: { $sum: 1 },
        totalSize: { $sum: '$size' },
        avgSize: { $avg: '$size' }
      }
    }
  ]);
};

// Instance methods
fileSchema.methods.updateLastAccessed = function() {
  this.lastAccessed = new Date();
  this.downloadCount += 1;
  return this.save();
};

fileSchema.methods.addTag = function(tag) {
  if (!this.tags.includes(tag)) {
    this.tags.push(tag);
    return this.save();
  }
  return Promise.resolve(this);
};

fileSchema.methods.removeTag = function(tag) {
  this.tags = this.tags.filter(t => t !== tag);
  return this.save();
};

fileSchema.methods.updateProcessingStatus = function(status, error = null) {
  this.processingStatus = status;
  if (error) {
    this.processingError = error;
  }
  return this.save();
};

fileSchema.methods.markAsCompleted = function() {
  this.processingStatus = 'completed';
  this.processingError = null;
  return this.save();
};

fileSchema.methods.markAsFailed = function(error) {
  this.processingStatus = 'failed';
  this.processingError = error;
  return this.save();
};

// Pre-save middleware
fileSchema.pre('save', function(next) {
  if (this.isNew) {
    this.lastAccessed = new Date();
  }
  next();
});

// Pre-remove middleware to cleanup files
fileSchema.pre('deleteOne', { document: true, query: false }, async function(next) {
  try {
    const fileProcessingService = await import('../services/fileProcessingService.js');
    await fileProcessingService.default.deleteFile(this.fileId, this.fileName);
  } catch (error) {
    console.error('Error cleaning up file during deletion:', error);
    // Don't fail the deletion if file cleanup fails
  }
  next();
});

const File = mongoose.model('File', fileSchema);

export default File;
