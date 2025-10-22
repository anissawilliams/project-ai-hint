from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

class RAGRetriever:
    def __init__(self, index_path, chunks_path, model_name='all-MiniLM-L6-v2'):
        self.index = faiss.read_index(index_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
        self.model = SentenceTransformer(model_name)

    def retrieve(self, query, top_k=5, filter_tag=None):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), top_k)
        results = []
        for i in indices[0]:
            chunk = self.chunks[i]
            if filter_tag and filter_tag not in chunk.get("tags", []):
                continue
            results.append(chunk)
        return results

def build_rag_tool(index_path, chunks_path):
    retriever = RAGRetriever(index_path, chunks_path)

    def rag_search(query: str) -> str:
        results = retriever.retrieve(query)
        if not results:
            return "No relevant content found in the RAG store."

        response = "📚 Retrieved content:\n\n"
        for i, chunk in enumerate(results):
            response += f"{i+1}. {chunk['text']}\n"
            response += f"   🔗 Source: {chunk.get('source_url', 'N/A')}\n"
            if chunk.get("tags"):
                response += f"   🏷️ Tags: {', '.join(chunk['tags'])}\n"
            response += "\n"
        return response

    return rag_search
