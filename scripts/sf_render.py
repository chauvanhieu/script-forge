#!/usr/bin/env python3
"""Render out/final.mp4: per-slide motion clips, a sample-exact audio timeline, and burned-in captions."""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
import wave

from sflib.media import decode_pcm, has_encoder, has_filter, run_ffmpeg
from sflib.project import EXIT_HUMAN, EXIT_OK, file_hash, input_hash, load_story, main_wrapper, save_story
from sflib.timeline import FPS, build_timeline

SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
ZOOM = 0.08
RATE = 48000


def sanitize_seo_filename(title: str, max_len: int = 80) -> str:
    """Convert a video title into an SEO-friendly, filesystem-safe filename slug."""
    title = title.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    slug = re.sub(r"-+", "-", slug)
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "video"


def motion_filter(motion: str, frames: int, width: int, height: int) -> str:
    n = frames
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "static":
        z, x, y = "1", center_x, center_y
    elif motion == "push_in":
        z, x, y = f"1+{ZOOM}*on/{n}", center_x, center_y
    elif motion == "pull_out":
        z, x, y = f"{1 + ZOOM}-{ZOOM}*on/{n}", center_x, center_y
    elif motion == "pan_left":
        z, x, y = f"{1 + ZOOM}", f"(iw-iw/zoom)*(1-on/{n})", center_y
    elif motion == "pan_right":
        z, x, y = f"{1 + ZOOM}", f"(iw-iw/zoom)*on/{n}", center_y
    else:
        raise ValueError(f"unknown motion {motion!r}")
    return (f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,crop={width * 2}:{height * 2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={width}x{height}:fps={FPS},setsar=1,format=yuv420p")


def _missing(story: dict, project_dir: Path) -> list[str]:
    missing = []
    for slide in story["slides"]:
        image = slide["image"]
        if image.get("status") != "done" or not (project_dir / (image.get("path") or "")).is_file():
            missing.append(f"{slide['id']}: image missing")
    for line in story["lines"]:
        audio = line["audio"]
        if audio.get("status") != "done" or not (project_dir / (audio.get("path") or "")).is_file():
            missing.append(f"{line['id']}: audio missing")
    return missing


def _write_timeline_wav(story: dict, timeline, project_dir: Path, out: Path) -> None:
    buffer = bytearray(round(timeline.total_ms * RATE / 1000) * 2)
    for line in story["lines"]:
        pcm = decode_pcm(project_dir / line["audio"]["path"], RATE)
        offset = round(timeline.line_start_ms[line["id"]] * RATE / 1000) * 2
        end = min(offset + len(pcm), len(buffer))
        buffer[offset:end] = pcm[: end - offset]
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(bytes(buffer))


def run(project_dir: Path, only: set[str] | None = None, size: tuple[int, int] | None = None) -> tuple[dict, int]:
    story = load_story(project_dir)
    summary: dict = {"video": None, "frames": 0, "duration_ms": 0, "rendered": [], "cached": 0, "needs_human": []}
    missing = _missing(story, project_dir)
    captions = None
    if story["brief"]["captions"]["mode"] != "none":
        captions = story["output"].get("captions")
        if not captions or not (project_dir / captions).is_file():
            missing.append("captions are not built; run sf_captions")
        elif not has_filter("ass"):
            missing.append("ffmpeg has no 'ass' filter; install an ffmpeg build with libass")
    if missing:
        summary["needs_human"] = missing
        return summary, EXIT_HUMAN
    width, height = size or SIZE[story["brief"]["aspect"]]
    timeline = build_timeline(story)
    use_vt = has_encoder("h264_videotoolbox")
    clip_codec = ["-c:v", "h264_videotoolbox", "-b:v", "8000k"] if use_vt else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
    final_codec = ["-c:v", "h264_videotoolbox", "-b:v", "6000k"] if use_vt else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    clips = project_dir / "clips"
    clips.mkdir(exist_ok=True)
    manifest_path = clips / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError):
        manifest = {}  # missing or corrupt: every clip is re-checked and rebuilt
    slides = {slide["id"]: slide for slide in story["slides"]}
    for span in timeline.slides:
        slide = slides[span.slide_id]
        if span.frames < 1:
            raise ValueError(f"{span.slide_id} spans {span.frames} frames; its lines are too short")
        image = project_dir / slide["image"]["path"]
        clip = clips / f"{span.slide_id}.mp4"
        clip_hash = input_hash({"image": file_hash(image), "motion": slide["visual"]["motion"],
                                "frames": span.frames, "size": [width, height]})
        if manifest.get(span.slide_id) == clip_hash and clip.is_file() and (only is None or span.slide_id not in only):
            summary["cached"] += 1
            continue
        run_ffmpeg(["-i", str(image), "-vf", motion_filter(slide["visual"]["motion"], span.frames, width, height),
                    "-frames:v", str(span.frames), *clip_codec,
                    "-pix_fmt", "yuv420p", "-r", str(FPS), str(clip)])
        manifest[span.slide_id] = clip_hash
        summary["rendered"].append(span.slide_id)
    manifest_tmp = manifest_path.with_suffix(".json.tmp")
    manifest_tmp.write_text(json.dumps(manifest, indent=2))
    os.replace(manifest_tmp, manifest_path)
    (clips / "concat.txt").write_text("".join(f"file '{span.slide_id}.mp4'\n" for span in timeline.slides))
    _write_timeline_wav(story, timeline, project_dir, clips / "timeline.wav")
    (project_dir / "out").mkdir(exist_ok=True)

    # SEO metadata extraction
    seo = story.get("seo") or {}
    brief = story.get("brief") or {}
    has_explicit_seo_title = bool(seo.get("title"))

    seo_title = seo.get("title") or brief.get("idea") or story.get("slug", "Video")
    seo_title = seo_title.split("\n")[0].strip()
    if len(seo_title) > 100:
        seo_title = seo_title[:97] + "..."

    seo_desc = seo.get("description") or brief.get("idea") or seo_title
    keywords = seo.get("keywords")
    if not keywords:
        keywords = [
            brief.get("genre", "general"),
            brief.get("content_type", "factual"),
            re.sub(r"^\d{8}(-\d{6})?-", "", story.get("slug", "")).replace("-", " "),
            "shorts",
            "viral"
        ]
    if isinstance(keywords, list):
        keywords_str = ", ".join(str(k) for k in keywords if k)
    else:
        keywords_str = str(keywords)

    author = seo.get("author") or "StoryForge"
    genre = brief.get("genre", "Education")
    date_str = datetime.now().strftime("%Y-%m-%d")

    metadata_args = [
        "-metadata", f"title={seo_title}",
        "-metadata", f"comment={seo_desc}",
        "-metadata", f"description={seo_desc}",
        "-metadata", f"synopsis={seo_desc}",
        "-metadata", f"keywords={keywords_str}",
        "-metadata", f"artist={author}",
        "-metadata", f"album_artist={author}",
        "-metadata", f"composer={author}",
        "-metadata", f"genre={genre}",
        "-metadata", f"date={date_str}",
    ]

    if has_explicit_seo_title:
        seo_slug = sanitize_seo_filename(seo_title)
        video_filename = f"{seo_slug}.mp4"
        video_rel = f"out/{video_filename}"
    else:
        video_filename = "final.mp4"
        video_rel = "out/final.mp4"

    target_video = project_dir / video_rel
    final_video = project_dir / "out/final.mp4"

    # Clean up obsolete video if filename changed
    old_video = story["output"].get("video")
    if old_video and old_video != video_rel and old_video != "out/final.mp4":
        old_path = project_dir / old_video
        if old_path.is_file():
            try:
                old_path.unlink()
            except OSError:
                pass

    args = ["-f", "concat", "-safe", "0", "-i", "clips/concat.txt", "-i", "clips/timeline.wav"]
    if captions:
        args += ["-vf", f"ass={captions}"]
    args += ["-map", "0:v", "-map", "1:a", *final_codec,
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
             "-ar", str(RATE), "-c:a", "aac", "-b:a", "192k", "-t", f"{timeline.total_ms / 1000:.3f}",
             *metadata_args,
             "-movflags", "+faststart", video_rel]
    run_ffmpeg(args, cwd=project_dir)

    if target_video != final_video:
        try:
            if final_video.is_symlink() or final_video.is_file():
                final_video.unlink()
            final_video.symlink_to(video_filename)
        except OSError:
            shutil.copy2(target_video, final_video)

    story["output"]["video"] = video_rel
    save_story(project_dir, story)
    summary.update(
        video=video_rel,
        final_alias="out/final.mp4" if video_rel != "out/final.mp4" else None,
        seo_title=seo_title,
        metadata_tags={"title": seo_title, "artist": author, "genre": genre, "keywords": keywords_str},
        frames=timeline.total_frames,
        duration_ms=timeline.total_ms
    )
    return summary, EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
