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
  - Tạo Thumbnail Viral: Agent học kiến thức từ skill `youtube-thumbnail` để tạo prompt linh hoạt, sau đó sinh ảnh trực tiếp qua `generate_image` (Gemini 3.1 Flash Image) hoặc FLUX local fallback, lưu vào `out/thumbnail.jpg` (9:16) và `out/thumbnail_16_9.jpg` (16:9). Không dùng script cứng.

## 4. Kiến trúc high-level
- **10-Stage Pipeline:** Brief/Canon -> Script (Gate 1) -> Plates -> Images -> Gate 2 -> Voice -> Render -> QC/Learn -> Thumbnail -> Package.
- **Multi-Slide Pacing:** Một đoạn voice (Line) có thể map với nhiều visual (Slide) để giữ nhịp độ video mà không bị giật lùi audio. Xử lý logic tại `sflib/timeline.py`.
- **Tích hợp bên ngoài:** Sử dụng VoiceStudio/Kokoro TTS cho giọng nói (`sflib/voicestudio.py`); sử dụng FFmpeg (có compile `h264_videotoolbox` và `libass`) để xử lý caption và render hardware acceleration.
- **Agent Roles:** Quy trình sản xuất được orchestration bởi `sf-director` skill gọi các script qua CLI, các skill khác xử lý các task hẹp hơn như biên kịch (`sf-script`), tạo ảnh (`sf-visual`), cast giọng (`sf-audio`). Toàn bộ skill được viết bằng tiếng Anh.

## 5. Quy ước quan trọng
- **Thêm tính năng mới:** Nếu thêm tính năng cho quy trình tạo video, cần bổ sung logic vào `scripts/` hoặc `scripts/sflib/`. Bất kỳ thay đổi cấu trúc nào của `story.json` đều phải được cập nhật ở `schemas/story.schema.json`.
- **Nguyên tắc Agent:** Các Agent không được tự động sửa những file hoặc metadata được sinh ra tự động bởi scripts (asset path, hash, audio measurements, etc.).
- **Ngôn ngữ Skill:** Tất cả file SKILL.md TRONG TOÀN BỘ hệ thống (kể cả `.agents/skills/`) bắt buộc phải ghi bằng tiếng Anh.
- **Ưu tiên công nghệ tạo ảnh (Image Generation Priority):**
  - **Khi chạy trên Antigravity:** Ưu tiên sinh ảnh bằng Gemini 3.1 Flash Image do chính Agent IDE thực hiện (qua tool `generate_image`), vừa nhanh vừa chất lượng cao.
  - **Fallback:** Nếu chạy trên IDE khác (Cursor, Claude Code, Terminal) hoặc agent không thể gọi tool tạo ảnh, fallback về FLUX.2 local qua `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`.
  - **Bố cục ảnh (Full-frame):** Không ép buộc tạo section text hoặc chừa khoảng trống ở đáy ảnh (`no clean lower third margin`); ảnh phải tràn khung tự nhiên và sinh động.
- **Nhịp độ video & Chuyển cảnh (Fast Pacing):** Tăng số lượng ảnh để đẩy nhịp chuyển cảnh nhanh (1.5s – 2.5s / slide cut), giúp video luôn có biến đổi thị giác dồn dập, đẩy mạnh tỷ lệ hoàn thành (completion rate).
- **Quy chuẩn thoại & Giọng đọc (Audio Flow):** Hạn chế tối đa dấu phẩy `,`, triệt tiêu dấu ba chấm `...` và ngoặc kép giữa các vế câu liền mạch; sử dụng liên từ ngữ pháp (`thì`, `và`, `khiến`) để công cụ TTS đọc một mạch tự nhiên, không bị ngắt khựng bất thường.
- **Quy chuẩn Subtext (Karaoke & Highlighting):** Khi làm subtext theo kiểu highlight (Karaoke), BẮT BUỘC dùng cơ chế "Audio-Visual Anticipation" (Pre-roll khoảng 40ms) và hiệu ứng Micro-Flash chuyển màu (\t trong ASS). Tuyệt đối KHÔNG thay đổi font scale, spacing hoặc tắt/bật tag `\b` giữa chừng (nên set bold mặc định) để tránh rục rịch layout chữ.
- **Quy chuẩn Thumbnail Viral (Linh hoạt qua Agent Skill):** Sau khi render xong video, Agent trực tiếp đọc kiến thức từ skill `youtube-thumbnail` (tỷ lệ gương mặt biểu cảm/hero 30-50%, bảng 2 màu tương phản cao, text hook 3-4 từ kích thích tò mò không che góc phải dưới) để tự viết prompt thích ứng theo ngữ cảnh kịch bản, sau đó tạo ảnh trực tiếp bằng Gemini 3.1 Flash Image (`generate_image`) hoặc fallback FLUX. Tuyệt đối KHÔNG dùng script sinh ảnh cứng; xuất đồng thời cả 2 tỷ lệ 9:16 và 16:9 vào `out/`.
- **Cơ chế tiến hoá qua Feedback (Continuous Learning):** Mỗi lần người dùng gửi `/story-feedback`, Agent BẮT BUỘC phải cập nhật ngay các quy tắc/note vào `library/taste.md`, `library/checks.md`, `AGENTS.md` và các file `SKILL.md` liên quan để hướng dẫn các Agent thế hệ sau tiến hóa thông minh hơn, không lặp lại lỗi cũ.

## 6. Lưu ý bảo mật/rủi ro
- Không hardcode API key. Cấu hình provider nên nằm trong file `.yaml` tại thư mục `config/` (đã được .gitignore cấu hình nhạy cảm nếu có).
- File `library/checks.md` là nơi chứa knowledge về lỗi để AI tự tránh, KHÔNG phải nơi lưu "taste" (thẩm mỹ).
- Đảm bảo môi trường chạy có đủ FFmpeg và uv trước khi execute pipeline.

---
*Lưu ý cho AI Sessions:* Hãy đọc file này trước tiên khi bắt đầu làm việc. Nếu thay đổi kiến trúc, quy ước, thêm lệnh, HÃY CẬP NHẬT TRỰC TIẾP VÀO FILE NÀY!

