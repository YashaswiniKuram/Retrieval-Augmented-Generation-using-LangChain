# RAG Chat Assistant - Complete System

A complete RAG (Retrieval-Augmented Generation) system with a modern web interface that allows users to upload documents (PDF, DOC, DOCX, TXT) and chat with an AI assistant about their content.

## ✨ Features

### Backend (Flask API)
- **Multi-format Document Support**: PDF, DOC, DOCX, and TXT files
- **Document Processing**: Automatic chunking and vector embedding
- **Vector Store**: ChromaDB integration with Google Gemini embeddings
- **RESTful API**: Clean endpoints for all operations
- **Real-time Processing**: Instant document processing and vector store updates

### Frontend (Modern Web Interface)
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Drag & Drop Upload**: Easy file upload with visual feedback
- **Chat Interface**: Real-time conversation with AI assistant
- **Chat History**: Persistent chat history using localStorage
- **Document Management**: Visual document list with file types and sizes
- **Connection Status**: Real-time backend connection monitoring
- **Modern UI**: Beautiful gradient design with smooth animations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file in your project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open Your Browser
Navigate to `http://localhost:5000`

## 📁 Project Structure

```
RAG/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── test_api.py           # API testing script
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── app.js            # Frontend JavaScript
├── Docs/                 # Document storage directory
├── db/                   # ChromaDB storage
└── README.md            # This file
```

## 🔌 API Endpoints

### Web Interface
- **GET** `/` - Main web interface

### API Endpoints
- **GET** `/api/health` - System health check
- **GET** `/api/documents` - List all documents
- **POST** `/api/upload` - Upload and process documents
- **POST** `/api/ask` - Ask questions about documents

## 💻 Frontend Features

### Document Upload
- **Drag & Drop**: Simply drag files onto the upload area
- **File Browser**: Click to browse and select files
- **Multiple Files**: Upload several files at once
- **Progress Feedback**: Visual upload progress indicators
- **File Validation**: Automatic file type checking

### Chat Interface
- **Real-time Responses**: Instant AI responses
- **Typing Indicators**: Shows when AI is processing
- **Message History**: Persistent chat history
- **Source Attribution**: Shows which documents were referenced
- **Responsive Input**: Auto-expanding text area

### Document Management
- **Visual File List**: See all uploaded documents
- **File Type Icons**: Color-coded by document type
- **File Sizes**: Display file sizes in MB
- **Connection Status**: Real-time backend status

## 🎨 UI/UX Features

### Design
- **Modern Gradients**: Beautiful color schemes
- **Smooth Animations**: Fade-in effects and transitions
- **Responsive Layout**: Adapts to any screen size
- **Card-based Design**: Clean, organized interface
- **Icon Integration**: FontAwesome icons throughout

### User Experience
- **Intuitive Navigation**: Easy-to-use interface
- **Visual Feedback**: Hover effects and animations
- **Error Handling**: Clear error messages
- **Success Notifications**: Toast notifications for actions
- **Loading States**: Visual feedback during operations

## 🔧 Configuration

### Supported File Types
- **PDF**: `.pdf` files
- **Word Documents**: `.doc` and `.docx` files
- **Text Files**: `.txt` files

### File Limits
- **Maximum Size**: 16MB per file
- **Chunk Size**: 1024 characters
- **Chunk Overlap**: 24 characters

### Vector Store
- **Database**: ChromaDB
- **Embeddings**: Google Gemini (models/embedding-001)
- **Model**: Gemini 2.5 Flash for responses

## 📱 Mobile Support

The interface is fully responsive and works great on:
- **Desktop**: Full-featured experience
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Touch-friendly interface for small screens

## 🚀 Advanced Features

### Chat History Persistence
- **localStorage**: Chat history saved in browser
- **Session Persistence**: Maintains conversations across browser sessions
- **Clear History**: Option to clear chat history
- **Message Metadata**: Stores sources and timestamps

### Real-time Updates
- **Connection Monitoring**: Live backend status
- **Document Sync**: Automatic document list updates
- **Vector Store Status**: Real-time processing status
- **Error Handling**: Graceful error recovery

## 🛠️ Development

### Running in Development Mode
```bash
python app.py
```
The app runs with debug mode enabled and auto-reloads on changes.

### Testing the API
```bash
python test_api.py
```

### Frontend Development
- HTML template: `templates/index.html`
- JavaScript: `static/app.js`
- CSS: Embedded in HTML for simplicity

## 🔒 Security Features

- **File Type Validation**: Only allowed file types accepted
- **File Size Limits**: Prevents large file uploads
- **Secure Filenames**: Prevents path traversal attacks
- **CORS Support**: Configurable cross-origin requests

## 📊 Performance

- **Asynchronous Processing**: Non-blocking file uploads
- **Efficient Chunking**: Optimized document processing
- **Vector Store Caching**: Persistent ChromaDB storage
- **Memory Management**: Efficient document handling

## 🚀 Deployment

### Production Considerations
- **Environment Variables**: Secure API key management
- **Static File Serving**: Optimized for production
- **Error Logging**: Comprehensive error handling
- **Health Monitoring**: Built-in health check endpoint

### Scaling
- **Stateless Design**: Easy horizontal scaling
- **Database Persistence**: ChromaDB can be externalized
- **Load Balancing**: API endpoints support load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

### Common Issues
1. **Vector Store Not Found**: Ensure documents exist in `Docs/` folder
2. **API Key Issues**: Check your `.env` file and Google API key
3. **File Upload Errors**: Verify file type and size limits
4. **Port Conflicts**: Change port in `app.py` if needed

### Getting Help
- Check the console for error messages
- Verify your Google API key is valid
- Ensure all dependencies are installed
- Check file permissions for upload directory

## 🎯 Future Enhancements

- [ ] User authentication and management
- [ ] Document deletion and management
- [ ] Support for more file formats (images, audio)
- [ ] Advanced search and filtering
- [ ] Export chat conversations
- [ ] Multi-language support
- [ ] Advanced analytics and insights
- [ ] Integration with cloud storage
- [ ] Real-time collaboration features 