import mongoose from 'mongoose';

const conversationSchema = new mongoose.Schema({
  conversationId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  userId: {
    type: String,
    required: false, // Optional for anonymous users
    index: true
  },
  title: {
    type: String,
    required: true,
    maxlength: 200
  },
  summary: {
    type: String,
    maxlength: 1000
  },
  messageCount: {
    type: Number,
    default: 0
  },
  lastActivity: {
    type: Date,
    default: Date.now,
    index: true
  },
  tags: [{
    type: String,
    maxlength: 50
  }],
  metadata: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    default: {}
  },
  isArchived: {
    type: Boolean,
    default: false
  },
  hasVectorMemory: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for better query performance
conversationSchema.index({ userId: 1, lastActivity: -1 });
conversationSchema.index({ conversationId: 1, userId: 1 });
conversationSchema.index({ isArchived: 1, lastActivity: -1 });

// Virtual for conversation age
conversationSchema.virtual('ageInDays').get(function() {
  return Math.floor((Date.now() - this.lastActivity) / (1000 * 60 * 60 * 24));
});

// Static methods
conversationSchema.statics.findByUserId = function(userId, limit = 20) {
  return this.find({ 
    userId, 
    isArchived: false 
  })
  .sort({ lastActivity: -1 })
  .limit(limit);
};

conversationSchema.statics.findRecentConversations = function(limit = 10) {
  return this.find({ isArchived: false })
    .sort({ lastActivity: -1 })
    .limit(limit);
};

conversationSchema.statics.archiveOldConversations = function(daysOld = 90) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysOld);
  
  return this.updateMany(
    { 
      lastActivity: { $lt: cutoffDate },
      isArchived: false 
    },
    { 
      isArchived: true 
    }
  );
};

// Instance methods
conversationSchema.methods.updateActivity = function() {
  this.lastActivity = new Date();
  return this.save();
};

conversationSchema.methods.incrementMessageCount = function() {
  this.messageCount += 1;
  this.lastActivity = new Date();
  return this.save();
};

conversationSchema.methods.addTag = function(tag) {
  if (!this.tags.includes(tag)) {
    this.tags.push(tag);
    return this.save();
  }
  return Promise.resolve(this);
};

conversationSchema.methods.removeTag = function(tag) {
  this.tags = this.tags.filter(t => t !== tag);
  return this.save();
};

// Pre-save middleware
conversationSchema.pre('save', function(next) {
  if (this.isNew) {
    this.lastActivity = new Date();
  }
  next();
});

const Conversation = mongoose.model('Conversation', conversationSchema);

export default Conversation;
