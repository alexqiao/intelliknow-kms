import json
import time
from typing import List, Dict, Tuple
from app.database import Intent, QueryLog, Document, DocumentChunk, DocumentIntent

class QueryOrchestrator:
    def __init__(self, llm_service, vector_store, db_session):
        self.llm = llm_service
        self.vector_store = vector_store
        self.db = db_session
        self.confidence_threshold = 0.70

    async def process_query(self, query: str, source: str, user_id: str) -> Dict:
        start_time = time.time()

        intent, confidence = await self._classify_intent(query)
        if confidence < self.confidence_threshold:
            intent = "General"

        chunks = await self._retrieve_chunks(query, intent, top_k=5)
        response = await self._generate_response(query, chunks)

        response_time = int((time.time() - start_time) * 1000)
        self._log_query(query, source, user_id, intent, confidence, response, response_time)

        return {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "response_time_ms": response_time
        }

    async def _classify_intent(self, query: str) -> Tuple[str, float]:
        intents = self.db.query(Intent).all()
        intent_list = "\n".join([f"- {i.name}: {i.description} (keywords: {i.keywords})" for i in intents])

        prompt = f"""Classify the following user query into one of these intent categories:

{intent_list}

User query: "{query}"

Respond in JSON format:
{{"intent": "category_name", "confidence": 0.85}}"""

        response = await self.llm.chat_completion([{"role": "user", "content": prompt}])

        try:
            cleaned = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            return result["intent"], result["confidence"]
        except Exception as e:
            print(f"JSON Parsing Error: {e} - Raw Output: {response}")
            return "General", 0.5

    async def _retrieve_chunks(self, query: str, intent: str, top_k: int) -> List[Dict]:
        query_embedding = await self.llm.generate_embeddings([query])
        results = self.vector_store.search(query_embedding[0], 20, intent)

        # Get intent_id for filtering
        intent_obj = self.db.query(Intent).filter(Intent.name == intent).first()

        enriched = []
        accessed_docs = set()
        for r in results:
            chunk = self.db.query(DocumentChunk).filter(DocumentChunk.faiss_id == r["faiss_id"]).first()
            if chunk:
                doc = self.db.query(Document).filter(Document.id == chunk.document_id).first()

                # Filter by intent
                if intent == "General" or not intent_obj:
                    enriched.append({
                        "content": r["content"],
                        "doc_name": doc.filename if doc else "Unknown"
                    })
                    if doc and doc.id not in accessed_docs:
                        doc.access_count += 1
                        accessed_docs.add(doc.id)
                else:
                    doc_intent = self.db.query(DocumentIntent).filter(
                        DocumentIntent.document_id == chunk.document_id,
                        DocumentIntent.intent_id == intent_obj.id
                    ).first()
                    if doc_intent:
                        enriched.append({
                            "content": r["content"],
                            "doc_name": doc.filename if doc else "Unknown"
                        })
                        if doc and doc.id not in accessed_docs:
                            doc.access_count += 1
                            accessed_docs.add(doc.id)

                if len(enriched) >= top_k:
                    break

        self.db.commit()

        # Fallback mechanism
        if not enriched and intent != "General":
            print(f"⚠️ Intent '{intent}' returned no results. Falling back to General search.")
            return await self._retrieve_chunks(query, "General", top_k)

        return enriched[:top_k]

    async def _generate_response(self, query: str, chunks: List[Dict]) -> str:
        if not chunks:
            return "知识库中没有相关信息。"

        context = "\n\n".join([f"[来源: {c['doc_name']}]\n{c['content']}" for c in chunks])

        prompt = f"""基于以下知识库内容回答用户问题。如果内容中没有相关信息，请说"知识库中没有相关信息"。

知识库内容：
{context}

用户问题：{query}

请提供简洁准确的回答，并标注信息来源。"""

        return await self.llm.chat_completion([{"role": "user", "content": prompt}])

    def _log_query(self, query: str, source: str, user_id: str, intent: str, confidence: float, response: str, response_time: int):
        log = QueryLog(
            query_text=query,
            frontend_source=source,
            user_id=user_id,
            classified_intent=intent,
            confidence_score=confidence,
            response_text=response,
            response_time_ms=response_time
        )
        self.db.add(log)
        self.db.commit()
