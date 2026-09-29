# Services

## VoiceStudio (voices + ASR) — required before `sf_voice`, `sf_align`

Health: `curl -s -m 3 http://localhost:3900/health` → `{"status":"ok",...}`.
If it fails, start it from the repo root and poll health every 5 s for up to 90 s:

    mkdir -p logs && (cd VoiceStudio && nohup uv run uvicorn main:app --app-dir backend --host 127.0.0.1 --port 3900 > ../logs/voicestudio.log 2>&1 &)

Models needed (install once via `POST /models/install {"repo_id": ...}`): `k2-fsa/OmniVoice`,
`mlx-community/whisper-large-v3-mlx`.

## Local image generation — used by `sf_image`

Always pass `SF_CONFIG=config/providers.local-image.yaml` (FLUX.2-klein-4B via mflux,
~20–30 s per image, ~13 GB RAM). Do not run it concurrently with another image job.
The default `config/providers.yaml` uses the `fake` provider (tests, smoke test).
