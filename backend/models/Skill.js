import mongoose from 'mongoose';

const SkillSchema = new mongoose.Schema({
  category: {
    type: String,
    required: true,
    trim: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  level: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  icon: {
    type: String,
    trim: true
  }
}, { timestamps: true }); // Add timestamps option

export default mongoose.model('Skill', SkillSchema);
