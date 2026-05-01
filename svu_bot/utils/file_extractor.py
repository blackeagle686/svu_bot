"""Utility: extract text from common uploaded file types.

This helper tries a best-effort extraction for PDFs, DOCX, text, HTML, and Excel.
It returns a truncated excerpt (safe default) so the bot can analyze content immediately
without waiting for external RAG indexing.
"""
import os

def extract_text(file_path: str, max_chars: int = 3000) -> str:
    """Extract a text excerpt from `file_path`. Returns empty string on unknown types.

    Args:
        file_path: absolute path to the uploaded file
        max_chars: maximum number of characters to return (truncated with marker)
    """
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            try:
                from pypdf import PdfReader
            except Exception:
                return ""
            reader = PdfReader(file_path)
            parts = []
            for p in reader.pages:
                t = p.extract_text() or ""
                if t:
                    parts.append(t)
                if sum(len(s) for s in parts) >= max_chars:
                    break
            full = "\n".join(parts)
            return (full[:max_chars] + "... (truncated)") if len(full) > max_chars else full

        if ext == ".docx":
            try:
                from docx import Document
            except Exception:
                return ""
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            full = "\n".join(paragraphs)
            return (full[:max_chars] + "... (truncated)") if len(full) > max_chars else full

        if ext in (".txt", ".md", ".csv"):
            with open(file_path, "r", errors="ignore") as f:
                full = f.read()
            return (full[:max_chars] + "... (truncated)") if len(full) > max_chars else full

        if ext in (".html", ".htm"):
            try:
                from bs4 import BeautifulSoup
            except Exception:
                return ""
            with open(file_path, "r", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
            full = soup.get_text(separator="\n")
            return (full[:max_chars] + "... (truncated)") if len(full) > max_chars else full

        if ext in (".xlsx", ".xls"):
            try:
                import pandas as pd
            except Exception:
                return ""
            # Read a small portion to avoid heavy memory use
            df = pd.read_excel(file_path, engine="openpyxl")
            full = df.head(20).to_csv(index=False)
            return (full[:max_chars] + "... (truncated)") if len(full) > max_chars else full

    except Exception as e:
        return f"[Unable to extract file text: {e}]"

    return ""
