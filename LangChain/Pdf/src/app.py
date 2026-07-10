from src.data_loader import load_all_documents
from src.embedding import EmbeddingPipeline
from src.vectorstore import QdrantVectorStore
from src.search import RAGSearch


## Example Usage
if __name__ == "__main__":
    # docs = load_all_documents("data") # load only in the beginning untul you have the document
    store = QdrantVectorStore()  # connects to Qdrant (docker-compose "qdrant" service, or Qdrant Cloud via env vars)
    # store.build_from_documents(docs) # no need to run this everytime; until you have the document
    # chunks = EmbeddingPipeline().chunk_documents(docs)
    # chunkVectors = EmbeddingPipeline().embed_chunks(chunks=chunks)
    # print(chunkVectors)
    store.load()
    print(store.query("Who is Vaishali?", top_k=3))
   
    print()
    print()
   
    rag_search = RAGSearch()
    query = "Who is Vaishali?"
    summary = rag_search.search_and_summarize(query=query, top_k=3)
    print("Summary: ", summary)
