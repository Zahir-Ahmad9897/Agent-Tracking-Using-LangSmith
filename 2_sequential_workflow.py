import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Set a unique LangSmith project identifier
os.environ['LANGCHAIN_PROJECT'] = 'Sequential-Intelligence-Pipeline'
load_dotenv()

# Step 1: Content Generation Template
content_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert technical writer."),
    ("human", "Draft a professional technical report on the topic: {subject}")
])

# Step 2: Insight Extraction Template
insight_summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior analyst specializing in concise summaries."),
    ("human", "Extract 5 critical action items from the following report:\n\n{draft_report}")
])

# Core LLM Engine
logic_engine = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.6,
    max_tokens=800,
)

# Standard Output Parser
response_parser = StrOutputParser()

# Define the intelligence pipeline
# Flow: Generator -> LLM -> Parser -> Summarizer -> LLM -> Parser
intelligence_pipeline = (
    content_generator_prompt 
    | logic_engine 
    | response_parser 
    | insight_summarizer_prompt 
    | logic_engine 
    | response_parser
)

def execute_sequential_workflow():
    # LangSmith Configuration for tracing
    execution_config = {
        'run_name': 'Automated-Insight-Extraction',
        'tags': ['Production', 'Summarizer', 'V1.0'],
        'metadata': {
            'engine_type': 'Groq-Llama-70b',
            'environment': 'development'
        }
    }
    
    try:
        topic = 'The impact of Quantum Computing on Cybersecurity'
        print(f"Starting pipeline for topic: {topic}\n")
        
        final_insights = intelligence_pipeline.invoke(
            {'subject': topic}, 
            config=execution_config
        )
        
        print("--- Final Extracted Insights ---")
        print(final_insights)
        
    except Exception as error:
        print(f"Pipeline execution failed: {error}")

if __name__ == "__main__":
    execute_sequential_workflow()
