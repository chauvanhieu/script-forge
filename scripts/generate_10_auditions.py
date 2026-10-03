#!/usr/bin/env python3
"""Generate 10 distinct deep, soulful, and evocative Vietnamese audition voices for Buddhist wisdom / reflection."""
import json
from pathlib import Path
from sflib.voicestudio import VoiceStudio

def main():
    vs = VoiceStudio("http://localhost:3900")
    sample_text = "Tại sao người ăn ở hiền lành mà cuộc đời vẫn lận đận chông gai"
    out_dir = Path("projects/20261002-210638-tai-sao-nguoi-hien-lai-kho/audio/audition_voices")
    out_dir.mkdir(parents=True, exist_ok=True)

    voice_definitions = [
        {
            "id": "giong_01_nam_storyteller_tram_am",
            "title": "Giọng 01: Nam Cao Niên - Trầm Ấm Kể Chuyện",
            "archetype_id": "feat_03_the_storyteller",
            "kind": "archetype",
            "seed": 101,
            "tone": "Trầm ấm, từng trải, khoan thai, như bậc cao niên kể chuyện nhân quả.",
        },
        {
            "id": "giong_02_nam_dinh_dac_thau_suot",
            "title": "Giọng 02: Nam Trung Niên - Đĩnh Đạc Thấu Suốt",
            "archetype_id": "feat_01_the_documentarian",
            "kind": "archetype",
            "seed": 202,
            "tone": "Trầm vừa, rõ ràng, dứt khoát, phong thái người khai sáng triết lý.",
        },
        {
            "id": "giong_03_nam_tram_sau_chieu_sau",
            "title": "Giọng 03: Nam Trung Niên - Trầm Sâu Nội Lực",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "middle-aged", "Pitch": "very low pitch", "Style": "Auto", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, middle-aged, very low pitch",
            "seed": 303,
            "tone": "Tông nam trầm sâu (very low pitch), vang dội, giàu nội lực tâm linh.",
        },
        {
            "id": "giong_04_nam_lao_su_uy_nghiem",
            "title": "Giọng 04: Nam Lão Sư - Thiền Sư Uy Nghiêm",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "elderly", "Pitch": "very low pitch", "Style": "Auto", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, elderly, very low pitch",
            "seed": 404,
            "tone": "Chất giọng trầm mặc, cổ kính như tiếng chuông đồng vọng lại từ cổ tự.",
        },
        {
            "id": "giong_05_nam_thi_tham_chua_lanh",
            "title": "Giọng 05: Nam Trung Niên - Thì Thầm Chữa Lành",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "middle-aged", "Pitch": "low pitch", "Style": "whisper", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, middle-aged, low pitch, whisper",
            "seed": 505,
            "tone": "Tông trầm pha hơi thở thì thầm tĩnh tại, rất êm ái, xoa dịu muộn phiền.",
        },
        {
            "id": "giong_06_nam_tu_su_dong_cam",
            "title": "Giọng 06: Nam Trung Niên - Tự Sự Đồng Cảm",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "middle-aged", "Pitch": "low pitch", "Style": "Auto", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, middle-aged, low pitch",
            "seed": 777,
            "tone": "Giọng nam trung niên đằm thắm, nhả chữ chân thành, giàu cảm xúc sẻ chia.",
        },
        {
            "id": "giong_07_nu_tram_diu_bao_dung",
            "title": "Giọng 07: Nữ Trung Niên - Trầm Dịu Bao Dung",
            "archetype_id": "feat_02_the_calm_guide",
            "kind": "archetype",
            "seed": 707,
            "tone": "Giọng nữ trầm ấm, thì thầm dịu dàng như người mẹ bao dung vỗ về tâm hồn.",
        },
        {
            "id": "giong_08_nu_tram_sau_chiem_nghiem",
            "title": "Giọng 08: Nữ Trung Niên - Trầm Sâu Chiêm Nghiệm",
            "archetype_id": "feat_00_the_librarian",
            "kind": "archetype",
            "seed": 808,
            "tone": "Tông nữ trầm thanh tịnh, đĩnh đạc, mộc mạc, giàu tính chiêm nghiệm triết lý.",
        },
        {
            "id": "giong_09_nam_tram_am_nhan_nha",
            "title": "Giọng 09: Nam Trung Niên - Trầm Ấm Nhã Nhặn",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "middle-aged", "Pitch": "low pitch", "Style": "Auto", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, middle-aged, low pitch",
            "seed": 9999,
            "tone": "Tông nam ấm áp, tròn vành rõ chữ, nhã nhặn, vang hòa cùng tiếng chuông thiền.",
        },
        {
            "id": "giong_10_nam_thien_su_buong_xa",
            "title": "Giọng 10: Nam Cao Niên - Thiền Sư Buông Xả",
            "kind": "design",
            "attrs": {"Gender": "male", "Age": "elderly", "Pitch": "low pitch", "Style": "Auto", "EnglishAccent": "Auto", "ChineseDialect": "Auto"},
            "instruct": "male, elderly, low pitch",
            "seed": 8888,
            "tone": "Giọng cụ già hiền từ, nhả chữ chậm rãi, lắng đọng, giải thoát muộn phiền.",
        },
    ]

    results = []
    print(f"Generating {len(voice_definitions)} audition samples...")
    for idx, v in enumerate(voice_definitions, start=1):
        if v["kind"] == "archetype":
            arch = vs.use_archetype(v["archetype_id"], f"audition_{v['id']}")
            pid = arch["profile_id"]
            instruct = arch.get("instruct", "")
        else:
            pid = vs.create_design_profile(
                f"audition_{v['id']}",
                v["attrs"],
                v["instruct"],
                "vi",
                sample_text
            )
            instruct = v["instruct"]

        audio_bytes, meta = vs.generate(
            text=sample_text,
            language="vi",
            profile_id=pid,
            seed=v["seed"]
        )

        filename = f"{v['id']}.wav"
        file_path = out_dir / filename
        file_path.write_bytes(audio_bytes)

        duration = float(meta.get("duration_s") or 0.0)
        size_kb = round(len(audio_bytes) / 1024, 1)
        print(f"[{idx}/10] {filename} -> {duration}s ({size_kb} KB)")

        results.append({
            "order": idx,
            "id": v["id"],
            "filename": filename,
            "path": str(file_path),
            "title": v["title"],
            "kind": v["kind"],
            "profile_id": pid,
            "instruct": instruct,
            "seed": v["seed"],
            "duration_s": duration,
            "size_kb": size_kb,
            "tone": v["tone"]
        })

    catalog_path = out_dir / "audition_catalog.json"
    catalog_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done! Catalog saved to {catalog_path}")

if __name__ == "__main__":
    main()
