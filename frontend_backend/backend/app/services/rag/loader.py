import os
import glob
import fitz  # PyMuPDF
from typing import List, Dict, Any

class DocumentLoader:
    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Loads all PDF and TXT files from the knowledge directory recursively.
        Returns a list of raw pages/documents with initial metadata.
        """
        docs = []
        search_pattern = os.path.join(self.knowledge_dir, "**", "*")
        for filepath in glob.glob(search_pattern, recursive=True):
            if not os.path.isfile(filepath):
                continue
                
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".pdf":
                docs.extend(self._load_pdf(filepath))
            elif ext == ".txt":
                docs.extend(self._load_txt(filepath))
                
        return docs

    def _load_pdf(self, filepath: str) -> List[Dict[str, Any]]:
        docs = []
        filename = os.path.basename(filepath)
        category = os.path.basename(os.path.dirname(filepath))
        
        try:
            doc = fitz.open(filepath)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()
                if not text:
                    continue
                
                docs.append({
                    "text": text,
                    "title": filename,
                    "source": filepath,
                    "document_type": category,
                    "page_number": page_num + 1
                })
        except Exception as e:
            print(f"Error loading PDF {filepath}: {e}")
            
        return docs

    def _load_txt(self, filepath: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(filepath)
        category = os.path.basename(os.path.dirname(filepath))
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()
                
            if text:
                return [{
                    "text": text,
                    "title": filename,
                    "source": filepath,
                    "document_type": category,
                    "page_number": None
                }]
        except Exception as e:
            print(f"Error loading TXT {filepath}: {e}")
            
        return []
