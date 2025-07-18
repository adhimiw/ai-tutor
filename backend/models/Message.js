import mongoose from 'mongoose';

const MessageSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  visitorId: {
    type: String
  },
  role: {
    type: String,
    enum: ['HR', 'Student', 'IT Employee', 'Teacher', 'Other']
  },
  date: {
    type: Date,
    default: Date.now
  },
  read: {
    type: Boolean,
    default: false
  }
});

const Message = mongoose.model('Message', MessageSchema);

export default Message;
