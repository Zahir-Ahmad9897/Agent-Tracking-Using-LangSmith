import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# Initialize configuration
load_dotenv()
os.environ['LANGCHAIN_PROJECT'] = 'Autonomous-Research-Agent'

# --- Custom Research Tools ---
web_search_utility = DuckDuckGoSearchRun()

@tool
def fetch_meteorological_info(city_name: str) -> str:
    """
    Retrieves current atmospheric and weather conditions for a specified city.
    """
    # Note: Access key is provided for demonstration. In production, use environment variables.
    api_key = "f07d9636974c4120025fadf60678771b"
    endpoint = f'https://api.weatherstack.com/current?access_key={api_key}&query={city_name}'

    try:
        api_response = requests.get(endpoint)
        api_response.raise_for_status()
        return api_response.json()
    except Exception as e:
        return f"Failed to retrieve weather data: {str(e)}"

# --- Agent Configuration ---
def initialize_research_agent():
    # 1. Brain Component
    brain_engine = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

    # 2. Reasoning Framework (Standard ReAct)
    reasoning_blueprint = hub.pull("hwchase17/react")

    # 3. Toolset Integration
    available_tools = [web_search_utility, fetch_meteorological_info]

    # 4. Agent Synthesis
    reasoning_agent = create_react_agent(
        llm=brain_engine,
        tools=available_tools,
        prompt=reasoning_blueprint
    )

    # 5. Operational Wrapper
    return AgentExecutor(
        agent=reasoning_agent,
        tools=available_tools,
        verbose=True,
        max_iterations=4,
        handle_parsing_errors=True
    )

if __name__ == "__main__":
    print("Research Agent Initialized. Processing query...")
    
    agent_orchestrator = initialize_research_agent()
    
    # Complex multi-step inquiry
    test_query = "Identify the home city of Albert Einstein and provide its current weather status."
    
    print(f"\n--- Executive Task: {test_query} ---\n")
    
    try:
        final_report = agent_orchestrator.invoke({"input": test_query})
        print("\n--- Final Agent Synthesis ---")
        print(final_report['output'])
    except Exception as operational_error:
        print(f"Agent reasoning failure: {operational_error}")