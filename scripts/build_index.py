"""Bangun ulang vectorstore dari data/knowledge/*.txt."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from empath.config import settings

docs = DirectoryLoader(
    str(settings.rag_source_dir),
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
).load()

if not docs:
    raise SystemExit("Tidak ada .txt di data/knowledge")

chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120).split_documents(docs)
Chroma.from_documents(
    documents=chunks,
    embedding=GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
        output_dimensionality=settings.embedding_dim,
        task_type="RETRIEVAL_DOCUMENT",
    ),
    collection_name="psikologi",
    persist_directory=str(settings.rag_persist_dir),
)
print(f"OK — {len(chunks)} chunk dari {len(docs)} dokumen")