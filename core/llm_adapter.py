import os
from typing import Optional

class LLMAdapter:
    """Optional LLM adapter providing fallback to local pipeline if API keys are absent."""

    def __init__(self, grok_api_key: Optional[str] = None, huggingface_api_key: Optional[str] = None):
        self.grok_api_key = grok_api_key or os.environ.get('GROK_API_KEY') or os.environ.get('OPENAI_API_KEY')
        self.huggingface_api_key = huggingface_api_key or os.environ.get('HUGGINGFACE_API_KEY')
        self.is_available = bool(self.grok_api_key)

    def generate_answer(self, prompt: str, context: str) -> Optional[str]:
        """Generate answer using external LLM if available; otherwise return None for local processing."""
        if not self.is_available:
            return None

        try:
            # xAI Grok uses the OpenAI-compatible API client
            import openai
            client = openai.OpenAI(
                api_key=self.grok_api_key,
                base_url="https://api.x.ai/v1"
            )
            response = client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {"role": "system", "content": "You are IntelliQA, an intelligent assistant. Answer concisely using provided context."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM API Call failed, falling back to local IR engine: {e}")
            return None
