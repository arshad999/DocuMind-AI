from pathlib import Path
from typing import Any
import re

from docx import Document as DocxDocument
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

class DocumentLoader:
    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        document = DocxDocument(file_path)
        text_segments = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text_segments.append(paragraph.text.strip())
        return "\n".join(text_segments)

    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())
        return "\n".join(pages)

    @classmethod
    def load_document(cls, file_path: Path) -> dict[str, Any]:
        extension = file_path.suffix.lower()
        if extension == ".docx":
            raw_text = cls.extract_text_from_docx(file_path)
        elif extension == ".pdf":
            raw_text = cls.extract_text_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported extension: {extension}")

        headings = cls._extract_headings(raw_text)
        sanitized_text = cls._normalize_text(raw_text)
        return {
            "filename": file_path.name,
            "extension": extension,
            "raw_text": sanitized_text,
            "headings": headings,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\t", " ")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _extract_headings(text: str) -> list[str]:
        headings = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.isupper() and len(stripped.split()) <= 8:
                headings.append(stripped)
            elif re.match(r"^(?:[0-9]+\.|[A-Z]\.|\-\s).+", stripped):
                headings.append(stripped)
        return headings
