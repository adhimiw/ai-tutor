import mongoose from 'mongoose';

const notificationSchema = new mongoose.Schema(
  {
    type: {
      type: String,
      enum: ['contact', 'system', 'job', 'project', 'visitor'],
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    message: {
      type: String,
      required: true,
    },
    priority: {
      type: String,
      enum: ['high', 'medium', 'low'],
      default: 'medium',
    },
    status: {
      type: String,
      enum: ['unread', 'read', 'archived', 'responded'],
      default: 'unread',
    },
    metadata: {
      contactId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Contact',
      },
      visitorId: String,
      email: String,
      name: String,
      aiSummary: String,
      aiSuggestedResponse: String,
      category: String,
      responseMessage: String,
    },
  },
  { timestamps: true }
);

// Create indexes for better query performance
notificationSchema.index({ status: 1 });
notificationSchema.index({ type: 1 });
notificationSchema.index({ priority: 1 });
notificationSchema.index({ createdAt: -1 });
notificationSchema.index({ 'metadata.contactId': 1 });

const Notification = mongoose.model('Notification', notificationSchema);

export default Notification;
