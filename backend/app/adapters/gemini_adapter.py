"""Gemini generateContent REST adapter. No model IDs are chosen automatically."""

import re

from .base import ModelReply, ProviderConfig, ProviderError
from .http_transport import JsonTransport


class GeminiAdapter:
    def __init__(self, config: ProviderConfig, api_key: str, *, transport: JsonTransport | None = None) -> None:
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", config.model_id):
            raise ValueError("Gemini requires a model ID without models/ prefix")
        self.config, self._key = config, api_key
        self._transport = transport or JsonTransport()

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply:
        payload: dict[str, object] = {
            "systemInstruction": {"parts": [{"text": instructions}]},
            "contents": [{"role": "model" if m["role"] == "assistant" else "user",
                          "parts": [{"text": m["content"]}]} for m in messages],
            "generationConfig": {"maxOutputTokens": self.config.max_output_tokens, "candidateCount": 1},
        }
        data = self._transport.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model_id}:generateContent",
            payload, {"x-goog-api-key": self._key}, self.config.timeout_seconds)
        try:
            model, response_id = data.get("modelVersion"), data.get("responseId")
            if any(v is not None and not isinstance(v, str) for v in (model, response_id)):
                raise ValueError("Invalid identity")
            usage = data.get("usageMetadata", {})
            if not isinstance(usage, dict):
                raise ValueError("Invalid usage")
            candidates = data.get("candidates", [])
            if not candidates:
                if not data.get("promptFeedback", {}).get("blockReason"):
                    raise ValueError("No candidates or block reason")
                return ModelReply("", model, response_id, usage, False, "prompt_blocked")
            if len(candidates) != 1:
                raise ValueError("Unexpected candidates")
            candidate = candidates[0]
            reason = candidate["finishReason"]
            if not isinstance(reason, str):
                raise ValueError("Invalid completion status")
            text = "".join(p["text"] for p in candidate.get("content", {}).get("parts", [])
                           if "text" in p and not p.get("thought", False))
            return ModelReply(text, model, response_id, usage, reason == "STOP" and bool(text), reason)
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ProviderError("malformed_response") from None

    def close(self) -> None:
        self._transport.close()
