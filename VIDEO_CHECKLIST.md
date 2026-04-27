Video Walkthrough Checklist
--------------------------

Commands to run (copy into PowerShell in project root):

```powershell
# 1) Run the schedule demo
python main.py

# 2) RAG demo (simulated unless OPENAI_API_KEY set)
python main.py --rag

# 3) Observable multi-step agent demo (shows intermediate steps & tool call)
python main.py --agent

# 4) Run the confidence/evaluation test
python -m pytest tests/test_rag_confidence.py -q
```

Suggested short narration lines and timestamps (2–3 minute video):

- 00:00 — Introduce project: "This is PawPal+, a scheduling app for pet care."
- 00:10 — Show architecture diagram (`assets/system_diagram.mmd` rendered): "Major components: retriever, agent/RAG, LLM wrapper, tests."
- 00:20 — Run `python main.py` and narrate schedule outputs.
- 00:50 — Run `python main.py --rag` and narrate RAG behavior and printed confidences.
- 01:20 — Run `python main.py --agent` and highlight intermediate steps and the calculator tool call.
- 01:50 — Run `pytest tests/test_rag_confidence.py` to show the evaluator passing.

Recording tips:
- Use the `demo_run.ps1` script to capture all steps in order.
- If demonstrating live LLM, set `OPENAI_API_KEY` before running `--rag` to show difference in confidence.
