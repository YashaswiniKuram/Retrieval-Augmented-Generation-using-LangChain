import os
import getpass
import dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
dotenv.load_dotenv()

# Ensure API key exists
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter OpenAI API Key: ")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, "Docs")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

print(f"Books directory: {books_dir}")
print(f"Persistent directory: {persistent_directory}")

# Ensure DB folder exists
os.makedirs(db_dir, exist_ok=True)

if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    if not os.path.exists(books_dir):
        raise FileNotFoundError(f"Directory {books_dir} does not exist.")

    book_files = [f for f in os.listdir(books_dir) if f.endswith(".txt")] # Gets all the text files

    documents = []
    for book_file in book_files:
        loader = TextLoader(os.path.join(books_dir, book_file), encoding="utf-8")
        book_docs = loader.load()
        for doc in book_docs:
            doc.metadata = {"source": book_file}
            documents.append(doc)

    text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=24)
    docs = text_splitter.split_documents(documents)
    print(f"Number of document chunks: {len(docs)}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    db = Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
    print("Vector store created and persisted.")

else:
    print("Vector store already exists.")
