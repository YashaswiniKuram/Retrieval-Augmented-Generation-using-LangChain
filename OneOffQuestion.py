import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables from .env
# Make sure your .env contains: GOOGLE_API_KEY=your_api_key_here
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

# Define the embedding model (Gemini's embeddings)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

if os.path.exists(persistent_directory):
    # Load the existing vector store with the embedding function
    db = Chroma(
        persist_directory=persistent_directory,
        embedding_function=embeddings
    )
    
    # Define the user's question
    query = input("Enter the Query : ") # "What does dracula fear the most?"
    
    # Retrieve relevant documents based on the query
    retriever = db.as_retriever(
        search_type="similarity", # Using different Searching type.
        search_kwargs={"k": 3},
    )
    relevant_docs = retriever.invoke(query)
    
    # # Display the relevant results with metadata
    # print("\n--- Relevant Documents ---")
    # for i, doc in enumerate(relevant_docs, 1):
    #     print(f"Document {i}:\n{doc.page_content}\n")
    #     if doc.metadata:
    #         print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")
    
    # Combine the query and the relevant document contents
    combined_input = (
        "Here are some documents that might help answer the question: "
        + query
        + "\n\nRelevant Documents:\n"
        + "\n\n".join([doc.page_content for doc in relevant_docs])
        + "\n\nPlease provide a rough answer based only on the provided documents. "
          "If the answer is not found in the documents, respond with 'I'm not sure'."
    )
    
    # Create a Gemini model
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    # Define the messages for the model
    messages = [
        SystemMessage(content="You are a helpful AI assistant, Which Helps in Retrieval of Information from Complex Documents"),
        HumanMessage(content=combined_input),
    ]
    
    # Invoke the model with the combined input
    result = model.invoke(messages)
    
    # Display the generated content
    print("\n--- Generated Response ---")
    print(result.content)
