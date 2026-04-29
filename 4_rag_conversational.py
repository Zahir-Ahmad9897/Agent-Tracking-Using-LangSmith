import os
from dotenv import load_dotenv
from langsmith import traceable
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# --- Environment Configuration ---
os.environ['LANGCHAIN_PROJECT'] = "Advanced-Document-QA-System"
load_dotenv()

SOURCE_PDF = "islr.pdf"

# --- Traced Modular Components ---
@traceable(name="ingest_document")
def ingest_document(file_path: str):
    loader = PyPDFLoader(file_path)
    return loader.load()

@traceable(name="fragment_content")
def fragment_content(documents, size=1000, overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap
    )
    return splitter.split_documents(documents)

@traceable(name="create_semantic_store")
def create_semantic_store(shards):
    embeddings_engine = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_documents(shards, embeddings_engine)
    return vector_db

@traceable(name="initialize_qa_engine")
def initialize_qa_engine(path: str):
    raw_docs = ingest_document(path)
    content_shards = fragment_content(raw_docs)
    knowledge_base = create_semantic_store(content_shards)
    return knowledge_base

# --- Core Pipeline Logic ---
def format_shards(shards):
    return "\n\n".join(shard.page_content for shard in shards)

def build_qa_pipeline(knowledge_base):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    
    system_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an intelligent knowledge assistant. Answer questions based ONLY on the provided context. If the answer is not present, state that you cannot find the information."),
        ("human", "Question: {question}\n\nSupporting Context:\n{context}")
    ])

    retriever = knowledge_base.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    retrieval_bridge = RunnableParallel({
        "context": retriever | RunnableLambda(format_shards),
        "question": RunnablePassthrough(),
    })

    return retrieval_bridge | system_prompt | llm | StrOutputParser()

# --- Execution Entry Point ---
if __name__ == "__main__":
    if not os.path.exists(SOURCE_PDF):
        print(f"Error: {SOURCE_PDF} missing.")
    else:
        print("Initializing Advanced QA Engine...")
        kb = initialize_qa_engine(SOURCE_PDF)
        qa_pipeline = build_qa_pipeline(kb)
        
        print("\nQA System Ready. Enter your inquiry below:")
        user_query = input("Inquiry: ").strip()

        tracing_config = {
            "run_name": "Document-Interaction-Session",
            "metadata": {"source": "local_pdf", "engine": "Groq-Llama-3"}
        }

        try:
            response = qa_pipeline.invoke(user_query, config=tracing_config)
            print("\nAssistant Analysis:", response)
        except Exception as ex:
            print(f"System Error: {ex}")
