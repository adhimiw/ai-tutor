import mongoose from 'mongoose';
import connectDB from '../config/db.js';

const setupDatabase = async () => {
  try {
    console.log('🔧 Setting up AI Tutor database...');
    
    // Connect to MongoDB
    await connectDB();
    
    // Get database instance
    const db = mongoose.connection.db;
    
    // Create collections if they don't exist
    const collections = ['projects', 'skills', 'abouts', 'contacts', 'users', 'messages'];
    
    for (const collectionName of collections) {
      try {
        await db.createCollection(collectionName);
        console.log(`✅ Created collection: ${collectionName}`);
      } catch (error) {
        if (error.code === 48) {
          console.log(`ℹ️  Collection already exists: ${collectionName}`);
        } else {
          console.error(`❌ Error creating collection ${collectionName}:`, error.message);
        }
      }
    }
    
    // Create indexes for better performance
    console.log('🔍 Creating database indexes...');
    
    // Projects indexes
    await db.collection('projects').createIndex({ title: 1 });
    await db.collection('projects').createIndex({ featured: 1 });
    await db.collection('projects').createIndex({ technologies: 1 });
    
    // Skills indexes
    await db.collection('skills').createIndex({ category: 1 });
    await db.collection('skills').createIndex({ name: 1 });
    
    // Users indexes
    await db.collection('users').createIndex({ email: 1 }, { unique: true });
    
    // Messages indexes
    await db.collection('messages').createIndex({ date: -1 });
    await db.collection('messages').createIndex({ read: 1 });
    
    console.log('✅ Database indexes created successfully');
    
    // Display database info
    const stats = await db.stats();
    console.log('\n📊 Database Statistics:');
    console.log(`Database: ${db.databaseName}`);
    console.log(`Collections: ${stats.collections}`);
    console.log(`Data Size: ${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`);
    
    console.log('\n🎓 AI Tutor database setup completed successfully!');
    console.log('💡 Next steps:');
    console.log('   1. Run "npm run import-data" to import portfolio data');
    console.log('   2. Run "npm run dev" to start the development server');
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Error setting up database:', error);
    process.exit(1);
  }
};

// Run the setup function
setupDatabase();
