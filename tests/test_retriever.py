from src.retriever import Retriever


def test_retriever_basic():
    docs = [
        {'id': 'd1', 'path': 'p1', 'text': 'This document is about scheduling and tests.'},
        {'id': 'd2', 'path': 'p2', 'text': 'Another file about recipes and cooking.'},
    ]
    r = Retriever()
    r.build_index(docs)
    hits = r.retrieve('scheduling', k=1)
    assert hits, 'Expected at least one hit'
    top_doc, score = hits[0]
    assert top_doc['id'] == 'd1'
    assert score >= 0
