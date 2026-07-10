# Telecom Support Chatbot (RAG)

## Demo

<video src="resources/demo.mov" controls width="700"></video>

If your Markdown viewer doesn't render inline video (e.g. GitHub.com without the asset-upload flow), [download/view the demo directly](resources/demo.mp4).

## Retrieval Overview

```text
                    User Question
                          │
                          ▼
                  "Internet disconnects"
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
     FAQ Search      Ticket Search     Guide Search
        │                 │                 │
      3 Docs           3 Docs           3 Docs
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
              Combined List (9 Documents)
                          │
                          ▼
                Format into Prompt Context
                          │
                          ▼
                      LLM (Qwen)
                          │
                          ▼
              ✅ One Final Answer
```

## Full Flow
  

```mermaid
flowchart TD

    %% User
    U["👤 User<br/>My internet disconnects every evening"]

    %% Main
    MAIN["main.py<br/><br/>question = input()<br/>chain.stream(question)"]

    %% RAG Chain
    RAG["rag_chain.py<br/><br/>Input Question"]

    U --> MAIN
    MAIN --> RAG

    %% Retrieval
    subgraph Retrieval["Retrieval Stage"]

        RL["RunnableLambda(retrieve)"]

        EMB["Convert Question<br/>to Embedding"]

        FAQ["FAQ Retriever"]
        TICKET["Ticket Retriever"]
        GUIDE["Guide Retriever"]

        FAQTOP["Top 3 FAQs"]
        TICKETTOP["Top 3 Tickets"]
        GUIDETOP["Top 3 Guide Chunks"]

        MERGE["Merge Retrieved Documents<br/>(9 Documents)"]

        RL --> EMB

        EMB --> FAQ
        EMB --> TICKET
        EMB --> GUIDE

        FAQ --> FAQTOP
        TICKET --> TICKETTOP
        GUIDE --> GUIDETOP

        FAQTOP --> MERGE
        TICKETTOP --> MERGE
        GUIDETOP --> MERGE

    end

    RAG --> RL

    %% Formatting
    subgraph Format["Document Formatting"]

        FORMAT["_format_docs(docs)"]

        CONTEXT["One Context String<br/><br/>[FAQ]...<br/>---<br/>[TICKET]...<br/>---<br/>[GUIDE]..."]

        FORMAT --> CONTEXT

    end

    MERGE --> FORMAT

    %% Prompt
    subgraph Prompt["Prompt Creation"]

        SYS["System Prompt"]

        HUMAN["User Question"]

        FINALPROMPT["Final Prompt<br/><br/>System Prompt<br/>+<br/>Context<br/>+<br/>User Question"]

        SYS --> FINALPROMPT
        CONTEXT --> FINALPROMPT
        HUMAN --> FINALPROMPT

    end

    U -.-> HUMAN

    %% LLM
    subgraph LLM["Qwen3-32B (Groq)"]

        MODEL["Qwen3-32B"]

        REASON["Reads all 9 documents<br/>Reasons over them<br/>Synthesizes one answer"]

        MODEL --> REASON

    end

    FINALPROMPT --> MODEL

    %% Response
    ANSWER["Final Answer<br/><br/>Restart modem<br/>Check cables<br/>Inspect splitter<br/>Contact support if needed"]

    REASON --> ANSWER
```