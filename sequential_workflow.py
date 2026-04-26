from importlib.metadata import metadata
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ['LANGCHAIN_PROJECT'] = 'Sequential LLM App'
load_dotenv()

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

model = ChatGroq(model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=500,
)

parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser

config = {
    'run_name' :'Sequential Chain',
    'tags' : ['LLM APP' , 'Summarizer' , 'Sequential Workflow'],
    'metadata' : {'model' : "Using Groq free model", 'model name' :'llama-3.3-70b-versatile' }
}
result = chain.invoke({'topic': 'what is AI in short'},config=config)

print(result)
