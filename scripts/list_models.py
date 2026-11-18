from openai import OpenAI

from t2s.config import settings

client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
for m in sorted(client.models.list().data, key=lambda m: m.id):
    print(m.id)
