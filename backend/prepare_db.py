import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Configuration ---
load_dotenv()
# Use the correct environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATA_PATH = "backend/data"
DB_PATH = "backend/chroma_db"

# Ensure the necessary directories exist
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)


def create_db():
    """Loads PDF documents, splits them, and creates a Chroma vector store."""
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found in .env file. Please add your key.")
        return

    # 1. Load Documents
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the 'backend/data' directory. Please add your PDF files.")
        return

    print(f"Loading {len(pdf_files)} PDF documents...")
    all_documents = []
    for pdf_file in pdf_files:
        # Load PDF, splitting it into smaller, manageable chunks
        loader = PyPDFLoader(os.path.join(DATA_PATH, pdf_file))
        # Note: PyPDFLoader's load_and_split method is now an instance method
        documents = loader.load_and_split()
        all_documents.extend(documents)

    if not all_documents:
        print("Documents loaded but failed to split. Check PDF content.")
        return

    print(f"Total document chunks: {len(all_documents)}")

    # 2. Create Embeddings and Vector Store
    print("Creating Chroma database using Google embeddings...")

    # Initialize Google Embeddings
    # Use the specific, current embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model="text-embedding-004",

    )

    # Create the vector store
    vector_store = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    # NOTE: vector_store is intentionally unused, its creation saves the data.
    # We do not need to call .persist() with newer versions of Chroma.

    print(f"Successfully created Chroma database in {DB_PATH}")


if __name__ == "__main__":
    create_db()