"""PolicyStore THẬT — chromadb + OpenAI embeddings. 🔴 cần API key + mạng.

docs/rag-design.md. Import nặng trong __init__ để module import được khi offline.
Production: thêm hybrid + rerank + lọc ngày hiệu lực (ngoài phạm vi lát cắt).
"""

from __future__ import annotations

from ..schemas import PolicyCitation


class ChromaStore:
    def __init__(self, docs: list[dict], settings):
        import chromadb
        from langchain_openai import OpenAIEmbeddings

        self._embed = OpenAIEmbeddings(
            model=settings.embedding_model, api_key=settings.openai_api_key
        )
        client = chromadb.Client()
        self._col = client.get_or_create_collection("policies")
        if docs:
            self._col.add(
                ids=[str(i) for i in range(len(docs))],
                documents=[d["snippet"] for d in docs],
                embeddings=self._embed.embed_documents([d["snippet"] for d in docs]),
                metadatas=[
                    {"source": d["source"], "dieu": d.get("dieu") or ""} for d in docs
                ],
            )

    def retrieve(self, query: str, k: int = 3) -> list[PolicyCitation]:
        res = self._col.query(
            query_embeddings=[self._embed.embed_query(query)], n_results=k
        )
        out: list[PolicyCitation] = []
        for snippet, meta in zip(res["documents"][0], res["metadatas"][0]):
            out.append(
                PolicyCitation(
                    source=meta.get("source", ""),
                    snippet=snippet,
                    dieu=meta.get("dieu") or None,
                )
            )
        return out
