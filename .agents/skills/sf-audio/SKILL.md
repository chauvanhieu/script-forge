---
name: sf-audio
description: Casts StoryForge voices (audition, library, design, clone), handles Vibe-to-Archetype matching, voice generation, expressive controls and retakes. Use for stage 6 (voice) and voice-related redos or feedback in a StoryForge production.
---

# sf-audio

## 1. Audition Gate (Pha 6A — Tuyển Chọn Giọng Thông Minh từ VoiceStudio)
VoiceStudio cung cấp hơn **1.126 Archetypes** và hỗ trợ sinh giọng trên **646 ngôn ngữ**. Agent đóng vai trò là Giám Đốc Tuyển Giọng (Casting Director), sử dụng hệ thống tra cứu đa chiều để chọn giọng hoàn hảo cho dự án.

> Xem hướng dẫn tra cứu chi tiết tại: [references/smart-voice-casting.md](file:///Users/irondev/Desktop/Projects/chauvanhieu/yt/.agents/skills/sf-audio/references/smart-voice-casting.md)

### Quy trình 1: Smart Auto-Matching (Agent phân tích kịch bản & tự chọn)
Chạy chế độ thông minh để hệ thống tự động bóc tách thể loại (`genre`), bối cảnh (`topic`), đối tượng khán giả (`audience`), quét 500 giọng từ VoiceStudio và chọn ra 3 giọng tối ưu nhất:
```bash
uv run scripts/sf_audition.py projects/<slug> --smart
```

### Quy trình 2: Tra Cứu Catalog Đa Chiều (Country, Language, Pitch, Use-case)
Agent có thể tra cứu theo bất kỳ tổ hợp tiêu chí nào (hỗ trợ `limit` lên tới 500 giọng):
```bash
# Lọc theo quốc gia (US, UK, AU, JP, CN...) và thể loại ứng dụng:
uv run scripts/sf_audition.py --list --country us --use-case narration --gender male --pitch low --limit 50

# Tìm kiếm tự do theo từ khóa (documentary, storyteller, calm, whisper, podcast):
uv run scripts/sf_audition.py --list -q "documentary" --limit 20

# Xuất dạng JSON để agent parse dữ liệu:
uv run scripts/sf_audition.py --list --limit 500 --json
```

### Quy trình 3: Thử Giọng Ứng Viên Trên Câu Hook (L001)
Agent chọn 2-3 giọng từ catalog để thử trực tiếp trên câu mở đầu của video:
```bash
# Thử các Archetype IDs cụ thể:
uv run scripts/sf_audition.py projects/<slug> --archetypes feat_01_the_documentarian feat_03_the_storyteller feat_02_the_calm_guide

# Thử theo bộ lọc quốc gia & thể loại:
uv run scripts/sf_audition.py projects/<slug> --country uk --use-case narration --gender male --limit 3
```
Hệ thống sẽ đo lường tốc độ nói (CPS) và thời lượng chính xác, xuất file preview tại `projects/<slug>/audio/previews/`.

### Quy trình 4: Chốt Giọng & Tổng Hợp Hàng Loạt
```bash
# Chốt theo mã số (opt1, opt2) hoặc Archetype ID và tự động sinh toàn bộ video:
uv run scripts/sf_audition.py projects/<slug> --select opt1 --batch
# hoặc:
uv run scripts/sf_audition.py projects/<slug> --select feat_01_the_documentarian --batch
```

---

## 2. Casting trực tiếp (per cast member, `voice` in story.json)
1. `source: library` + `library_ref` khi `library/cast/<ref>/voice.json` đã có sẵn (`{"profile_id", "instruct"}`) — tái sử dụng giọng định vị kênh.
2. `source: design` + `design_prompt`: các từ khóa thuộc tính chuẩn từ VoiceStudio:
   - `gender`: `male|female`
   - `age`: `child|teenager|young adult|middle-aged|elderly`
   - `pitch`: `very low pitch|low pitch|moderate pitch|high pitch|very high pitch`
   - Từ chỉ cảm xúc tự do không được hỗ trợ trong `instruct` (gây lỗi 400).
3. `source: clone` + file audio mẫu tham chiếu.

---

## 3. Điều khiển biểu cảm & Phát âm (Expressive controls)
- Dấu câu: `,`, `.`, `!`, `?` để ngắt nhịp thở.
- Khoảng dừng: `[pause]`, `[pause 300ms]`, `[pause 500ms]`.
- Từ điển phát âm: `[[từ hiển thị|từ đọc]]` (ví dụ: `[[80ms|tám mươi mi li giây]]`, `[[AI|ây ai]]`).
- Thì thầm: `whisper: true` trên từng câu thoại.

---

## 4. Tổng hợp hàng loạt (Pha 6B)
Sau khi đã chốt profile giọng trong `story.json`:
```bash
uv run scripts/sf_voice.py projects/<slug>
```
- Nếu có dòng bị `needs_human`: kiểm tra `audio.qc` (CER hoặc CPS), chỉnh sửa lại dấu câu hoặc `[[written|spoken]]` và chạy lại `--only <line id>`.
- Re-cast một giọng: chạy lại `uv run scripts/sf_audition.py projects/<slug>` để chọn giọng mới.

---

## 5. Lưu giọng định danh cho kênh (Recurring Channel Voice)
Khi muốn lưu giọng trúng tuyển làm giọng thương hiệu cố định cho kênh:
Lưu vào `library/cast/<tên-giọng>/voice.json` với `profile_id` và `instruct`, lần sau chỉ cần khai báo `source: library`.
