import os
import logging
from typing import Dict


OPENAI_ENV = 'OPENAI_API_KEY'
_logger = logging.getLogger(__name__)


def generate(prompt: str, max_tokens: int = 256) -> Dict:
    """Generate text from an LLM if API key available, otherwise return a safe fallback.

    Returns a dict: {'text': str, 'confidence': float} where confidence in [0,1].
    - If OpenAI is available and call succeeds, returns LLM text and moderate confidence.
    - On fallback or errors returns a deterministic simulated text and lower confidence.
    """
    api_key = os.environ.get(OPENAI_ENV)
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            resp = openai.Completion.create(
                engine='text-davinci-003',
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.2,
                n=1,
            )
            text = resp.choices[0].text.strip()
            # Best-effort confidence: use a conservative default for network LLMs
            conf = 0.7
            _logger.info('LLM generate successful (external API)')
            return {'text': text, 'confidence': conf}
        except Exception as e:
            _logger.exception('LLM call failed, falling back to simulated output: %s', e)

    # Fallback simulated answer — concise and deterministic
    snippet = prompt.replace('\n', ' ')[:400]
    text = f"SIMULATED LLM OUTPUT: {snippet}"
    conf = 0.3
    _logger.info('Using simulated LLM output (no API key or failure)')
    return {'text': text, 'confidence': conf}
