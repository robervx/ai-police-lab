"""OpenAI Responses API; local RuleEngine remains the action authority."""

from .base import ModelReply, ProviderConfig, ProviderError


class OpenAIAdapter:
    def __init__(self, config: ProviderConfig, api_key: str, *, client=None):
        from openai import OpenAI

        self.config = config
        self._client = client or OpenAI(
            api_key=api_key, base_url="https://api.openai.com/v1",
            timeout=config.timeout_seconds, max_retries=0,
        )

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply:
        from openai import APIConnectionError, APIStatusError, APITimeoutError, APIResponseValidationError

        try:
            response = self._client.responses.create(
                model=self.config.model_id,
                instructions=instructions,
                input=messages,
                max_output_tokens=self.config.max_output_tokens,
                store=False,
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
        if response.status not in {"completed", "incomplete", "failed", "cancelled", "queued", "in_progress"}:
            raise ValueError("Missing response status")
        refused = any(
            part.type == "refusal"
            for item in response.output if item.type == "message"
            for part in item.content
        )
        return ModelReply(
            text=response.output_text, model_id=response.model, response_id=response.id,
            usage=response.usage.model_dump() if response.usage else {},
            completed=response.status == "completed" and not refused and bool(response.output_text),
            finish_reason="refusal" if refused else str(response.status),
        )

    def close(self) -> None:
        self._client.close()
