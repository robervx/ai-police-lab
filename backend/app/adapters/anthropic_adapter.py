"""Anthropic Messages API using the same semantic input and output budget."""

from .base import ModelReply, ProviderConfig, ProviderError


class AnthropicAdapter:
    def __init__(self, config: ProviderConfig, api_key: str, *, client=None):
        from anthropic import Anthropic

        self.config = config
        self._client = client or Anthropic(
            api_key=api_key, base_url="https://api.anthropic.com",
            timeout=config.timeout_seconds, max_retries=0,
        )

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply:
        from anthropic import APIConnectionError, APIStatusError, APITimeoutError, APIResponseValidationError

        try:
            response = self._client.messages.create(
                model=self.config.model_id,
                system=instructions,
                messages=messages,
                max_tokens=self.config.max_output_tokens,
            )
        except APITimeoutError:
            raise ProviderError("timeout", recoverable=True) from None
        except APIConnectionError:
            raise ProviderError("connection_error", recoverable=True) from None
        except APIStatusError as exc:
            raise ProviderError(f"http_{exc.status_code}",
                                recoverable=exc.status_code in {408, 409, 429} or exc.status_code >= 500) from None
        except (APIResponseValidationError, ValueError):
            raise ProviderError("malformed_response") from None
        try:
            return self._normalize(response)
        except (AttributeError, TypeError, ValueError):
            raise ProviderError("malformed_response") from None

    @staticmethod
    def _normalize(response) -> ModelReply:
        if not isinstance(response.model, str) or not isinstance(response.id, str):
            raise ValueError("Missing response identity")
        text = "".join(block.text for block in response.content if block.type == "text")
        return ModelReply(
            text=text, model_id=response.model, response_id=response.id,
            usage=response.usage.model_dump(),
            completed=response.stop_reason == "end_turn" and bool(text),
            finish_reason=str(response.stop_reason),
        )

    def close(self) -> None:
        self._client.close()
