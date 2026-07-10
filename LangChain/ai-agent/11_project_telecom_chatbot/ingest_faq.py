"""
Ingest data/faq.csv into 'faq chroma collection
Run once (or whenever the csv changes): python ingest_faq.py
"""

import os
os.environ["TRANSFORMER_VERBOSITY"] = "error"
import pandas as pd
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


CHROMA_DIR = "chroma_store"
COLLECTION = "faq"
CSV_PATH = os.path.join("data", "faq.csv")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-V2"


def load_faq_documents(csv_path: str) -> list[Document]:
    df = pd.read_csv(csv_path)
    docs = []
    for _, row in df.iterrows():
        content = f"Q: {row['question']}\nA: {row['answer']}"
        docs.append(Document(
            page_content=content,
            metadata={"source": "faq", "category": row["category"], "faq_id": str(row["id"])},
        ))
    return docs


def main():
    print("Loading FAQ documents...")
    docs = load_faq_documents(CSV_PATH)
    print(f"    {len(docs)} FAQ entries loaded.")

    print("Initializing embedding model")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print(f"Embedding and store in CHroma Collection: '{COLLECTION}'...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR
    )
    print(f"    Done. {vectorstore._collection.count()} vector stored.")


if __name__== "__main__":
    main()