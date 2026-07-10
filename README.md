# RAG Tutorial Projects

This workspace contains a collection of LangChain and RAG tutorials, along with two complete mini-projects that are the main focus of this repository:

- Shopping Assistant: [LangChain/ai-agent/10_project_shopping_agent](LangChain/ai-agent/10_project_shopping_agent)
- Telecom Support Chatbot: [LangChain/ai-agent/11_project_telecom_chatbot](LangChain/ai-agent/11_project_telecom_chatbot)

## Prerequisites

Make sure you have:

- Python 3.10+ installed
- A working internet connection for installing dependencies and using the LLM APIs
- A Groq API key for the LLM calls used by both projects

Create a `.env` file in the project root with your API key:

```bash
cd /Users/vaishalisomuramesh-personal/Desktop/Simplilearn/RAG/Tutorial
cat > .env <<'EOF'
GROQ_API_KEY=your_groq_api_key_here
EOF
```

## Setup

From the repository root, create and activate a virtual environment and install the required packages:

```bash
cd /Users/vaishalisomuramesh-personal/Desktop/Simplilearn/RAG/Tutorial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project 1: Shopping Agent

Location: [LangChain/ai-agent/10_project_shopping_agent](LangChain/ai-agent/10_project_shopping_agent)

This app is a Streamlit-based shopping assistant that lets users:

- search products from a local SQLite database
- get product ratings from review data
- place orders
- upload product images for visual matching

### Run the shopping app

```bash
cd /Users/vaishalisomuramesh-personal/Desktop/Simplilearn/RAG/Tutorial/LangChain/ai-agent/10_project_shopping_agent
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

### Optional quick test

You can also run a simple terminal-based demo:

```bash
python shopping_agent.py
```

## Project 2: Telecom Support Chatbot

Location: [LangChain/ai-agent/11_project_telecom_chatbot](LangChain/ai-agent/11_project_telecom_chatbot)

This project is a RAG chatbot for telecom customer support. It uses FAQ data, resolved tickets, and a PDF guide to answer user questions.

### Step 1: Build the vector database

Run these ingestion scripts once before starting the chatbot:

```bash
cd /Users/vaishalisomuramesh-personal/Desktop/Simplilearn/RAG/Tutorial/LangChain/ai-agent/11_project_telecom_chatbot
python ingest_faq.py
python ingest_tickets.py
python ingest_pdf.py
```

These commands populate the Chroma vector store inside the project's [LangChain/ai-agent/11_project_telecom_chatbot/chroma_store](LangChain/ai-agent/11_project_telecom_chatbot/chroma_store) folder.

### Step 2: Run the chatbot

#### Option A: Streamlit web app

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

#### Option B: Command-line chat

```bash
python main.py
```

## Notes

- If the app fails to start, check that your `.env` file contains a valid `GROQ_API_KEY`.
- The shopping app uses the local SQLite database in [LangChain/ai-agent/10_project_shopping_agent/store.db](LangChain/ai-agent/10_project_shopping_agent/store.db).
- The telecom app depends on the generated vector store, so make sure the ingestion scripts have been run at least once.
