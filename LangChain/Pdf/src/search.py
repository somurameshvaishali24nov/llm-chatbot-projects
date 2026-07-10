import os
from dotenv import load_dotenv
from src.vectorstore import QdrantVectorStore
from langchain_groq import ChatGroq


load_dotenv()


class RAGSearch:
    def __init__(self, collection_name: str = "rag_documents", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "llama-3.1-8b-instant"):
        self.vectorstore = QdrantVectorStore(collection_name=collection_name, embedding_model=embedding_model)

        # Build the collection the first time (empty), otherwise just reuse what's in Qdrant
        if self.vectorstore.count() == 0:
            from src.data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()

        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            api_key=groq_api_key, model=llm_model, temperature=0.1, max_tokens=1024
        )
        print(f"[INFO] Groq LLM intitalized: {llm_model}")

        

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query_text=query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant document found"

        prompt = f"""
            Summarize the following context for the query: '{query}
                Context: {context}
                Answer:
        """
        response = self.llm.invoke([prompt])
        return response.content
