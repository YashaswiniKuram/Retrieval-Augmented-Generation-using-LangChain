from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from werkzeug.utils import secure_filename

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# ----------------------- CONFIGURATION -----------------------
UPLOAD_FOLDER = 'Docs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, "Docs")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

os.makedirs(books_dir, exist_ok=True)
os.makedirs(db_dir, exist_ok=True)

# ----------------------- HELPERS -----------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_document_loader(file_path, file_extension):
    if file_extension.lower() == 'txt':
        return TextLoader(file_path, encoding="utf-8")
    elif file_extension.lower() == 'pdf':
        return PyPDFLoader(file_path)
    elif file_extension.lower() in ['doc', 'docx']:
        return Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def chroma_settings():
    return Settings(
        persist_directory=persistent_directory,
        anonymized_telemetry=False   # Disable Chroma telemetry
    )


def get_vector_store():
    embeddings = get_embeddings()
    if os.path.exists(persistent_directory):
        return Chroma(
            persist_directory=persistent_directory,
            embedding_function=embeddings,
            client_settings=chroma_settings()
        )
    return None


def process_documents():
    supported_files = [
        f for f in os.listdir(books_dir)
        if any(f.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
    ]

    if not supported_files:
        return False

    documents = []
    for file in supported_files:
        try:
            file_path = os.path.join(books_dir, file)
            file_extension = file.rsplit('.', 1)[1].lower()

            loader = get_document_loader(file_path, file_extension)
            file_docs = loader.load()

            for doc in file_docs:
                doc.metadata = {"source": file, "type": file_extension}
            documents.extend(file_docs)

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=24)
    docs = text_splitter.split_documents(documents)

    embeddings = get_embeddings()
    db = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=persistent_directory,
        client_settings=chroma_settings()
    )
    db.persist()
    return True


# ----------------------- ROUTES -----------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/documents', methods=['GET'])
def list_documents():
    try:
        files = [
            {
                "filename": f,
                "type": f.rsplit('.', 1)[1].lower(),
                "size_mb": round(os.path.getsize(os.path.join(books_dir, f)) / (1024 * 1024), 2)
            }
            for f in os.listdir(books_dir)
            if any(f.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
        ]

        return jsonify({"documents": files, "count": len(files)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_document():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(books_dir, filename)
        file.save(file_path)

        success = process_documents()

        return jsonify({
            "message": "File uploaded",
            "processed": success,
            "filename": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Question is required"}), 400

        db = get_vector_store()
        if not db:
            return jsonify({"error": "Vector store empty. Upload documents first."}), 404

        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        relevant_docs = retriever.invoke(question)

        combined = (
            question + "\n\nRelevant Docs:\n" +
            "\n\n".join([doc.page_content for doc in relevant_docs]) +
            "\n\nAnswer only using the above data. If unsure, say 'I'm not sure'."
        )

        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", convert_system_message_to_human=True)

        result = model.invoke([
            SystemMessage(content="You answer strictly from the provided documents."),
            HumanMessage(content=combined)
        ])

        return jsonify({
            "question": question,
            "answer": result.content,
            "sources": [doc.metadata.get("source") for doc in relevant_docs]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "vector_store": "available" if get_vector_store() else "empty",
        "docs_dir": books_dir,
        "db_dir": persistent_directory
    })


# ----------------------- MAIN -----------------------
if __name__ == '__main__':
    if os.listdir(books_dir):
        print("Initializing vector store...")
        process_documents()
        print("Vector store Ready.")

    app.run(debug=True, host="0.0.0.0", port=5000)
