import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import webhooks, documents, intents, query, config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
app = FastAPI(title="IntelliKnow KMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router, tags=["webhooks"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(intents.router, prefix="/api", tags=["intents"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(config.router, prefix="/api", tags=["config"])

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"status": "ok", "service": "IntelliKnow KMS"}

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "healthy"}
