import mongoose from 'mongoose';

const VisitorSchema = new mongoose.Schema({
  role: {
    type: String,
    enum: ['HR', 'Student', 'IT Employee', 'Teacher', 'Other'],
    required: true
  },
  ipAddress: {
    type: String
  },
  userAgent: {
    type: String
  },
  referrer: {
    type: String
  },
  visitDate: {
    type: Date,
    default: Date.now
  },
  pagesVisited: [{
    page: {
      type: String
    },
    timestamp: {
      type: Date,
      default: Date.now
    }
  }]
});

// Create a compound index on role and visitDate for efficient querying
VisitorSchema.index({ role: 1, visitDate: 1 });

const Visitor = mongoose.model('Visitor', VisitorSchema);

export default Visitor;
