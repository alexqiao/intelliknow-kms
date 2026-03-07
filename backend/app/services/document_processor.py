import PyPDF2
import docx
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, llm_service, vector_store, db_session):
        self.llm = llm_service
        self.vector_store = vector_store
        self.db = db_session
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

    async def process_document(self, file_path: str, doc_id: int):
        text = self._extract_text(file_path)
        chunks = self.splitter.split_text(text)
        embeddings = await self.llm.generate_embeddings(chunks)
        faiss_ids = self.vector_store.add_vectors(embeddings, chunks, doc_id)

        from app.database import DocumentChunk, Document
        for idx, (chunk, faiss_id) in enumerate(zip(chunks, faiss_ids)):
            chunk_obj = DocumentChunk(
                document_id=doc_id,
                chunk_index=idx,
                content=chunk,
                faiss_id=faiss_id
            )
            self.db.add(chunk_obj)

        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        doc.processed = True
        doc.chunk_count = len(chunks)
        self.db.commit()

        return len(chunks)

    def _extract_text(self, file_path: str) -> str:
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([page.extract_text() for page in reader.pages])
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        return ""
