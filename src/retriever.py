from typing import List, Tuple, Dict
import os

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False


class Retriever:
    """Simple Retriever that builds an index over local documents and returns top-k passages.

    - Uses sklearn TF-IDF if available; otherwise falls back to substring scoring.
    - Exposes `build_index(doc_texts)` and `retrieve(query, k=3)`.
    """

    def __init__(self):
        self.docs: List[Dict] = []
        self.tfidf = None
        self.vector_matrix = None
        self.vectorizer = None

    def build_index(self, docs: List[Dict]):
        """Build index from list of docs, where each doc is {'id':..., 'text': ...}
        Keeps docs in memory for retrieval.
        """
        self.docs = docs
        texts = [d.get('text', '') for d in docs]
        if _SKLEARN_AVAILABLE and texts:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            try:
                self.vector_matrix = self.vectorizer.fit_transform(texts)
            except Exception:
                # fallback to None
                self.vector_matrix = None
        else:
            self.vectorizer = None
            self.vector_matrix = None

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[Dict, float]]:
        """Return top-k (doc, score) tuples for the query."""
        if not self.docs:
            return []

        if self.vector_matrix is not None:
            # use cosine similarity via linear_kernel (fast)
            q_vec = self.vectorizer.transform([query])
            try:
                cosine_similarities = linear_kernel(q_vec, self.vector_matrix).flatten()
                ranked_idx = cosine_similarities.argsort()[::-1]
                results = []
                for i in ranked_idx[:k]:
                    results.append((self.docs[i], float(cosine_similarities[i])))
                return results
            except Exception:
                pass

        # Fallback: simple substring count scoring
        scores = []
        q_lower = query.lower()
        for d in self.docs:
            text = d.get('text', '').lower()
            score = 0
            if q_lower in text:
                score += 1.0
            # partial matches by counting words
            for w in q_lower.split():
                if w and w in text:
                    score += 0.1
            scores.append(score)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in ranked[:k]:
            results.append((self.docs[idx], float(score)))
        return results


def load_local_docs(root_paths: List[str]) -> List[Dict]:
    """Load a few local text files to use as documents for the retriever.

    - root_paths: list of file paths or directories. If a directory, reads README.md and any .md files in top level.
    - returns list of {'id', 'path', 'text'}
    """
    docs = []
    seen = 0
    for p in root_paths:
        if os.path.isdir(p):
            # prefer README.md, then other md files
            readme = os.path.join(p, 'README.md')
            if os.path.exists(readme):
                try:
                    with open(readme, encoding='utf-8') as fh:
                        text = fh.read()
                    docs.append({'id': f'doc-{seen}', 'path': readme, 'text': text})
                    seen += 1
                except Exception:
                    pass
            # collect other md files
            for fname in os.listdir(p):
                if fname.lower().endswith('.md') and fname != 'README.md':
                    fp = os.path.join(p, fname)
                    try:
                        with open(fp, encoding='utf-8') as fh:
                            text = fh.read()
                        docs.append({'id': f'doc-{seen}', 'path': fp, 'text': text})
                        seen += 1
                    except Exception:
                        pass
        elif os.path.isfile(p):
            try:
                with open(p, encoding='utf-8') as fh:
                    text = fh.read()
                docs.append({'id': f'doc-{seen}', 'path': p, 'text': text})
                seen += 1
            except Exception:
                pass
    return docs
