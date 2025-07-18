import mongoose from 'mongoose';

const deviceSchema = new mongoose.Schema(
  {
    userId: {
      type: String,
      required: true,
      index: true,
    },
    deviceType: {
      type: String,
      enum: ['web', 'android', 'ios'],
      default: 'web',
    },
    deviceToken: {
      type: String,
      required: true,
    },
    deviceName: {
      type: String,
    },
    isActive: {
      type: Boolean,
      default: true,
    },
    lastActive: {
      type: Date,
      default: Date.now,
    },
  },
  { timestamps: true }
);

// Create a compound index for userId and deviceToken
deviceSchema.index({ userId: 1, deviceToken: 1 }, { unique: true });

const Device = mongoose.model('Device', deviceSchema);

export default Device;
