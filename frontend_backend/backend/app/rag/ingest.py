import argparse
from app.core.config import core_settings
from app.services.rag.loader import DocumentLoader
from app.services.rag.chunker import TextChunker
from app.services.rag.embedder import EmbeddingService
from app.services.rag.qdrant import QdrantService

def main():
    parser = argparse.ArgumentParser(description="Ingest RAG documents into Qdrant")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Max characters per chunk")
    parser.add_argument("--overlap", type=int, default=200, help="Character overlap between chunks")
    args = parser.parse_args()

    print(f"Starting RAG ingestion pipeline...")
    print(f"Knowledge Directory: {core_settings.KNOWLEDGE_DIR}")
    print(f"Chunk Size: {args.chunk_size}, Overlap: {args.overlap}")

    # 1. Load
    loader = DocumentLoader(core_settings.KNOWLEDGE_DIR)
    raw_docs = loader.load_documents()
    print(f"Loaded {len(raw_docs)} raw document pages/sections.")

    if not raw_docs:
        print("No documents found to ingest.")
        return

    # 2. Chunk
    chunker = TextChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    chunks = chunker.chunk_documents(raw_docs)
    print(f"Created {len(chunks)} text chunks.")

    # 3. Embed
    print("Generating embeddings (this may take a moment)...")
    embedder = EmbeddingService()
    embedded_chunks = embedder.embed_chunks(chunks)

    # 4. Store
    print("Connecting to Qdrant...")
    qdrant = QdrantService()
    inserted_count = qdrant.ingest_chunks(embedded_chunks)
    
    print(f"Successfully ingested {inserted_count} NEW chunks into Qdrant.")
    if inserted_count < len(embedded_chunks):
        print(f"Skipped {len(embedded_chunks) - inserted_count} chunks that were already present.")

if __name__ == "__main__":
    main()
