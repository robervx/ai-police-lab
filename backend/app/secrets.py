"""Keep configured credentials out of messages, logs and terminal output."""

import re


class Redactor:
    def __init__(self, secrets: tuple[str, ...] = ()):
        self._secrets = tuple(sorted((s for s in secrets if s), key=len, reverse=True))

    def __call__(self, value):
        if isinstance(value, str):
            for secret in self._secrets:
                value = value.replace(secret, "[REDACTED]")
            return re.sub(r"\bsk-[A-Za-z0-9_-]{8,}", "[REDACTED]", value)
        if isinstance(value, dict):
            return {self(str(key)): self(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self(item) for item in value]
        return value
