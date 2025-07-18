import mongoose from 'mongoose';

const CertificateSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  issuer: {
    type: String,
    required: true,
    trim: true
  },
  issueDate: {
    type: Date,
    required: true
  },
  expiryDate: {
    type: Date
  },
  credentialId: {
    type: String,
    trim: true
  },
  credentialUrl: {
    type: String,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  category: {
    type: String,
    enum: ['Technical', 'Professional', 'Academic', 'Other'],
    default: 'Technical'
  }
});

const EducationSchema = new mongoose.Schema({
  institution: {
    type: String,
    required: true,
    trim: true
  },
  level: {
    type: String,
    required: true,
    enum: ['SSLC', 'HSC', 'HSSC', 'Undergraduate', 'Postgraduate', 'Doctorate', 'Diploma', 'Certificate', 'Other'],
    default: 'Other'
  },
  degree: {
    type: String,
    trim: true
  },
  field: {
    type: String,
    required: true,
    trim: true
  },
  startDate: {
    type: Date,
    required: true
  },
  endDate: {
    type: Date
  },
  current: {
    type: Boolean,
    default: false
  },
  description: {
    type: String,
    trim: true
  },
  // New fields for marks/grades
  percentage: {
    type: Number,
    min: 0,
    max: 100
  },
  cgpa: {
    type: Number,
    min: 0,
    max: 10
  },
  totalSemesters: {
    type: Number,
    min: 1,
    max: 12
  },
  completedSemesters: {
    type: Number,
    min: 0,
    max: 12
  },
  boardOrUniversity: {
    type: String,
    trim: true
  }
});

const ExperienceSchema = new mongoose.Schema({
  company: {
    type: String,
    required: true,
    trim: true
  },
  position: {
    type: String,
    required: true,
    trim: true
  },
  startDate: {
    type: Date,
    required: true
  },
  endDate: {
    type: Date
  },
  current: {
    type: Boolean,
    default: false
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  responsibilities: {
    type: [String]
  }
});

const AboutSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  title: {
    type: String,
    required: true,
    trim: true
  },
  bio: {
    type: String,
    required: true,
    trim: true
  },
  avatar: {
    type: String,
    trim: true
  },
  education: [EducationSchema],
  experience: [ExperienceSchema],
  certificates: [CertificateSchema],
  location: {
    type: String,
    trim: true
  },
  email: {
    type: String,
    trim: true
  },
  resumeLink: {
    type: String,
    trim: true
  },
  socialLinks: {
    instagram: {
      type: String,
      trim: true
    },
    linkedin: {
      type: String,
      trim: true
    },
    github: {
      type: String,
      trim: true
    },
    medium: {
      type: String,
      trim: true
    }
  }
});

export default mongoose.model('About', AboutSchema);
