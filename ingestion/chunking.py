from typing import List
import re

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 100

class Chunker:
    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> List[str]:
        paragraphs = [para.strip() for para in re.split(r"\n{2,}", text) if para.strip()]
        chunks = []
        current = []
        current_len = 0

        for paragraph in paragraphs:
            paragraph_len = len(paragraph)
            if current_len + paragraph_len > chunk_size and current:
                chunks.append("\n\n".join(current).strip())
                overlap_text = "\n\n".join(current)[-overlap:]
                current = [overlap_text] if overlap_text else []
                current_len = len(overlap_text)

            current.append(paragraph)
            current_len += paragraph_len + 2

        if current:
            chunks.append("\n\n".join(current).strip())

        return [chunk for chunk in chunks if chunk]
