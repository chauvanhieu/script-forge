#!/usr/bin/env python3
"""Manage, sync, and inspect channel topic ledgers to prevent content cannibalization."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT

LEDGER_FILENAME = "topic-ledger.md"
COOLDOWN_LIMIT = 30  # Recent N items in active cooldown window


def get_channels_dir() -> Path:
    return ROOT / "channels"


def get_projects_dir() -> Path:
    return ROOT / "projects"


def extract_date_from_slug(slug_or_dir: str) -> str:
    m = re.match(r"^(\d{4})(\d{2})(\d{2})", slug_or_dir)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return datetime.now().strftime("%Y-%m-%d")


def infer_core_mechanism(slug: str, idea: str, title: str) -> str:
    combined = f"{slug} {idea} {title}".lower()
    
    # Common known mechanisms for biology-of-desire
    if any(k in combined for k in ["slot-machine", "intermittent", "skinner", "ignore", "mixed signal", "cờ bạc"]):
        return "B.F. Skinner / Intermittent Variable Reward Schedule (Dopamine Slot Machine)"
    if any(k in combined for k in ["coolidge", "passion fade", "18 month", "18-month"]):
        return "The Coolidge Effect / Dopamine Novelty Reset"
    if any(k in combined for k in ["prolactin", "refractory", "numb after", "goes cold"]):
        return "Prolactin Surge & Post-Coital Refractory Drop"
    if any(k in combined for k in ["gas", "brake", "dual control"]):
        return "Dual Control Model (Sexual Excitation vs Inhibition SES/SIS)"
    if any(k in combined for k in ["oxytocin", "red flag", "blind spot", "blindness", "blind to danger"]):
        return "Oxytocin Amygdala Dampening & Trust Blindness"
    if any(k in combined for k in ["testosterone", "npt", "6am"]):
        return "Circadian Testosterone Peak & Endothelial NPT Signaling"
    if any(k in combined for k in ["sweaty t-shirt", "sweaty t shirt", "mhc", "olfactory mate", "body odor"]):
        return "MHC Gene Compatibility & Olfactory Mate Selection (Sweaty T-Shirt Experiment)"
    if any(k in combined for k in ["the ick", "sudden disgust", "revulsion"]):
        return "The Ick / Involuntary Olfactory & Pathogen Revulsion Reflex"
    if any(k in combined for k in ["limerence", "tennov", "obsessive attachment", "cuồng si"]):
        return "Limerence & Serotonin Depletion / OCD Neuro-Overlap"
    if any(k in combined for k in ["birth control", "contraceptive", "pill mate"]):
        return "Hormonal Contraceptive Mate Preference Reversal"
    if any(k in combined for k in ["angry sex", "makeup sex", "adrenaline spike"]):
        return "Adrenaline Surge & Sexual Arousal Reappraisal (Angry Sex)"
    if any(k in combined for k in ["heartbeat", "cardiac synchrony"]):
        return "Autonomous Heartbeat Synchronization in Romantic Dyads"
    
    # Common known cases for the-grey-verdict
    if any(k in combined for k in ["parking-meter", "75-year", "chicago"]):
        return "Chicago Parking Meter 75-Year Wall Street Lease (2008)"
    if any(k in combined for k in ["pepsi", "fighter jet", "harrier"]):
        return "Leonard v. Pepsico (1999) - $33M Harrier Jet Commercial Offer"
    if any(k in combined for k in ["katko", "briney", "spring-gun", "deadly-trespasser"]):
        return "Katko v. Briney (1971) - Spring-Gun Booby Trap on Property"
    if any(k in combined for k in ["custom of the sea", "dudley", "stephens", "cabin boy"]):
        return "R v. Dudley and Stephens (1884) - Necessity Defense in Maritime Cannibalism"
    if any(k in combined for k in ["good-samaritan", "burning car", "van horn"]):
        return "Van Horn v. Watson (2008) - Good Samaritan Rescue Liability"
    if any(k in combined for k in ["bodily-integrity", "mcfall", "shimp", "bone marrow"]):
        return "McFall v. Shimp (1978) - Forced Bodily Organ/Marrow Donation"
    if any(k in combined for k in ["reverse-bank-robbery", "bank of america"]):
        return "Florida Foreclosure Legal Execution against Bank of America (2011)"
    if any(k in combined for k in ["unlimited-flight", "rothstein", "aairpass", "10,000 times"]):
        return "American Airlines Lifetime Unlimited AAirpass Contract Termination (2008)"
    if any(k in combined for k in ["living-dead", "donald miller"]):
        return "Donald Miller Ohio Presumption of Death Legal Fiction (2013)"
        
    # tam-an-giac-ngo
    if "khau-nghiep" in combined:
        return "Khẩu Nghiệp & Phước Đức Từ Lời Nói"
    if "nguoi-hien" in combined:
        return "Nghiệp Báo Người Lương Thiện Gặp Nạn"
    if "con-cai" in combined:
        return "4 Mối Duyên Nợ Cha Mẹ và Con Cái"
    if "phan-boi" in combined:
        return "Nhân Quả Người Phản Bội & Trả Thù Bằng Buông Bỏ"
    if "tra-het-nghiep" in combined:
        return "Dấu Hiệu Trả Hết Nghiệp Cũ Đón Đại Vận"
    if "3-noi-dung-den" in combined:
        return "3 Nơi Đừng Đến 3 Người Đừng Nhờ Khi Sa Cơ"
        
    # the-karma-pawnshop
    if "bought-10-extra-years" in combined:
        return "Ký Hợp Đồng Mua Thêm 10 Năm Tuổi Thọ & Điều Khoản 27"

    # Fallback to cleaned title/idea
    if title:
        return title[:70]
    return idea[:70] if idea else slug.replace("-", " ").title()


def scan_channel_projects(channel_slug: str) -> list[dict]:
    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        return []

    channel_projects = []
    for p in sorted(projects_dir.iterdir()):
        if not p.is_dir() or p.name.startswith("."):
            continue
        story_file = p / "story.json"
        if not story_file.exists():
            continue
        try:
            data = json.loads(story_file.read_text(encoding="utf-8"))
            brief = data.get("brief", {})
            c_slug = brief.get("channel", "")
            if not c_slug:
                # check fallback from style_bible / seo / author
                author = data.get("seo", {}).get("author", "").lower()
                if channel_slug.replace("-", " ") in author:
                    c_slug = channel_slug
            
            if c_slug != channel_slug:
                continue

            stage = data.get("state", {}).get("stage", "")
            # check if completed or script approved
            has_video = (p / "out").exists() and any((p / "out").glob("*.mp4"))
            is_valid = stage == "done" or has_video or stage in ["gate2", "render", "qc"]

            slug = data.get("slug", p.name)
            date_str = extract_date_from_slug(p.name)
            idea = brief.get("idea", "")
            title = data.get("seo", {}).get("title", "")
            mechanism = infer_core_mechanism(slug, idea, title)

            channel_projects.append({
                "dir": p.name,
                "slug": slug,
                "date": date_str,
                "idea": idea,
                "title": title,
                "mechanism": mechanism,
                "status": "done" if (stage == "done" or has_video) else stage or "in-progress"
            })
        except Exception:
            continue

    # Sort descending by date/dir
    channel_projects.sort(key=lambda x: x["dir"], reverse=True)
    return channel_projects


def build_ledger_markdown(channel_slug: str, projects: list[dict]) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d")
    channel_title = channel_slug.replace("-", " ").title()

    lines = [
        f"# Topic Ledger & Cooldown Registry: {channel_title}",
        "",
        "> **Mục đích:** File này lưu trữ lịch sử đề tài đã sản xuất của kênh nhằm triệt tiêu hoàn toàn hiện tượng trùng lặp ý tưởng (Content Cannibalization) và tự động mở rộng sang các phân nhánh nội dung mới.",
        "> **Quy tắc bắt buộc đối với `/create-idea`:**",
        "> 1. Đọc phần **Active Cooldown Window** bên dưới trước khi đề xuất bất kỳ ý tưởng nào.",
        "> 2. **CẤM TUYỆT ĐỐI** đề xuất lại các cơ chế/vụ án (Core Mechanisms) đang nằm trong danh sách Hồi chiêu (Active Cooldown).",
        "> 3. Bắt buộc phân bổ 5 ý tưởng theo 5 Trụ Cột Độc Lập (Content Pillars) được quy định trong `blueprint.md`.",
        "",
        "---",
        "",
        f"## 1. Vùng Hồi Chiêu Đang Hiệu Lực (Active Cooldown Window - {COOLDOWN_LIMIT} Video Gần Nhất)",
        "",
        "Các chủ đề, cơ chế sinh học hoặc vụ việc trong bảng này **ĐÃ BÃO HÒA** trên kênh. Agent tạo ý tưởng BẮT BUỘC bỏ qua các đề tài này:",
        "",
        "| STT | Ngày | Mã Slug Dự Án | Cơ Chế / Vụ Việc Cốt Lõi (Core Mechanism) | Tiêu Đề Đã Xuất Bản | Trạng Thái |",
        "| :---: | :---: | :--- | :--- | :--- | :---: |",
    ]

    active_items = projects[:COOLDOWN_LIMIT]
    archive_items = projects[COOLDOWN_LIMIT:]

    if not active_items:
        lines.append("| - | - | *(Chưa có video nào)* | *(Chưa có)* | *(Chưa có)* | - |")
    else:
        for idx, item in enumerate(active_items, 1):
            s_date = item["date"]
            s_slug = item["dir"]
            s_mech = item["mechanism"].replace("|", "/")
            s_title = (item["title"] or item["idea"] or s_slug)[:60].replace("|", "/")
            s_stat = "✅ Done" if item["status"] == "done" else "⏳ " + item["status"]
            lines.append(f"| {idx:02d} | {s_date} | `{s_slug}` | **{s_mech}** | {s_title} | {s_stat} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Kho Lưu Trữ Lịch Sử (Historical Archive - Đã Hết Hạn Hồi Chiêu)",
        "",
        "Các chủ đề trong mục này đã sản xuất từ lâu. Kênh **có thể tái khai thác (Remake / Angle Pivot)** nếu tìm được một góc nhìn, nghịch lý hoặc bằng chứng mới mẻ hoàn toàn khác biệt:",
        "",
        "| STT | Ngày | Mã Slug Dự Án | Cơ Chế / Vụ Việc Cốt Lõi | Tiêu Đề Cũ |",
        "| :---: | :---: | :--- | :--- | :--- |",
    ])

    if not archive_items:
        lines.append("| - | - | *(Kho lưu trữ trống)* | *(Chưa có video cũ)* | *(Chưa có)* |")
    else:
        for idx, item in enumerate(archive_items, 1):
            s_date = item["date"]
            s_slug = item["dir"]
            s_mech = item["mechanism"].replace("|", "/")
            s_title = (item["title"] or item["idea"] or s_slug)[:60].replace("|", "/")
            lines.append(f"| {idx:02d} | {s_date} | `{s_slug}` | {s_mech} | {s_title} |")

    lines.extend([
        "",
        "---",
        "",
        f"*Đồng bộ tự động lần cuối: {now_str} qua `sf_ledger.py`*",
        ""
    ])

    return "\n".join(lines)


def sync_channel(channel_slug: str) -> dict:
    channel_dir = get_channels_dir() / channel_slug
    if not channel_dir.exists():
        return {"ok": False, "channel": channel_slug, "error": f"Channel directory {channel_slug} does not exist"}

    projects = scan_channel_projects(channel_slug)
    content = build_ledger_markdown(channel_slug, projects)
    ledger_path = channel_dir / LEDGER_FILENAME
    ledger_path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "channel": channel_slug,
        "ledger": str(ledger_path),
        "total_projects": len(projects),
        "cooldown_count": min(len(projects), COOLDOWN_LIMIT),
        "archived_count": max(0, len(projects) - COOLDOWN_LIMIT)
    }


def sync_all_channels() -> list[dict]:
    channels_dir = get_channels_dir()
    if not channels_dir.exists():
        return []

    results = []
    for item in sorted(channels_dir.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue
        res = sync_channel(item.name)
        results.append(res)
    return results


def check_similarity(channel_slug: str, idea: str, slug: str = "") -> dict:
    channel_dir = get_channels_dir() / channel_slug
    ledger_path = channel_dir / LEDGER_FILENAME
    if not ledger_path.exists():
        return {"ok": True, "channel": channel_slug, "match": None, "score": 0.0, "warning": None}

    content = ledger_path.read_text(encoding="utf-8")
    
    # Extract cooldown section
    cooldown_match = re.search(r"## 1\. Vùng Hồi Chiêu Đang Hiệu Lực.*?\n(.*?)\n---", content, re.DOTALL)
    cooldown_text = cooldown_match.group(1) if cooldown_match else content

    # Check for direct mechanism triggers
    query_str = f"{slug} {idea}".lower()
    
    triggers = [
        ("B.F. Skinner / Intermittent Variable Reward", ["slot-machine", "intermittent", "skinner", "ignore", "mixed signal"]),
        ("The Coolidge Effect", ["coolidge", "passion fade", "18 month", "18-month"]),
        ("Prolactin Surge & Post-Coital Refractory Drop", ["prolactin", "refractory", "numb after", "goes cold"]),
        ("Oxytocin Amygdala Dampening & Trust Blindness", ["oxytocin", "threat-hijack", "blindness", "blind to danger", "threat hijack"]),
        ("Chicago Parking Meter Lease", ["parking meter", "parking-meter", "75 year", "75-year", "chicago street"]),
        ("Pepsi Fighter Jet", ["pepsi", "fighter jet", "harrier"]),
        ("Katko v. Briney Spring-Gun", ["katko", "spring-gun", "spring gun", "deadly trespasser"]),
    ]

    for label, keywords in triggers:
        if any(kw in query_str for kw in keywords):
            if label.lower() in cooldown_text.lower():
                return {
                    "ok": True,
                    "channel": channel_slug,
                    "match": label,
                    "score": 0.95,
                    "warning": f"CHỦ ĐỀ ĐANG HỒI CHIÊU: Cơ chế/Vụ việc '{label}' đã có trong Active Cooldown của kênh {channel_slug}."
                }

    return {"ok": True, "channel": channel_slug, "match": None, "score": 0.0, "warning": None}


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage channel topic ledgers and check topic duplicates")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: sync
    sync_parser = subparsers.add_parser("sync", help="Sync topic-ledger.md from existing projects")
    sync_parser.add_argument("channel", nargs="?", default="", help="Channel slug (optional, syncs all if omitted)")

    # Subcommand: check
    check_parser = subparsers.add_parser("check", help="Check if an idea or slug duplicates a cooldown topic")
    check_parser.add_argument("channel", help="Channel slug")
    check_parser.add_argument("--idea", required=True, help="Proposed idea or title")
    check_parser.add_argument("--slug", default="", help="Proposed slug")

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List active cooldown topics for a channel")
    list_parser.add_argument("channel", help="Channel slug")

    args = parser.parse_args()

    if args.command == "sync":
        if args.channel:
            res = sync_channel(args.channel)
            print(json.dumps(res, ensure_ascii=False))
            sys.exit(EXIT_OK if res["ok"] else EXIT_HUMAN)
        else:
            results = sync_all_channels()
            print(json.dumps({"ok": True, "results": results}, ensure_ascii=False))
            sys.exit(EXIT_OK)

    elif args.command == "check":
        res = check_similarity(args.channel, args.idea, args.slug)
        print(json.dumps(res, ensure_ascii=False))
        sys.exit(EXIT_OK)

    elif args.command == "list":
        channel_dir = get_channels_dir() / args.channel
        ledger_path = channel_dir / LEDGER_FILENAME
        if not ledger_path.exists():
            print(json.dumps({"ok": False, "error": f"Ledger not found for {args.channel}"}))
            sys.exit(EXIT_HUMAN)
        print(ledger_path.read_text(encoding="utf-8"))
        sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
