Param(
    [string]$ProjectDir = $PSScriptRoot
)

Push-Location $ProjectDir

Write-Host "[1/3] Running main.py (schedule demo, RAG disabled by default)"
python main.py

Write-Host "`n[2/3] Running main.py --rag (RAG demo; will use simulated LLM if OPENAI_API_KEY is not set)"
python main.py --rag

Write-Host "`n[2.5/3] Running main.py --agent (observable multi-step agent demo)"
python main.py --agent

Write-Host "`n[3/3] Running pytest for RAG confidence test"
python -m pytest tests/test_rag_confidence.py -q

Write-Host "`nDemo run complete. To run a live-API RAG demo set the environment variable and re-run:" -ForegroundColor Cyan
Write-Host '  $env:OPENAI_API_KEY = "<YOUR_KEY>"; python main.py --rag' -ForegroundColor Cyan

Pop-Location
