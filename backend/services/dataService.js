import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the exported data from the portfolio project
const portfolioDataPath = '/home/adhithan/Downloads/Adhithan-Dev_portfolio-main/public/data';

class DataService {
  constructor() {
    this.data = {
      projects: [],
      skills: [],
      about: {},
      contact: {}
    };
    this.loadData();
  }

  loadData() {
    try {
      // Load Projects
      const projectsPath = join(portfolioDataPath, 'projects.json');
      if (fs.existsSync(projectsPath)) {
        this.data.projects = JSON.parse(fs.readFileSync(projectsPath, 'utf8'));
        console.log(`Loaded ${this.data.projects.length} projects`);
      }

      // Load Skills
      const skillsPath = join(portfolioDataPath, 'skills.json');
      if (fs.existsSync(skillsPath)) {
        this.data.skills = JSON.parse(fs.readFileSync(skillsPath, 'utf8'));
        console.log(`Loaded ${this.data.skills.length} skills`);
      }

      // Load About
      const aboutPath = join(portfolioDataPath, 'about.json');
      if (fs.existsSync(aboutPath)) {
        this.data.about = JSON.parse(fs.readFileSync(aboutPath, 'utf8'));
        console.log('Loaded about information');
      }

      // Load Contact
      const contactPath = join(portfolioDataPath, 'contact.json');
      if (fs.existsSync(contactPath)) {
        this.data.contact = JSON.parse(fs.readFileSync(contactPath, 'utf8'));
        console.log('Loaded contact information');
      }

      console.log('✅ Portfolio data loaded successfully for AI Tutor');
    } catch (error) {
      console.error('❌ Error loading portfolio data:', error.message);
      // Use fallback data if portfolio data is not available
      this.loadFallbackData();
    }
  }

  loadFallbackData() {
    console.log('Loading fallback data...');
    
    this.data = {
      projects: [
        {
          _id: '1',
          title: 'AI Tutor Application',
          description: 'An intelligent learning companion powered by Google Gemini 2.5 Pro',
          longDescription: 'This AI Tutor application provides personalized education experiences through AI-powered chat, interactive tutorials, and smart quizzes. Built with React, Node.js, and Google Gemini 2.5 Pro.',
          technologies: ['React', 'Node.js', 'Google Gemini 2.5 Pro', 'MongoDB', 'Socket.IO', 'Tailwind CSS'],
          images: ['/images/ai-tutor-1.jpg'],
          githubLink: 'https://github.com/adhimiw/ai-tutor',
          featured: true,
          createdAt: new Date()
        }
      ],
      skills: [
        { _id: '1', category: 'AI/ML', name: 'Google Gemini', level: 5, icon: 'brain' },
        { _id: '2', category: 'Frontend', name: 'React', level: 5, icon: 'react' },
        { _id: '3', category: 'Backend', name: 'Node.js', level: 4, icon: 'node' },
        { _id: '4', category: 'Database', name: 'MongoDB', level: 4, icon: 'mongodb' },
        { _id: '5', category: 'Tools', name: 'Socket.IO', level: 4, icon: 'websocket' }
      ],
      about: {
        _id: '1',
        name: 'Adhithan',
        title: 'AI Developer & Full Stack Engineer',
        bio: 'Passionate about creating intelligent applications that enhance learning and education. Experienced in AI integration, full-stack development, and creating user-centric solutions.',
        avatar: '/images/profile.jpg',
        location: 'India',
        email: 'adhithanraja6@gmail.com'
      },
      contact: {
        _id: '1',
        email: 'adhithanraja6@gmail.com',
        phone: '+91 XXXXXXXXXX',
        location: 'India',
        socialLinks: {
          github: 'https://github.com/adhimiw',
          linkedin: 'https://www.linkedin.com/in/adhithan-dev/',
          instagram: 'https://www.instagram.com/404_adhi.dev'
        }
      }
    };
  }

  // API methods
  async getProjects() {
    return this.data.projects;
  }

  async getSkills() {
    return this.data.skills;
  }

  async getAbout() {
    return this.data.about;
  }

  async getContact() {
    return this.data.contact;
  }

  async getFeaturedProjects() {
    return this.data.projects.filter(project => project.featured);
  }

  async getSkillsByCategory(category) {
    return this.data.skills.filter(skill => skill.category === category);
  }

  // Get all data for AI context
  async getAllData() {
    return {
      projects: this.data.projects,
      skills: this.data.skills,
      about: this.data.about,
      contact: this.data.contact
    };
  }
}

export default new DataService();
