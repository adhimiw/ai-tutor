import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

import connectDB from '../config/db.js';
import Project from '../models/Project.js';
import Skill from '../models/Skill.js';
import About from '../models/About.js';
import Contact from '../models/Contact.js';

// Get the directory path of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the exported data from the portfolio project
const portfolioDataPath = '/home/adhithan/Downloads/Adhithan-Dev_portfolio-main/public/data';

const importData = async () => {
  try {
    // Connect to local MongoDB
    await connectDB();
    console.log('Connected to local MongoDB for data import');

    // Clear existing data
    await Project.deleteMany();
    await Skill.deleteMany();
    await About.deleteMany();
    await Contact.deleteMany();
    console.log('Existing data cleared');

    // Import Projects
    const projectsPath = join(portfolioDataPath, 'projects.json');
    if (fs.existsSync(projectsPath)) {
      const projectsData = JSON.parse(fs.readFileSync(projectsPath, 'utf8'));
      if (projectsData && projectsData.length > 0) {
        await Project.insertMany(projectsData);
        console.log(`Imported ${projectsData.length} projects`);
      }
    }

    // Import Skills
    const skillsPath = join(portfolioDataPath, 'skills.json');
    if (fs.existsSync(skillsPath)) {
      const skillsData = JSON.parse(fs.readFileSync(skillsPath, 'utf8'));
      if (skillsData && skillsData.length > 0) {
        await Skill.insertMany(skillsData);
        console.log(`Imported ${skillsData.length} skills`);
      }
    }

    // Import About
    const aboutPath = join(portfolioDataPath, 'about.json');
    if (fs.existsSync(aboutPath)) {
      const aboutData = JSON.parse(fs.readFileSync(aboutPath, 'utf8'));
      if (aboutData && Object.keys(aboutData).length > 0) {
        await About.create(aboutData);
        console.log('Imported about information');
      }
    }

    // Import Contact
    const contactPath = join(portfolioDataPath, 'contact.json');
    if (fs.existsSync(contactPath)) {
      const contactData = JSON.parse(fs.readFileSync(contactPath, 'utf8'));
      if (contactData && Object.keys(contactData).length > 0) {
        await Contact.create(contactData);
        console.log('Imported contact information');
      }
    }

    console.log('✅ All data imported successfully to local MongoDB!');
    console.log('🎓 AI Tutor database is ready with portfolio data');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error importing data:', error);
    process.exit(1);
  }
};

// Run the import function
importData();
