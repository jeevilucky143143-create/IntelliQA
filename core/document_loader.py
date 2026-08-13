import os
import pandas as pd
from typing import List, Dict, Tuple
from core.preprocessing import split_into_sentences, clean_text

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

class DocumentLoader:
    """Loads and manages unstructured documents and converts them to indexable passages."""

    def __init__(self, documents_dir: str):
        self.documents_dir = documents_dir

    def load_txt_file(self, filepath: str) -> str:
        """Read text from a plain text file with multiple encoding fallbacks."""
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""

    def load_pdf_file(self, filepath: str) -> str:
        """Extract plain text from PDF using pypdf."""
        if not PYPDF_AVAILABLE:
            raise ImportError("pypdf is required to process PDF files.")
        
        text_content = []
        try:
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
        except Exception as e:
            print(f"Error reading PDF {filepath}: {e}")
        return "\n".join(text_content)

    def load_csv_as_text(self, filepath: str) -> str:
        """Convert CSV rows into descriptive natural language sentences."""
        try:
            df = pd.read_csv(filepath)
            lines = []
            for _, row in df.iterrows():
                row_str = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                lines.append(row_str + ".")
            return "\n".join(lines)
        except Exception as e:
            print(f"Error converting CSV {filepath}: {e}")
            return ""

    def load_single_file(self, filepath: str) -> Tuple[str, str]:
        """Load text based on file extension. Returns (filename, text)."""
        filename = os.path.basename(filepath)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if ext == 'txt':
            content = self.load_txt_file(filepath)
        elif ext == 'pdf':
            content = self.load_pdf_file(filepath)
        elif ext == 'csv':
            content = self.load_csv_as_text(filepath)
        else:
            content = self.load_txt_file(filepath)
            
        return filename, clean_text(content)

    def load_all_documents(self) -> List[Dict]:
        """
        Scans self.documents_dir, loads all supported files, and segments them into passages.
        Each passage dict contains:
        - passage_id: unique int index
        - source: document filename
        - text: paragraph or sentence text
        """
        passages = []
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir, exist_ok=True)
            return passages

        passage_counter = 0
        for filename in sorted(os.listdir(self.documents_dir)):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(self.documents_dir, filename)
            if not os.path.isfile(filepath):
                continue

            fname, content = self.load_single_file(filepath)
            if not content:
                continue

            # Split content into sentences/passages
            sentences = split_into_sentences(content)
            for s in sentences:
                passages.append({
                    'passage_id': passage_counter,
                    'source': fname,
                    'text': s
                })
                passage_counter += 1

        return passages

    def get_document_summary(self) -> List[Dict]:
        """Returns metadata for all documents in documents_dir."""
        summary = []
        if not os.path.exists(self.documents_dir):
            return summary

        for filename in sorted(os.listdir(self.documents_dir)):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(self.documents_dir, filename)
            if not os.path.isfile(filepath):
                continue

            fname, content = self.load_single_file(filepath)
            sentences = split_into_sentences(content)
            summary.append({
                'filename': fname,
                'type': fname.rsplit('.', 1)[-1].upper() if '.' in fname else 'TXT',
                'size_kb': round(os.path.getsize(filepath) / 1024, 2),
                'passages_count': len(sentences),
                'status': 'Indexed'
            })
        return summary
