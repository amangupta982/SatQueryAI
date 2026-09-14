"""
Document text extraction and chunking pipeline for remote sensing knowledge.
Supports Markdown (.md), Plain Text (.txt), and PDF (.pdf).
"""

import os
import re
import uuid
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeChunk:
    """Represents an isolated chunk with provenance metadata."""
    def __init__(
        self,
        text: str,
        source: str,
        document: str,
        section: str = "General",
        category: str = "general",
        chunk_id: Optional[str] = None,
        page: Optional[int] = None,
        char_length: int = 0
    ):
        self.text = text.strip()
        self.source = source
        self.document = document
        self.section = section
        self.category = category
        self.chunk_id = chunk_id or str(uuid.uuid4())
        self.page = page
        self.char_length = len(self.text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "document": self.document,
            "section": self.section,
            "category": self.category,
            "chunk_id": self.chunk_id,
            "page": self.page,
            "char_length": self.char_length,
        }


def extract_text_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract raw text blocks with page/section context from a file.
    Returns list of dicts: [{"text": str, "page": Optional[int], "section": str}]
    """
    ext = os.path.splitext(file_path)[1].lower()
    sections = []

    if ext in [".md", ".txt"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            # Split by Markdown headings (e.g., # or ## or ###)
            pattern = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)
            parts = pattern.split(content)
            
            if len(parts) <= 1:
                # No headings found, treat whole text as single section
                sections.append({"text": content.strip(), "page": 1, "section": "General"})
            else:
                current_heading = "Introduction"
                for part in parts:
                    part_stripped = part.strip()
                    if not part_stripped:
                        continue
                    if part_stripped.startswith("#"):
                        current_heading = re.sub(r"^#+\s*", "", part_stripped).strip()
                    else:
                        sections.append({
                            "text": part_stripped,
                            "page": 1,
                            "section": current_heading
                        })
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")

    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    sections.append({
                        "text": page_text.strip(),
                        "page": page_num,
                        "section": f"Page {page_num}"
                    })
        except ImportError:
            # Fallback if pypdf is not installed: try simple binary search for stream text
            logger.warning(f"pypdf not installed. Reading PDF {file_path} text fallback.")
            try:
                with open(file_path, "rb") as f:
                    raw = f.read().decode("latin1", errors="ignore")
                matches = re.findall(r"\((.*?)\)", raw)
                clean_text = " ".join([m for m in matches if len(m) > 3])
                if clean_text:
                    sections.append({"text": clean_text, "page": 1, "section": "PDF Fallback"})
            except Exception as e:
                logger.error(f"Failed to extract PDF fallback for {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")

    return sections


def chunk_text(
    text: str,
    max_chars: int = 750,
    overlap_chars: int = 150
) -> List[str]:
    """
    Split text into overlapping chunks respecting paragraph and sentence boundaries.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []

    chunks = []
    # Split primarily on paragraphs
    paragraphs = text.split("\n\n")
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If single paragraph exceeds max_chars, break into sentence units
        if len(para) > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if current_length + len(sent) > max_chars and current_chunk:
                    chunk_str = " ".join(current_chunk)
                    chunks.append(chunk_str)
                    # Keep overlap from the end
                    overlap_accum = []
                    overlap_len = 0
                    for prev_sent in reversed(current_chunk):
                        if overlap_len + len(prev_sent) < overlap_chars:
                            overlap_accum.insert(0, prev_sent)
                            overlap_len += len(prev_sent)
                        else:
                            break
                    current_chunk = overlap_accum + [sent]
                    current_length = sum(len(s) for s in current_chunk) + len(current_chunk)
                else:
                    current_chunk.append(sent)
                    current_length += len(sent)
        else:
            if current_length + len(para) > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [para]
                current_length = len(para)
            else:
                current_chunk.append(para)
                current_length += len(para)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_document(
    file_path: str,
    category: str,
    max_chars: int = 750,
    overlap_chars: int = 150
) -> List[KnowledgeChunk]:
    """
    Extract and chunk a single document into KnowledgeChunk objects.
    """
    doc_name = os.path.basename(file_path)
    sections = extract_text_from_file(file_path)
    all_chunks = []

    for sec in sections:
        raw_text = sec.get("text", "")
        section_name = sec.get("section", "General")
        page_num = sec.get("page", 1)

        text_pieces = chunk_text(raw_text, max_chars=max_chars, overlap_chars=overlap_chars)
        for idx, piece in enumerate(text_pieces):
            if len(piece.strip()) < 40:
                continue  # ignore trivial fragments
            chunk = KnowledgeChunk(
                text=piece,
                source=f"{category}/{doc_name}",
                document=doc_name,
                section=section_name,
                category=category,
                page=page_num,
                chunk_id=f"{doc_name}_{page_num}_{idx}_{uuid.uuid4().hex[:6]}"
            )
            all_chunks.append(chunk)

    return all_chunks
