import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI

load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Path to your folder
docs_folder = "documents"
all_docs = []

print(f"Scanning folder: {docs_folder}...")

# --- STEP 1: AUTOMATIC FILE LOADING ---
for filename in os.listdir(docs_folder):
    file_path = os.path.join(docs_folder, filename)
    
    try:
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            all_docs.extend(loader.load())
            print(f"Loaded PDF: {filename}")
            
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
            all_docs.extend(loader.load())
            print(f"Loaded TXT: {filename}")
            
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# --- STEP 2: CHUNKING & INDEXING ---
if all_docs:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = text_splitter.split_documents(all_docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Save the index
    vectorstore.save_local("LifeTrail_Combined_Index_Final")

    print("-" * 30)
    print(f"SUCCESS: Knowledge Base Updated!")
    print(f"Total Files Loaded: {len(os.listdir(docs_folder))}")
    print(f"Total Semantic Chunks: {len(chunks)}")
    print("-" * 30)
else:
    print("No documents found in the folder. Check your path!")