# Kiến thức dự án: StoryForge 🎬⚡

## 1. Tổng quan dự án
- **Mục đích:** StoryForge là một AI Video Production Engine tự động (Autonomous) tập trung vào Viral Retention Architecture (Kiến trúc giữ chân người xem) và Multi-Slide Pacing (Nhịp độ đa slide). Giúp tạo các video dọc (Shorts/TikTok/Reels) và ngang chất lượng cao, sẵn sàng publish từ một ý tưởng ban đầu thành file `.mp4`.
- **Đối tượng:** Dành cho các AI Agents (đặc biệt là sf-director, sf-script, sf-visual, sf-audio, v.v.) và các developer/creator muốn tự động hóa việc tạo video với tỷ lệ hoàn thành (completion rate) cao.

## 2. Cấu trúc thư mục chính
- `config/`: Chứa cấu hình (providers, caption styles, local-image config).
- `docs/`: Tài liệu kỹ thuật, kế hoạch, specs.
- `library/`: Chứa kiến thức và quy chuẩn hệ thống (calibration, checks, taste, telemetry).
- `projects/`: Workspace chứa dữ liệu của từng video (mỗi video 1 thư mục với `story.json`, `script.md`...).
- `schemas/`: `story.schema.json` dùng để validate cấu trúc dữ liệu video.
- `scripts/`: Chứa các script Python thực thi 9 giai đoạn của pipeline (`sf_validate.py`, `sf_image.py`, v.v.).
  - `scripts/sflib/`: Thư viện core (timeline, media, project state, voicestudio client).
- `tools/`: Chứa công cụ hỗ trợ như `local-image` (MLX SDXL/FLUX cho Apple Silicon).
- `.agents/skills/`: Chứa các bộ kỹ năng (skills) định hướng Agent trong từng công đoạn (sf-script, sf-visual, sf-audio, sf-director...).

## 3. Các lệnh thường dùng
- **Cài đặt:** `uv sync` (Sử dụng uv làm package manager).
- **Chạy Test:** `uv run pytest` (Để chạy toàn bộ bài test) hoặc `uv run pytest tests/<tên_file>.py` để chạy test đơn lẻ.
- **Quy trình chạy 1 dự án (thư mục `projects/<slug>`):**
  - Khởi tạo & Validate: `uv run scripts/sf_validate.py projects/<slug>`
  - Tạo ảnh: `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`
  - Xem trước ảnh: `uv run scripts/sf_contact_sheet.py projects/<slug>`
  - Tạo giọng nói: `uv run scripts/sf_voice.py projects/<slug>`
  - Khớp chữ & Subtitle: `uv run scripts/sf_align.py projects/<slug>` và `uv run scripts/sf_captions.py projects/<slug>`
  - Render Video: `uv run scripts/sf_render.py projects/<slug>`
  - QC & Cập nhật: `uv run scripts/sf_qc.py projects/<slug>` và `uv run scripts/sf_learn.py projects/<slug>`

## 4. Kiến trúc high-level
- **9-Stage Pipeline:** Brief/Canon -> Script (Gate 1) -> Plates -> Images -> Gate 2 -> Voice -> Render -> QC/Learn -> Package.
- **Multi-Slide Pacing:** Một đoạn voice (Line) có thể map với nhiều visual (Slide) để giữ nhịp độ video mà không bị giật lùi audio. Xử lý logic tại `sflib/timeline.py`.
- **Tích hợp bên ngoài:** Sử dụng VoiceStudio/Kokoro TTS cho giọng nói (`sflib/voicestudio.py`); sử dụng FFmpeg (có compile `h264_videotoolbox` và `libass`) để xử lý caption và render hardware acceleration.
- **Agent Roles:** Quy trình sản xuất được orchestration bởi `sf-director` skill gọi các script qua CLI, các skill khác xử lý các task hẹp hơn như biên kịch (`sf-script`), tạo ảnh (`sf-visual`), cast giọng (`sf-audio`). Toàn bộ skill được viết bằng tiếng Anh.

## 5. Quy ước quan trọng
- **Thêm tính năng mới:** Nếu thêm tính năng cho quy trình tạo video, cần bổ sung logic vào `scripts/` hoặc `scripts/sflib/`. Bất kỳ thay đổi cấu trúc nào của `story.json` đều phải được cập nhật ở `schemas/story.schema.json`.
- **Nguyên tắc Agent:** Các Agent không được tự động sửa những file hoặc metadata được sinh ra tự động bởi scripts (asset path, hash, audio measurements, etc.).
- **Ngôn ngữ Skill:** Tất cả file SKILL.md TRONG TOÀN BỘ hệ thống (kể cả `.agents/skills/`) bắt buộc phải ghi bằng tiếng Anh.

## 6. Lưu ý bảo mật/rủi ro
- Không hardcode API key. Cấu hình provider nên nằm trong file `.yaml` tại thư mục `config/` (đã được .gitignore cấu hình nhạy cảm nếu có).
- File `library/checks.md` là nơi chứa knowledge về lỗi để AI tự tránh, KHÔNG phải nơi lưu "taste" (thẩm mỹ).
- Đảm bảo môi trường chạy có đủ FFmpeg và uv trước khi execute pipeline.

---
*Lưu ý cho AI Sessions:* Hãy đọc file này trước tiên khi bắt đầu làm việc. Nếu thay đổi kiến trúc, quy ước, thêm lệnh, HÃY CẬP NHẬT TRỰC TIẾP VÀO FILE NÀY!
