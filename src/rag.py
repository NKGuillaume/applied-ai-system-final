from typing import List, Dict
import logging
from .retriever import Retriever, load_local_docs
from .llm import generate


_logger = logging.getLogger(__name__)


class RAGAgent:
    """Very small RAG agent: given a query, retrieve top-k docs, build a prompt, and call the LLM wrapper.

    Usage:
        docs = load_local_docs([project_root, 'assets/system_diagram.mmd'])
        r = Retriever(); r.build_index(docs)
        agent = RAGAgent(r)
        answer = agent.answer('Summarize the testing approach')
    """

    def __init__(self, retriever: Retriever, k: int = 3):
        self.retriever = retriever
        self.k = k

    def build_prompt(self, query: str, contexts: List[Dict]) -> str:
        parts = ["Use the following context to answer the query. If the context doesn't contain the answer, answer concisely and say you don't know."]
        for i, c in enumerate(contexts):
            path = c.get('path', c.get('id', f'doc-{i}'))
            text = c.get('text', '')
            parts.append(f"[Context {i+1} — {path}]\n" + text[:1000])
        parts.append("---\nQuery:\n" + query)
        parts.append("\nAnswer:")
        return "\n\n".join(parts)

    def answer(self, query: str) -> str:
        try:
            hits = self.retriever.retrieve(query, k=self.k)
            contexts = [h[0] for h in hits]
            scores = [h[1] for h in hits]
            prompt = self.build_prompt(query, contexts)
            llm_resp = generate(prompt)

            # llm_resp is {'text':..., 'confidence':...}
            text = llm_resp.get('text') if isinstance(llm_resp, dict) else str(llm_resp)
            llm_conf = float(llm_resp.get('confidence', 0.0)) if isinstance(llm_resp, dict) else 0.0

            # Context coverage: use max score (cosine sim or fallback) normalized to [0,1]
            context_conf = 0.0
            if scores:
                try:
                    context_conf = max(0.0, min(1.0, float(max(scores))))
                except Exception:
                    context_conf = 0.0

            # Combine confidence signals (weighted)
            final_conf = 0.6 * context_conf + 0.4 * llm_conf
            final_conf = max(0.0, min(1.0, final_conf))

            _logger.info('RAG answer produced (conf=%.3f) context_conf=%.3f llm_conf=%.3f hits=%d',
                         final_conf, context_conf, llm_conf, len(hits))
            return {'text': text, 'confidence': final_conf}
        except Exception as e:
            _logger.exception('RAGAgent.answer failed: %s', e)
            return {'text': 'RAG error: failed to answer', 'confidence': 0.0}
