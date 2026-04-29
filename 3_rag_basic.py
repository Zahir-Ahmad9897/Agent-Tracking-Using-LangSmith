import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Initialization
load_dotenv()
os.environ['LANGCHAIN_PROJECT'] = "Knowledge-Retrieval-Core"

SOURCE_DOCUMENT = "islr.pdf"

def run_semantic_search_pipeline():
    if not os.path.exists(SOURCE_DOCUMENT):
        print(f"Error: Required file '{SOURCE_DOCUMENT}' not found in the workspace.")
        return

    try:
        # 1. Document Ingestion
        print(f"Ingesting document: {SOURCE_DOCUMENT}...")
        document_loader = PyPDFLoader(SOURCE_DOCUMENT)
        raw_data = document_loader.load()

        # 2. Semantic Chunking
        print("Segmenting content into shards...")
        content_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, 
            chunk_overlap=250
        )
        content_shards = content_splitter.split_documents(raw_data)

        # 3. Embedding & Indexing
        print("Generating embeddings and building semantic index...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        semantic_index = FAISS.from_documents(documents=content_shards, embedding=embedding_model)
        knowledge_retriever = semantic_index.as_retriever()

        # 4. LLM & Contextual Prompt
        print("Configuring retrieval-augmented generation engine...")
        llm_engine = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        
        instruction_template = """You are a highly capable documentation assistant. 
        Use the following retrieved context to answer the user's question accurately.
        
        Context:
        {context}

        Question: {question}
        
        Answer professionally and clearly:"""
        
        rag_prompt = ChatPromptTemplate.from_template(instruction_template)

        # 5. RAG Pipeline Construction
        retrieval_chain = (
            {"context": knowledge_retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | llm_engine
            | StrOutputParser()
        )

        # 6. Execution
        query = "What are the fundamental principles of statistical learning discussed here?"
        print(f"\nDispatching query: {query}")
        answer = retrieval_chain.invoke(query)
        
        print("\n--- Synthesis Result ---")
        print(answer)

    except Exception as e:
        print(f"Retrieval pipeline error: {e}")

if __name__ == "__main__":
    run_semantic_search_pipeline()
