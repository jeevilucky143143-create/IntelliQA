import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.preprocessing import clean_text, tokenize

class IREngine:
    """Information Retrieval engine using TF-IDF and Cosine Similarity over document passages."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.passages: List[Dict] = []
        self.is_indexed: bool = False

    def build_index(self, passages: List[Dict]) -> bool:
        """Build TF-IDF vector index over a list of passages."""
        self.passages = passages
        if not passages:
            self.vectorizer = None
            self.tfidf_matrix = None
            self.is_indexed = False
            return False

        texts = [p['text'] for p in passages]
        # Use word and bigram TF-IDF features
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            self.is_indexed = True
            return True
        except Exception as e:
            print(f"Error building TF-IDF index: {e}")
            self.is_indexed = False
            return False

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search indexed passages for a given user query.
        Returns top_k passage matches sorted by cosine similarity score.
        """
        if not self.is_indexed or self.vectorizer is None or self.tfidf_matrix is None or not self.passages:
            return []

        cleaned_query = clean_text(query)
        if not cleaned_query:
            return []

        try:
            query_vec = self.vectorizer.transform([cleaned_query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            # Rank passages by similarity score
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.01:  # Filter completely non-matching passages
                    passage_info = self.passages[idx].copy()
                    passage_info['score'] = round(score, 4)
                    results.append(passage_info)
                    
            return results
        except Exception as e:
            print(f"Error executing IR search: {e}")
            return []

    def get_stats(self) -> Dict:
        """Returns statistical overview of the IR index."""
        return {
            'is_indexed': self.is_indexed,
            'total_passages': len(self.passages),
            'vocabulary_size': len(self.vectorizer.vocabulary_) if self.vectorizer and hasattr(self.vectorizer, 'vocabulary_') else 0
        }
