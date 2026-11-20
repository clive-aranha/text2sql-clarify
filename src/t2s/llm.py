import json
import time
from typing import TypeVar

from openai import BadRequestError, OpenAI, RateLimitError
from pydantic import BaseModel, ValidationError

from .config import settings

T = TypeVar("T", bound=BaseModel)


class LLM:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

    def structured(self, system: str, user: str, model_cls: type[T], retries: int = 3) -> T:
        schema = json.dumps(model_cls.model_json_schema())
        messages = [
            {
                "role": "system",
                "content": f"{system}\n\nReturn ONLY JSON matching this JSON Schema:\n{schema}",
            },
            {"role": "user", "content": user},
        ]
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=0 if attempt == 0 else 0.3,
                    response_format={"type": "json_object"},
                )
            except (BadRequestError, RateLimitError) as e:
                # The model failed to produce JSON, or we hit a rate limit: wait and retry.
                last_error = e
                time.sleep(2 * (attempt + 1))
                continue

            raw = resp.choices[0].message.content or ""
            try:
                return model_cls.model_validate_json(raw)
            except ValidationError as e:
                last_error = e
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {"role": "user", "content": f"Invalid output. Fix these errors, JSON only:\n{e}"}
                )
        raise RuntimeError(f"LLM failed to produce valid output: {last_error}")
