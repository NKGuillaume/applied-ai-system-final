from typing import List, Dict
import logging
from .llm import generate
from .tools import Calculator

_logger = logging.getLogger(__name__)


class MultiStepAgent:
    """A simple observable multi-step agent that plans, retrieves, analyzes, and finalizes.

    The agent returns the final answer plus a list of intermediate steps for visibility.
    """

    def __init__(self, retriever, k: int = 3):
        self.retriever = retriever
        self.k = k

    def _plan(self, query: str) -> List[str]:
        # Very small planner that creates a handful of human-readable steps
        return [
            "retrieve: fetch top-k relevant documents",
            "analyze: compute simple stats over retrieved docs",
            "finalize: synthesize an answer using the LLM",
        ]

    def run(self, query: str) -> Dict:
        steps = []
        try:
            plan = self._plan(query)
            steps.append({"step": "plan", "detail": plan})

            # Retrieve
            hits = self.retriever.retrieve(query, k=self.k)
            retrieved = []
            scores = []
            for doc, score in hits:
                retrieved.append({"id": doc.get("id"), "path": doc.get("path"), "snippet": doc.get("text", "")[:300]})
                scores.append(float(score))
            steps.append({"step": "retrieve", "detail": retrieved})

            # Analyze / compute simple stats
            total_chars = sum(len(d.get('snippet','')) for d in retrieved)
            avg_score = float(max(scores)) if scores else 0.0
            analysis = {"total_chars": total_chars, "avg_top_score": avg_score, "num_docs": len(retrieved)}
            steps.append({"step": "analyze", "detail": analysis})

            # Tool-call example: use Calculator to compute a small derived metric
            try:
                calc = Calculator()
                expr = f"{analysis['total_chars']} + {analysis['num_docs']}"
                tool_result = calc.compute(expr)
                steps.append({"step": "tool_call", "detail": {"tool": "Calculator", "expr": expr, "result": tool_result}})
            except Exception as e:
                steps.append({"step": "tool_call", "detail": {"tool": "Calculator", "error": str(e)}})

            # Build prompt that includes an explicit 'chain-of-thought' request to make the LLM verbose (if available)
            parts = [
                "You are an assistant. Follow the plan and show brief intermediate reasoning when helpful.",
            ]
            for i, r in enumerate(retrieved):
                parts.append(f"[Context {i+1} — {r.get('path')}]:\n" + r.get('snippet', ''))
            parts.append("---\nQuery:\n" + query)
            parts.append("\nPlease provide a concise answer and, before the final answer, a short bulleted list of intermediate observations.")
            prompt = "\n\n".join(parts)

            llm_resp = generate(prompt)
            text = llm_resp.get('text') if isinstance(llm_resp, dict) else str(llm_resp)
            llm_conf = float(llm_resp.get('confidence', 0.0)) if isinstance(llm_resp, dict) else 0.0

            steps.append({"step": "llm", "detail": {"text_preview": text[:400], "llm_confidence": llm_conf}})

            # Simple confidence fusion similar to RAG
            context_conf = 0.0
            if scores:
                try:
                    context_conf = max(0.0, min(1.0, float(max(scores))))
                except Exception:
                    context_conf = 0.0
            final_conf = 0.5 * context_conf + 0.5 * llm_conf
            final_conf = max(0.0, min(1.0, final_conf))

            steps.append({"step": "finalize", "detail": {"final_confidence": final_conf}})

            _logger.info('MultiStepAgent completed (conf=%.3f) context_conf=%.3f llm_conf=%.3f hits=%d',
                         final_conf, context_conf, llm_conf, len(hits))
            return {"text": text, "confidence": final_conf, "steps": steps}
        except Exception as e:
            _logger.exception('MultiStepAgent.run failed: %s', e)
            return {"text": "Agent error: failed to produce answer", "confidence": 0.0, "steps": steps}
