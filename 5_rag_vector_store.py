import os
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

# --- Global Config ---
os.environ['LANGCHAIN_PROJECT'] = "Deep-Retrieval-Architecture"
load_dotenv()

SOURCE_PDF = "islr.pdf"

# --- Document Handling Modules ---
@traceable(name="execute_pdf_load")
def execute_pdf_load(path: str):
    return PyPDFLoader(path).load()

@traceable(name="segment_into_chunks")
def segment_into_chunks(docs, size=1100, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return splitter.split_documents(docs)

@traceable(name="initialize_faiss_index")
def initialize_faiss_index(chunks):
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2", 
        encode_kwargs={"normalize_embeddings": True}
    )
    return FAISS.from_documents(chunks, embedder)

# --- Integrated Pipeline Setup ---
@traceable(name="orchestrate_index_build", tags=["initialization"])
def orchestrate_index_build(pdf_path: str):
    print(f"Orchestrating index build for: {pdf_path}")
    raw_documents = execute_pdf_load(pdf_path)
    semantic_shards = segment_into_chunks(raw_documents)
    search_index = initialize_faiss_index(semantic_shards)
    return search_index

# --- Response Generation logic ---
def combine_context(shards):
    return "\n\n".join(s.page_content for s in shards)

@traceable(name="execute_deep_retrieval_query")
def execute_deep_retrieval_query(pdf_path: str, user_question: str):
    # Step A: Build/Load Index
    search_index = orchestrate_index_build(pdf_path)

    # Step B: Setup Retriever
    retrieval_unit = search_index.as_retriever(search_type="mmr", search_kwargs={"k": 5})

    # Step C: Configure Brain
    brain = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
    
    prompt_blueprint = ChatPromptTemplate.from_messages([
        ("system", "Use the provided domain-specific context to answer the inquiry. Maintain technical accuracy."),
        ("human", "Inquiry: {question}\n\nTechnical Context:\n{context}")
    ])

    # Step D: Construct Chain
    processing_pipeline = (
        RunnableParallel({
            "context": retrieval_unit | RunnableLambda(combine_context),
            "question": RunnablePassthrough(),
        })
        | prompt_blueprint 
        | brain 
        | StrOutputParser()
    )

    # Execution with detailed tracing
    config_overrides = {
        "run_name": "Semantic-Context-Query",
        "tags": ["Production-Grade", "RAG"],
        "metadata": {"search_algorithm": "MMR", "top_k": 5}
    }
    
    return processing_pipeline.invoke(user_question, config=config_overrides)

# --- Application Entry ---
if __name__ == "__main__":
    if not os.path.exists(SOURCE_PDF):
        print(f"Error: Document {SOURCE_PDF} not found.")
    else:
        print("Knowledge Retrieval System Online.")
        query = input("\nPlease enter your technical question: ").strip()
        
        try:
            final_output = execute_deep_retrieval_query(SOURCE_PDF, query)
            print("\n--- System Response ---")
            print(final_output)
        except Exception as error:
            print(f"Operational failure: {error}")
