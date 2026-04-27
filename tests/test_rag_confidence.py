from src.retriever import Retriever
from src.rag import RAGAgent


def test_confidence_higher_with_relevant_context():
    # Relevant document contains the query terms
    docs_relevant = [
        {'id': 'r1', 'path': 'rel.md', 'text': 'This document describes the testing approach and test design.'}
    ]
    r_rel = Retriever()
    r_rel.build_index(docs_relevant)
    agent_rel = RAGAgent(r_rel)
    ans_rel = agent_rel.answer('testing approach')
    assert isinstance(ans_rel, dict)
    conf_rel = float(ans_rel.get('confidence', 0.0))

    # Unrelated document lacks the query terms
    docs_unrelated = [
        {'id': 'u1', 'path': 'unrel.md', 'text': 'Completely different subject about gardening and plants.'}
    ]
    r_un = Retriever()
    r_un.build_index(docs_unrelated)
    agent_un = RAGAgent(r_un)
    ans_un = agent_un.answer('testing approach')
    assert isinstance(ans_un, dict)
    conf_un = float(ans_un.get('confidence', 0.0))

    assert conf_rel >= conf_un
