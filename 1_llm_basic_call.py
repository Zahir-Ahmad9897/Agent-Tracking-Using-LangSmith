import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize environment
load_dotenv()

# Define a more structured input template
input_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and concise research assistant."),
    ("human", "{user_query}")
])

# Initialize the Groq inference engine
inference_engine = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    max_tokens=600,
)

# Output processor to handle string results
output_processor = StrOutputParser()

# Construct the simple completion flow
simple_completion_flow = input_template | inference_engine | output_processor

def run_basic_inference():
    try:
        # Example query
        query = "Summarize the significance of data privacy in the 21st century."
        print(f"Running inference for query: {query}\n")
        
        # Execute the flow
        response = simple_completion_flow.invoke({"user_query": query})
        
        print("--- Response Received ---")
        print(response)
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    run_basic_inference()
