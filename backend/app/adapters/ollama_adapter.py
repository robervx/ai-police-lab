"""Ollama native local chat. No pull, installation or remote endpoint fallback."""

from .base import ModelReply, ProviderConfig, ProviderError
from .http_transport import JsonTransport


class OllamaAdapter:
    def __init__(self, config: ProviderConfig, api_key: str | None = None, *,
                 transport: JsonTransport | None = None) -> None:
        self.config = config
        self._transport = transport or JsonTransport()

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply:
        payload: dict[str, object] = {"model": self.config.model_id, "stream": False,
                   "messages": [{"role": "system", "content": instructions}, *messages],
                   "options": {"num_predict": self.config.max_output_tokens}}
        data = self._transport.post("http://127.0.0.1:11434/api/chat", payload, {}, self.config.timeout_seconds)
        try:
            model, message, reason = data["model"], data["message"], data["done_reason"]
            text = message["content"]
            if (not isinstance(model, str) or not isinstance(text, str)
                    or not isinstance(reason, str) or type(data["done"]) is not bool):
                raise ValueError("Invalid response")
            usage = {k: data[k] for k in ("prompt_eval_count", "eval_count", "total_duration",
                                         "load_duration", "prompt_eval_duration", "eval_duration") if k in data}
            complete = data["done"] and reason == "stop" and bool(text) and not message.get("tool_calls")
            return ModelReply(text, model, None, usage, complete, reason)
        except (KeyError, TypeError, ValueError):
            raise ProviderError("malformed_response") from None

    def close(self) -> None:
        self._transport.close()
