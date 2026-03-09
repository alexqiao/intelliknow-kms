import PyPDF2
import docx
import logging
import asyncio
import time
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from alibabacloud_docmind_api20220711.client import Client
from alibabacloud_tea_openapi.models import Config
from alibabacloud_docmind_api20220711.models import SubmitDocStructureJobAdvanceRequest, GetDocStructureResultRequest
from alibabacloud_tea_util.models import RuntimeOptions

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, llm_service, vector_store, db_session):
        self.llm = llm_service
        self.vector_store = vector_store
        self.db = db_session
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.aliyun_client = None

    def _init_aliyun_client(self):
        """Initialize Aliyun Document Mind client"""
        from app.config import get_settings
        settings = get_settings()

        if not settings.aliyun_access_key_id or not settings.aliyun_access_key_secret:
            return None

        config = Config(
            access_key_id=settings.aliyun_access_key_id,
            access_key_secret=settings.aliyun_access_key_secret,
            endpoint='docmind-api.cn-hangzhou.aliyuncs.com'
        )
        return Client(config)

    async def _extract_with_aliyun(self, file_path: str) -> str:
        """Extract document using Aliyun Document Mind API"""
        if not self.aliyun_client:
            self.aliyun_client = self._init_aliyun_client()
            if not self.aliyun_client:
                raise Exception("Aliyun client not configured")

        file_extension = file_path.split('.')[-1]
        runtime = RuntimeOptions()

        with open(file_path, 'rb') as f:
            submit_request = SubmitDocStructureJobAdvanceRequest(
                file_url_object=f,
                file_name_extension=file_extension
            )
            submit_response = self.aliyun_client.submit_doc_structure_job_advance(submit_request, runtime)

        if not submit_response.body.data:
            raise Exception(f"Aliyun API rejected the request: {submit_response.body.message}")

        job_id = submit_response.body.data.id

        start_time = time.time()
        # Increase timeout to 120s for large/complex PDFs
        while time.time() - start_time < 120:
            get_request = GetDocStructureResultRequest(id=job_id)
            result_response = self.aliyun_client.get_doc_structure_result(get_request)

            # The official way to check if task is done is the 'completed' boolean
            completed = getattr(result_response.body, 'completed', False)

            if completed:
                status = getattr(result_response.body, 'status', '')
                if status == "Success" or status == "success":
                    data = result_response.body.data

                    # Convert Aliyun model to a dictionary
                    if hasattr(data, 'to_map'):
                        data_dict = data.to_map()
                    elif isinstance(data, dict):
                        data_dict = data
                    else:
                        data_dict = {"raw": str(data)}

                    # Extract high-quality markdown content from layouts
                    if 'layouts' in data_dict:
                        md_text = ""
                        for layout in data_dict.get('layouts', []):
                            if 'markdownContent' in layout:
                                md_text += layout['markdownContent'] + "\n"
                            elif 'text' in layout:
                                md_text += layout['text'] + "\n"
                        if md_text:
                            return md_text

                    import json
                    return json.dumps(data_dict, ensure_ascii=False)

                else:
                    error_msg = getattr(result_response.body, 'message', 'Unknown Error')
                    raise Exception(f"Aliyun extraction task failed (Status: {status}): {error_msg}")

            await asyncio.sleep(2)

        raise Exception("Aliyun extraction timeout after 120 seconds")

    async def process_document(self, file_path: str, doc_id: int):
        from app.database import DocumentChunk

        # Clean up existing chunks if document is being reprocessed
        existing_chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
        if existing_chunks:
            for chunk in existing_chunks:
                self.db.delete(chunk)
            self.db.commit()
            # Rebuild FAISS index to remove old vectors
            self.vector_store.remove_document(doc_id)

        # Dual-pipeline: Try Aliyun Document Mind API first, fallback to local extraction
        try:
            logger.info(f"Attempting Aliyun Document Mind extraction for {file_path}")
            text = await self._extract_with_aliyun(file_path)
            logger.info("Aliyun extraction succeeded")
            # Log a preview of the extracted text (first 500 characters) to verify Markdown structure
            logger.info(f"Extracted text length: {len(text)} characters")
            preview_text = text[:500].replace('\n', ' \\n ')  # Escape newlines for cleaner single-line or block logging
            logger.info(f"Content Preview: {preview_text} ...")
        except Exception as e:
            logger.warning(f"Aliyun extraction failed: {e}. Falling back to local extraction")
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
