import asyncio
from app.database import get_db, Document, DocumentChunk
from app.dependencies import llm_service_instance, vector_store_instance

async def rebuild_faiss():
    vs = vector_store_instance

    # Clear FAISS index
    vs.metadata = []
    vs.save()

    db = next(get_db())

    # Get all documents
    docs = db.query(Document).all()
    print(f"Found {len(docs)} documents")

    for doc in docs:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).all()
        if not chunks:
            continue

        print(f"Processing {doc.filename}: {len(chunks)} chunks")

        # Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = await llm_service_instance.generate_embeddings(texts)

        # Add to FAISS
        faiss_ids = vs.add_vectors(embeddings, texts, doc.id)

        # Update chunks with new faiss_ids
        for chunk, faiss_id in zip(chunks, faiss_ids):
            chunk.faiss_id = faiss_id

        db.commit()
        print(f"  Updated {len(chunks)} chunks")

    print("FAISS index rebuilt successfully")

if __name__ == "__main__":
    asyncio.run(rebuild_faiss())
