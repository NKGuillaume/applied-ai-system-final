from src.retriever import Retriever
from src.rag import RAGAgent


def test_rag_agent_simulated_answer():
    docs = [
        {'id': 'd1', 'path': 'p1', 'text': 'Testing docs content about scheduling and tests.'}
    ]
    r = Retriever()
    r.build_index(docs)
    agent = RAGAgent(r)
    ans = agent.answer('What is the testing approach?')
    assert ans is not None
    # New behavior: should return a dict with text and confidence
    assert isinstance(ans, dict)
    assert 'text' in ans and 'confidence' in ans
    assert isinstance(ans['confidence'], float)
    assert 0.0 <= ans['confidence'] <= 1.0
    assert isinstance(ans['text'], str)
    assert ans['text'].startswith('SIMULATED LLM OUTPUT')
