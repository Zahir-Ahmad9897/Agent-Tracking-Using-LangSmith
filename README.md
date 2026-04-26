# Agent Tracking Using LangSmith

This repository demonstrates the foundational concepts of building and tracking AI agents using LangChain, Groq, and LangSmith. It provides clear, step-by-step examples of how to interact with Large Language Models (LLMs) and orchestrate complex workflows.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [Groq API Key](https://console.groq.com/)
- [LangSmith API Key](https://smith.langchain.com/) (Optional, for tracking)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Zahir-Ahmad9897/Agent-Tracking-Using-LangSmith.git
   cd Agent-Tracking-Using-LangSmith
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables in a `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=Agent-Tracking
   ```

## 📂 Core Examples

### 1. Basic LLM Call (`1_llm_basic_call.py`)
This script demonstrates the simplest way to interact with an LLM using LangChain. It sets up a basic prompt template and a chain to get a response from the `llama-3.3-70b-versatile` model.

**Key Features:**
- Prompt Template usage
- Integration with ChatGroq
- Output Parsing with `StrOutputParser`

### 2. Sequential Workflow (`2_sequential_workflow.py`)
This example shows how to chain multiple LLM calls together where the output of one step serves as the input to the next.

**Key Features:**
- Multi-step reasoning chains
- Custom LangSmith configuration (tags, metadata)
- Advanced workflow orchestration

## 🛠️ Usage

To run an example, simply execute the Python script:

```bash
python 1_llm_basic_call.py
```

---
Built with ❤️ using LangChain and Groq.
