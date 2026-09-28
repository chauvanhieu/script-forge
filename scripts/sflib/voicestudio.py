"""Minimal client for the VoiceStudio local API (docs: VoiceStudio/docs, backend/api/routers)."""
from __future__ import annotations

import json
from pathlib import Path

import httpx

from sflib.project import ProviderError


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:300]
    detail = body.get("detail", body) if isinstance(body, dict) else body
    return detail[:300] if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)[:300]


class VoiceStudio:
    def __init__(self, base_url: str, *, transport: httpx.BaseTransport | None = None, timeout_s: float = 1900.0):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, transport=transport,
                                   timeout=httpx.Timeout(timeout_s, connect=10.0))

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = self.client.request(method, url, **kwargs)
        except httpx.TransportError as exc:
            raise ProviderError("transient", f"VoiceStudio {method} {url}: {exc}") from exc
        if response.status_code < 400:
            return response
        detail = _detail(response)
        if response.status_code == 409:
            raise ProviderError("auth", f"VoiceStudio setup needed: {detail}")
        if response.status_code >= 500 or response.status_code == 429 \
                or response.headers.get("X-OmniVoice-Retryable") == "true":
            raise ProviderError("transient", detail)
        raise ProviderError("invalid", f"{response.status_code}: {detail}")

    def health(self) -> None:
        try:
            response = self.client.get("/health")
        except httpx.TransportError as exc:
            raise ProviderError("auth", f"VoiceStudio is not reachable at {self.base_url}; "
                                        f"open the VoiceStudio app first ({exc})") from exc
        if response.status_code >= 400:
            raise ProviderError("auth", f"VoiceStudio /health returned {response.status_code}")

    def describe(self, description: str) -> dict:
        return self._request("POST", "/design/describe", json={"description": description}).json()

    def create_design_profile(self, name: str, attrs: dict, instruct: str, language: str) -> str:
        response = self._request("POST", "/profiles", data={
            "name": name, "kind": "design", "vd_states": json.dumps(attrs), "instruct": instruct, "language": language,
        })
        return response.json()["id"]

    def create_clone_profile(self, name: str, ref_audio: Path, ref_text: str, language: str) -> str:
        with ref_audio.open("rb") as fh:
            response = self._request("POST", "/profiles", data={
                "name": name, "kind": "clone", "ref_text": ref_text, "language": language,
            }, files={"ref_audio": (ref_audio.name, fh, "audio/wav")})
        return response.json()["id"]

    def generate(self, *, text: str, language: str, profile_id: str, seed: int,
                 engine: str | None = None, instruct: str | None = None) -> tuple[bytes, dict]:
        data = {"text": text, "language": language, "profile_id": profile_id, "seed": str(seed)}
        if engine:
            data["engine"] = engine
        if instruct:
            data["instruct"] = instruct
        response = self._request("POST", "/generate", data=data)
        meta = {
            "seed": response.headers.get("X-Seed"),
            "duration_s": response.headers.get("X-Audio-Duration"),
            "dropped_chunks": response.headers.get("X-OmniVoice-Dropped-Chunks"),
        }
        return response.content, meta

    def transcribe_words(self, wav: Path, language: str) -> list[dict]:
        with wav.open("rb") as fh:
            response = self._request("POST", "/transcribe", data={"language": language, "mode": "accurate"},
                                     files={"audio": (wav.name, fh, "audio/wav")})
        words = []
        for segment in response.json().get("segments", []):
            for word in segment.get("words") or []:
                text = (word.get("word") or word.get("text") or "").strip()
                if text:
                    words.append({"text": text, "start": word.get("start"), "end": word.get("end")})
        return words
