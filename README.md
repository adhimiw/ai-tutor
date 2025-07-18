# 🎓 AI Tutor Application - Enhanced Edition

A comprehensive AI-powered tutoring application built with React and Node.js, featuring advanced Google Gemini 2.5 Flash integration, vector memory, and multimodal file processing capabilities.

## 🚀 Major Enhancements (Latest Update)

### ✨ **Vector Memory System**
- **Google Gemini Embeddings**: Integrated text-embedding-004 model for high-quality vector representations
- **Conversation Memory**: AI remembers previous conversations and can reference past discussions
- **Context-Aware Responses**: Retrieves relevant conversation history for more personalized tutoring
- **In-Memory Vector Store**: Fast similarity search with cosine similarity calculations

### 🔄 **Gemini 2.5 Flash Upgrade**
- **Latest Model**: Upgraded from gemini-2.0-flash-exp to gemini-2.5-flash for improved performance
- **Enhanced Context**: Support for 1M+ token context window for complex educational discussions
- **Multimodal Capabilities**: Advanced image understanding and document processing
- **Vision Integration**: Separate vision model for detailed image analysis

### 📁 **Advanced File Processing**
- **Multi-Format Support**: PDF documents, images (JPEG, PNG, WebP, HEIC, HEIF), and text files
- **PDF Text Extraction**: Automatic text extraction and chunking for searchable content
- **Image Analysis**: AI-powered image understanding with educational insights
- **Text File Processing**: Support for .txt and .md files with content analysis
- **Vector Integration**: File content stored in vector memory for intelligent retrieval

### 🎨 **Modern UI/UX Enhancements**
- **Drag-and-Drop Upload**: Intuitive file upload with preview and validation
- **File Attachment Display**: Visual indicators for uploaded files in chat
- **Enhanced Chat Interface**: Improved message display with file attachment support
- **Responsive Design**: Mobile-friendly interface with smooth animations
- **Error Handling**: Comprehensive error messages and graceful fallbacks

## 🏗️ **Technical Architecture**

### **Backend Services**
```
backend/
├── services/
│   ├── geminiService.js      # Enhanced Gemini 2.5 Flash integration
│   ├── vectorMemoryService.js # Google embeddings + vector storage
│   └── fileProcessingService.js # Multi-format file processing
├── models/
│   ├── Conversation.js       # Conversation metadata
│   └── File.js              # File metadata and tracking
└── server.js                # Express server with file upload support
```

### **Frontend Components**
```
src/
├── components/
│   └── FileUpload.jsx       # Advanced drag-and-drop file upload
├── pages/
│   └── ChatPage.jsx         # Enhanced chat with multimodal support
└── styles/                  # Tailwind CSS with custom components
```

## 🔧 **Features**

### **Core AI Capabilities**
- ✅ **Intelligent Tutoring**: Context-aware educational responses
- ✅ **Conversation Memory**: Remembers previous discussions and learning progress
- ✅ **Multimodal Learning**: Analyze images, documents, and text simultaneously
- ✅ **Document Understanding**: Extract insights from uploaded PDFs and text files
- ✅ **Image Analysis**: Educational analysis of uploaded images

### **File Processing**
- ✅ **PDF Processing**: Text extraction, chunking, and vector indexing
- ✅ **Image Processing**: Thumbnail generation, metadata extraction, AI analysis
- ✅ **Text File Support**: .txt and .md file processing with content analysis
- ✅ **File Management**: Upload, preview, delete, and search functionality
- ✅ **Vector Storage**: All file content searchable through vector similarity

### **User Experience**
- ✅ **Modern Interface**: Clean, responsive design with file upload support
- ✅ **Real-time Chat**: Fast AI responses with streaming support
- ✅ **File Attachments**: Send messages with multiple file attachments
- ✅ **Conversation History**: Persistent chat history with MongoDB storage
- ✅ **Error Handling**: Graceful fallbacks and user-friendly error messages

## 🛠️ **Tech Stack**

### **Frontend**
- **React 18**: Modern React with hooks and functional components
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Modern icon library

### **Backend**
- **Node.js**: JavaScript runtime environment
- **Express.js**: Web application framework
- **MongoDB**: Document database for conversation storage
- **Multer**: File upload middleware
- **Sharp**: Image processing library
- **PDF-Parse**: PDF text extraction

### **AI & ML**
- **Google Gemini 2.5 Flash**: Latest multimodal AI model
- **Text-Embedding-004**: Google's embedding model for vector representations
- **Vector Memory**: Custom in-memory vector store with cosine similarity
- **Multimodal Processing**: Image, text, and document understanding

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js (v18 or higher)
- MongoDB (local or cloud)
- Google Gemini API key

### **Installation**

1. **Clone the repository:**
```bash
git clone https://github.com/adhimiw/ai-tutor.git
cd ai-tutor
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Google Gemini API
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/ai-tutor
MONGO_URI=mongodb://localhost:27017/ai-tutor

# Server Configuration
PORT=5000
NODE_ENV=development

# Vector Memory Configuration
CHROMA_URL=http://localhost:8000

# File Upload Configuration
UPLOAD_DIR=./uploads

# Application Settings
APP_NAME="AI Tutor"
APP_VERSION="2.0.0"
```

4. **Start MongoDB:**
```bash
# If using local MongoDB
mongod
```

5. **Start the application:**
```bash
# Start both frontend and backend
npm run dev

# Or start separately:
npm run server    # Backend only
npm run client    # Frontend only
```

6. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📖 **Usage**

### **Basic Chat**
1. Navigate to the AI Chat page
2. Type your question in the input field
3. Press Enter or click Send
4. Neto will respond with educational content

### **File Upload & Analysis**
1. Click the paperclip icon in the chat interface
2. Drag and drop files or click to browse
3. Supported formats: PDF, images (JPEG, PNG, WebP, HEIC, HEIF), text files
4. Type a question about the uploaded files
5. Send the message to get AI analysis

### **Vector Memory**
- All conversations are automatically stored in vector memory
- AI can reference previous discussions and uploaded documents
- Context-aware responses based on conversation history

## 🔌 **API Endpoints**

### **Chat API**
```bash
POST /api/chat
Content-Type: multipart/form-data

# With text only
{
  "message": "Explain machine learning",
  "userId": "user123",
  "conversationId": "conv_123" // optional
}

# With files
FormData:
- message: "Analyze this document"
- files: [file1, file2, ...]
- userId: "user123"
```

### **Memory API**
```bash
# Get conversation history
GET /api/memory/conversations?limit=10

# Get vector memory stats
GET /api/memory/stats

# Search conversations
GET /api/memory/search?query=machine%20learning&limit=5
```

### **Files API**
```bash
# Get uploaded files
GET /api/files

# Get file by ID
GET /api/files/:fileId

# Delete file
DELETE /api/files/:fileId
```

## 🧪 **Testing**

### **Manual Testing**
1. **Basic Chat**: Send text messages and verify AI responses
2. **File Upload**: Test with PDF, image, and text files
3. **Multimodal Chat**: Send messages with file attachments
4. **Memory Retrieval**: Ask follow-up questions to test context awareness
5. **Error Handling**: Test with invalid files and network issues

### **API Testing**
```bash
# Test basic chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Neto!", "userId": "test"}'

# Test file upload
curl -X POST http://localhost:5000/api/chat \
  -F "message=Analyze this document" \
  -F "files=@document.pdf" \
  -F "userId=test"

# Test memory stats
curl -X GET http://localhost:5000/api/memory/stats
```

## 📊 **Performance Metrics**

- **Response Time**: ~5-10 seconds for complex AI responses
- **File Processing**: ~2-5 seconds for document analysis
- **Vector Search**: <100ms for similarity queries
- **Memory Usage**: Efficient in-memory vector storage
- **Scalability**: Supports multiple concurrent users

## 🔮 **Future Enhancements**

### **Planned Features**
- [ ] **User Authentication**: JWT-based user management
- [ ] **Performance Monitoring**: Core Web Vitals tracking
- [ ] **Advanced Analytics**: Usage statistics and learning progress
- [ ] **Real-time Streaming**: Live response streaming
- [ ] **Mobile App**: React Native mobile application
- [ ] **Collaborative Learning**: Multi-user study sessions

### **Technical Improvements**
- [ ] **Persistent Vector Storage**: ChromaDB or Pinecone integration
- [ ] **Caching Layer**: Redis for improved performance
- [ ] **Load Balancing**: Horizontal scaling support
- [ ] **CI/CD Pipeline**: Automated testing and deployment
- [ ] **Docker Support**: Containerized deployment

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a pull request

## 📝 **Changelog**

### **v2.0.0 (Latest)** - Enhanced AI Tutor
- ✅ Vector memory system with Google Gemini embeddings
- ✅ Gemini 2.5 Flash model upgrade
- ✅ Advanced file processing (PDF, images, text)
- ✅ Modern UI with drag-and-drop file upload
- ✅ Multimodal chat capabilities
- ✅ Conversation memory and context awareness

### **v1.0.0** - Initial Release
- ✅ Basic AI chat functionality
- ✅ React frontend with Tailwind CSS
- ✅ Node.js backend with Express
- ✅ MongoDB integration
- ✅ Google Gemini API integration

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Google Gemini**: For providing advanced AI capabilities
- **React Team**: For the excellent frontend framework
- **MongoDB**: For reliable data storage
- **Tailwind CSS**: For beautiful, responsive styling
- **Open Source Community**: For the amazing tools and libraries

---

**Built with ❤️ by Adhithan** | **Powered by Google Gemini 2.5 Flash**
