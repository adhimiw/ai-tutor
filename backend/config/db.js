import mongoose from 'mongoose';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the directory path of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
const envPath = join(dirname(__dirname), '../.env');
dotenv.config({ path: envPath });

const connectDB = async () => {
  try {
    // Set mongoose options
    mongoose.set('strictQuery', false);

    // Display connection string (without credentials if any)
    const mongoUriDisplay = process.env.MONGO_URI || 'Not defined';
    console.log(`Attempting to connect to MongoDB: ${mongoUriDisplay}`);

    // Connect to local MongoDB with optimized options
    const conn = await mongoose.connect(process.env.MONGO_URI, {
      serverSelectionTimeoutMS: 10000, // 10 seconds timeout
      socketTimeoutMS: 45000, // Close sockets after 45 seconds of inactivity
      connectTimeoutMS: 10000, // Connection timeout
      maxPoolSize: 10, // Limit connection pool size
      minPoolSize: 1,
      maxIdleTimeMS: 30000, // Close idle connections after 30 seconds
    });

    console.log(`MongoDB Connected: ${conn.connection.host}`);
    console.log(`Database: ${conn.connection.name}`);
    return conn;
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error.message}`);
    throw error;
  }
};

export default connectDB;
