import json
from http.client import IncompleteRead
from io import BytesIO
from urllib.error import HTTPError

import pytest

from backend.app.adapters.base import ProviderConfig, ProviderError
from backend.app.adapters.gemini_adapter import GeminiAdapter
from backend.app.adapters.http_transport import JsonTransport, NoRedirect
from backend.app.adapters.ollama_adapter import OllamaAdapter
from backend.app.event_store import read_events
from backend.app.provider_runner import run_comparison

CLOSE = {"action": "CLOSE", "final_decision": "Fin", "actions_taken": [], "verified_facts": [],
         "unverified_claims": [], "remaining_uncertainties": [], "justification": "Prueba"}


def body(provider, text=None, reason=None):
    text = json.dumps(CLOSE) if text is None else text
    if provider == "gemini":
        return {"modelVersion": "resolved-gemini", "responseId": "real-response-id",
                "candidates": [{"finishReason": reason or "STOP", "content": {"parts": [
                    {"thought": True, "text": "PRIVATE_REASONING"}, {"text": text}]}}],
                "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 9}}
    return {"model": "local-model:tag", "message": {"role": "assistant", "content": text},
            "done": True, "done_reason": reason or "stop", "prompt_eval_count": 12, "eval_count": 9}


class Opener:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.requests = []
        self.closed = False

    def open(self, request, *, timeout):
        self.requests.append((request, timeout))
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return BytesIO(response if isinstance(response, bytes) else json.dumps(response).encode())

    def close(self):
        self.closed = True


def adapter(provider, *responses):
    opener = Opener(*responses)
    config = ProviderConfig(provider=provider, model_id="requested-model", max_retries=0)
    klass = GeminiAdapter if provider == "gemini" else OllamaAdapter
    return klass(config, "secret-test-key", transport=JsonTransport(opener)), opener


@pytest.mark.parametrize("provider", ["gemini", "ollama"])
def test_request_normalization_and_complete_session(provider, tmp_path):
    client, opener = adapter(provider, body(provider))
    result, = run_comparison([client], tmp_path)
    assert result.status == "agent_close"
    events = read_events(result.path)
    request = next(e["payload"] for e in events if e["type"] == "provider_request")
    assert request["transport"] == "python_urllib" and request["sdk_version"] is None
    response = next(e["payload"] for e in events if e["type"] == "provider_response")
    assert "PRIVATE_REASONING" not in response["text"]
    req, timeout = opener.requests[0]
    data = json.loads(req.data)
    assert timeout == client.config.timeout_seconds
    if provider == "gemini":
        assert req.full_url.startswith("https://generativelanguage.googleapis.com/")
        assert "secret-test-key" not in req.full_url
        assert req.get_header("X-goog-api-key") == "secret-test-key"
        assert data["generationConfig"]["maxOutputTokens"] == 1500
        assert data["contents"][0]["role"] == "user"
    else:
        assert req.full_url == "http://127.0.0.1:11434/api/chat"
        assert data["stream"] is False and data["options"]["num_predict"] == 1500
        assert data["messages"][0]["role"] == "system"
        assert response["response_id"] is None
    assert "secret-test-key" not in result.path.read_text()
    client.close()
    assert opener.closed


@pytest.mark.parametrize("provider,reason", [("gemini", "MAX_TOKENS"), ("gemini", "SAFETY"),
                                          ("ollama", "length")])
def test_truncated_or_blocked_response_never_executes(provider, reason, tmp_path):
    client, _ = adapter(provider, body(provider, reason=reason))
    result, = run_comparison([client], tmp_path)
    assert result.status == "provider_error" and result.turns == 0
    assert not any(e["type"] == "agent_action_requested" for e in read_events(result.path))


def test_gemini_blocked_prompt_does_not_invent_model_identity(tmp_path):
    client, _ = adapter("gemini", {"promptFeedback": {"blockReason": "SAFETY"}})
    result, = run_comparison([client], tmp_path)
    outcomes = json.loads((result.path.parent / "manifest-outcomes.json").read_text())
    assert outcomes["participants"][0]["resolved_model_ids"] == []
    assert outcomes["participants"][0]["trace_status"] == "complete"
    assert result.status == "provider_error"


@pytest.mark.parametrize("bad", [b"{", b"[]", b"x" * 2_000_001, {}, {"candidates": None}])
def test_malformed_http_response_is_controlled(bad):
    client, _ = adapter("gemini", bad)
    with pytest.raises(ProviderError, match="malformed_response"):
        client.generate("instructions", [{"role": "user", "content": "hello"}])


@pytest.mark.parametrize("error,code", [(TimeoutError("SECRET_BODY"), "timeout"),
    (HTTPError("https://example.invalid", 429, "SECRET_BODY", {}, BytesIO(b"SECRET_BODY")), "http_429"),
    (HTTPError("https://example.invalid", 302, "SECRET_BODY", {}, BytesIO()), "http_302")])
def test_transport_errors_have_only_safe_codes(error, code):
    client, _ = adapter("gemini", error)
    with pytest.raises(ProviderError) as captured:
        client.generate("instructions", [])
    assert str(captured.value) == code
    assert NoRedirect().redirect_request(None, None, None, None, None, None) is None


def test_gemini_multiturn_roles_and_thought_exclusion():
    client, opener = adapter("gemini", body("gemini"))
    reply = client.generate("same instructions", [{"role": "user", "content": "one"},
        {"role": "assistant", "content": "two"}, {"role": "user", "content": "three"}])
    data = json.loads(opener.requests[0][0].data)
    assert [c["role"] for c in data["contents"]] == ["user", "model", "user"]
    assert data["systemInstruction"]["parts"][0]["text"] == "same instructions"
    assert "PRIVATE_REASONING" not in reply.text


def test_truncated_http_body_closes_only_affected_participant(tmp_path):
    first, _ = adapter("gemini", IncompleteRead(b"SECRET_BODY", 100))
    second, _ = adapter("ollama", body("ollama"))
    results = run_comparison([first, second], tmp_path)
    assert [r.status for r in results] == ["provider_error", "agent_close"]
    assert "SECRET_BODY" not in results[0].path.read_text()
    error = next(e["payload"] for e in read_events(results[0].path) if e["type"] == "provider_error")
    assert error["code"] == "connection_error"


def test_gemini_blocked_response_validates_usage():
    client, _ = adapter("gemini", {"promptFeedback": {"blockReason": "SAFETY"}, "usageMetadata": []})
    with pytest.raises(ProviderError, match="malformed_response"):
        client.generate("instructions", [])
