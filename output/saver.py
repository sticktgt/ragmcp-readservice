from datetime import datetime
import os
import json
from langchain_core.documents import Document

def save_metadata_entry(doc: Document, index: int, path: str):
    data = {
        "id": index,
        "timestamp": datetime.utcnow().isoformat() + "Z",  # ISO 8601 UTC timestamp
        "process_id": os.getpid(),                        # Current process ID        
        "source_connector": doc.metadata.get("source_connector"),
        "source": doc.metadata.get("source"),
        "source_hash": doc.metadata.get("source_hash"),
        "original_name": doc.metadata.get("original_name"),
        "created_at": doc.metadata.get("created_at"),
        "size_bytes": doc.metadata.get("size_bytes"),
        # additional metadata can be added here
        # "metadata": doc.metadata,
        "size": len(doc.page_content) if isinstance(doc.page_content, str) else len(doc.page_content.encode("utf-8"))
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def save_doc_text(doc: Document, index: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"document_{index:04}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(doc.page_content)
