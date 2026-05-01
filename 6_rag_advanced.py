import os
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from langsmith import traceable

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# --- Project Identity ---
os.environ['LANGCHAIN_PROJECT'] = "Persistent-Knowledge-Hub"
load_dotenv()

SOURCE_PDF = "islr.pdf"
CACHE_DIRECTORY = Path(".persistent_indices")
CACHE_DIRECTORY.mkdir(exist_ok=True)

# --- Utility Functions (Internal Tracing) ---
@traceable(name="internal_pdf_ingestion")
def internal_pdf_ingestion(path: str):
    return PyPDFLoader(path).load()

@traceable(name="segment_source_material")
def segment_source_material(docs, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)

@traceable(name="generate_vector_embeddings")
def generate_vector_embeddings(shards, model_identifier: str):
    embeddings_engine = HuggingFaceEmbeddings(model_name=model_identifier)
    return FAISS.from_documents(shards, embeddings_engine)

# --- Fingerprinting Logic ---
def _compute_document_hash(path: str) -> dict:
    p = Path(path)
    sha_hash = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha_hash.update(chunk)
    return {
        "fingerprint": sha_hash.hexdigest(),
        "filesize": p.stat().st_size,
        "last_modified": int(p.stat().st_mtime)
    }

def _get_unique_cache_key(pdf_path: str, chunk_size: int, chunk_overlap: int, model_name: str) -> str:
    metadata = {
        "file_details": _compute_document_hash(pdf_path),
        "params": {"size": chunk_size, "overlap": chunk_overlap},
        "model": model_name,
        "version": "2.0"
    }
    return hashlib.sha256(json.dumps(metadata, sort_keys=True).encode("utf-8")).hexdigest()

# --- Cache Management Runs ---
@traceable(name="retrieve_cached_index", tags=["caching"])
def retrieve_cached_index(index_path: Path, model_name: str):
    engine = HuggingFaceEmbeddings(model_name=model_name)
    return FAISS.load_local(str(index_path), engine, allow_dangerous_deserialization=True)

@traceable(name="build_and_persist_index", tags=["caching"])
def build_and_persist_index(pdf_path: str, index_path: Path, chunk_size: int, chunk_overlap: int, model_name: str):
    print("No valid cache found. Rebuilding knowledge index...")
    raw_docs = internal_pdf_ingestion(pdf_path)
    shards = segment_source_material(raw_docs, chunk_size, chunk_overlap)
    vector_store = generate_vector_embeddings(shards, model_name)
    
    index_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_path))
    
    (index_path / "index_manifest.json").write_text(json.dumps({
        "original_file": os.path.abspath(pdf_path),
        "configuration": {"size": chunk_size, "overlap": chunk_overlap, "model": model_name}
    }, indent=4))
    
    return vector_store

# --- High-Level API ---
def get_intelligent_index(pdf_path: str, chunk_size=1000, chunk_overlap=150, model_name="all-MiniLM-L6-v2", force_refresh=False):
    key = _get_unique_cache_key(pdf_path, chunk_size, chunk_overlap, model_name)
    index_path = CACHE_DIRECTORY / key
    
    if index_path.exists() and not force_refresh:
        print("Optimized: Loading knowledge from local cache.")
        return retrieve_cached_index(index_path, model_name)
    else:
        return build_and_persist_index(pdf_path, index_path, chunk_size, chunk_overlap, model_name)

def format_context_string(docs):
    return "\n\n".join(d.page_content for d in docs)

@traceable(name="execute_intelligent_rag_workflow")
def execute_intelligent_rag_workflow(pdf_path: str, inquiry: str, **kwargs):
    # Load or rebuild the index
    knowledge_base = get_intelligent_index(pdf_path, **kwargs)
    
    # Setup the retrieval-augmented chain
    retriever = knowledge_base.as_retriever(search_kwargs={"k": 5})
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    blueprint = ChatPromptTemplate.from_messages([
        ("system", "You are an expert system. Extract answers exclusively from the context. If uncertain, admit limitations."),
        ("human", "User Inquiry: {question}\n\nContextual Data:\n{context}")
    ])

    pipeline = (
        RunnableParallel({
            "context": retriever | RunnableLambda(format_context_string),
            "question": RunnablePassthrough(),
        })
        | blueprint 
        | llm 
        | StrOutputParser()
    )

    return pipeline.invoke(inquiry, config={"run_name": "Intelligent-RAG-Session", "tags": ["Enterprise", "Cached"]})

# --- CLI Implementation ---
if __name__ == "__main__":
    if not os.path.exists(SOURCE_PDF):
        print(f"Operational Alert: {SOURCE_PDF} not detected.")
    else:
        print("Welcome to the Persistent Knowledge Hub.")
        user_input = input("\nWhat information would you like to extract? ").strip()
        
        try:
            result = execute_intelligent_rag_workflow(SOURCE_PDF, user_input)
            print("\nExtracted Intelligence:\n", result)
        except Exception as error:
            print(f"Error during intelligence extraction: {error}")
