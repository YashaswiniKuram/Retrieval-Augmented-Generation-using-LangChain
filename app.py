from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import getpass
import dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from werkzeug.utils import secure_filename
import json

# Load environment variables
dotenv.load_dotenv()

# Ensure API key exists
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google API Key: ")

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'Docs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, "Docs")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

# Ensure directories exist
os.makedirs(books_dir, exist_ok=True)
os.makedirs(db_dir, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_document_loader(file_path, file_extension):
    """Get appropriate document loader based on file extension"""
    if file_extension.lower() == 'txt':
        return TextLoader(file_path, encoding="utf-8")
    elif file_extension.lower() == 'pdf':
        return PyPDFLoader(file_path)
    elif file_extension.lower() in ['doc', 'docx']:
        return Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def get_vector_store():
    """Get or create the Chroma vector store"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    if os.path.exists(persistent_directory):
        return Chroma(
            persist_directory=persistent_directory,
            embedding_function=embeddings
        )
    else:
        return None

def process_documents():
    """Process all documents in the Docs folder and create/update vector store"""
    if not os.path.exists(books_dir):
        return False
    
    # Get all supported file types
    supported_files = []
    for f in os.listdir(books_dir):
        if any(f.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            supported_files.append(f)
    
    if not supported_files:
        return False
    
    documents = []
    for book_file in supported_files:
        try:
            file_path = os.path.join(books_dir, book_file)
            file_extension = book_file.rsplit('.', 1)[1].lower()
            
            loader = get_document_loader(file_path, file_extension)
            book_docs = loader.load()
            
            for doc in book_docs:
                doc.metadata = {"source": book_file, "type": file_extension}
                documents.append(doc)
                
        except Exception as e:
            print(f"Error processing {book_file}: {str(e)}")
            continue
    
    if not documents:
        return False
    
    text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=24)
    docs = text_splitter.split_documents(documents)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create or update the vector store
    db = Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
    db.persist()
    
    return True

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """GET endpoint for listing available documents"""
    try:
        if not os.path.exists(books_dir):
            return jsonify({"documents": [], "message": "No documents directory found"})
        
        documents = []
        for filename in os.listdir(books_dir):
            if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                file_path = os.path.join(books_dir, filename)
                file_size = os.path.getsize(file_path)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                documents.append({
                    "filename": filename,
                    "type": file_extension,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                })
        
        return jsonify({
            "documents": documents,
            "count": len(documents),
            "message": "Documents retrieved successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """POST endpoint for uploading and processing new documents"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(books_dir, filename)
            
            # Save the file
            file.save(file_path)
            
            # Process all documents and update vector store
            success = process_documents()
            
            if success:
                return jsonify({
                    "message": "Document uploaded and processed successfully",
                    "filename": filename,
                    "vector_store_updated": True
                }), 200
            else:
                return jsonify({
                    "message": "Document uploaded but vector store update failed",
                    "filename": filename,
                    "vector_store_updated": False
                }), 200
        else:
            return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """POST endpoint for asking questions (similar to QNA.py)"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data['question']
        
        # Get the vector store
        db = get_vector_store()
        if not db:
            return jsonify({"error": "Vector store not found. Please upload documents first."}), 404
        
        # Retrieve relevant documents
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )
        relevant_docs = retriever.invoke(question)
        
        # Combine the query and relevant documents
        combined_input = (
            "Here are some documents that might help answer the question: "
            + question
            + "\n\nRelevant Documents:\n"
            + "\n\n".join([doc.page_content for doc in relevant_docs])
            + "\n\nPlease provide a comprehensive answer based only on the provided documents. "
              "If the answer is not found in the documents, respond with 'I'm not sure'."
        )
        
        # Create Gemini model and get response
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            convert_system_message_to_human=True
        )
        messages = [
            SystemMessage(content="You are a helpful AI assistant that helps in retrieval of information from complex documents. Provide accurate answers based only on the provided documents."),
            HumanMessage(content=combined_input),
        ]
        
        result = model.invoke(messages)
        
        # Prepare response with metadata
        response_data = {
            "question": question,
            "answer": result.content,
            "sources": [doc.metadata.get('source', 'Unknown') for doc in relevant_docs],
            "relevant_chunks": len(relevant_docs)
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_vector_store()
        vector_store_status = "available" if db else "not_found"
        
        return jsonify({
            "status": "healthy",
            "vector_store": vector_store_status,
            "documents_directory": books_dir,
            "vector_store_directory": persistent_directory
        }), 200
    
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # Initialize vector store if documents exist
    if os.path.exists(books_dir) and os.listdir(books_dir):
        print("Initializing vector store...")
        process_documents()
        print("Vector store initialized successfully!")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 