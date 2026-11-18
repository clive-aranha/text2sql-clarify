from openai import OpenAI

from t2s.config import settings

client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
resp = client.chat.completions.create(
    model=settings.llm_model,
    messages=[{"role": "user", "content": "Reply with exactly: LLM connection works"}],
    temperature=0,
)
print(resp.choices[0].message.content)
