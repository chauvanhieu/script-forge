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
  - Khởi tạo sạch (Zero-Drift Scaffolding): `uv run scripts/sf_init.py projects/<slug> [--type factual|fiction|adaptation]`
  - Validate: `uv run scripts/sf_validate.py projects/<slug>`
  - Tạo ảnh qua Gemini IDE: Phát Single-Turn Mega-Batch `generate_image`, sau đó chạy: `uv run scripts/sf_sync_gemini_images.py projects/<slug>`
  - Tạo ảnh qua FLUX (Fallback): `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`
  - Xem trước ảnh: `uv run scripts/sf_contact_sheet.py projects/<slug>`
  - Tạo giọng nói: `uv run scripts/sf_voice.py projects/<slug>`
  - Khớp chữ & Subtitle: `uv run scripts/sf_align.py projects/<slug>` và `uv run scripts/sf_captions.py projects/<slug>`
  - Render Video: `uv run scripts/sf_render.py projects/<slug>`
  - QC & Cập nhật: `uv run scripts/sf_qc.py projects/<slug>` và `uv run scripts/sf_learn.py projects/<slug>`
  - Tạo Thumbnail Viral: Agent học kiến thức từ skill `youtube-thumbnail` để tạo prompt linh hoạt, sau đó sinh ảnh trực tiếp qua `generate_image` (Gemini 3.1 Flash Image) hoặc FLUX local fallback, lưu vào `out/thumbnail.jpg` (9:16) và `out/thumbnail_16_9.jpg` (16:9). Không dùng script cứng.

## 4. Kiến trúc high-level
- **10-Stage Pipeline:** Brief/Canon -> Script (Gate 1) -> Plates -> Production (Images || Voice) -> Gate 2 -> Render -> QC/Learn -> Thumbnail -> Package. (Giai đoạn tạo ảnh và tạo giọng đọc diễn ra song song với cơ chế Fail-fast).
- **Multi-Slide Pacing:** Một đoạn voice (Line) có thể map với nhiều visual (Slide) để giữ nhịp độ video mà không bị giật lùi audio. Xử lý logic tại `sflib/timeline.py`.
- **Tích hợp bên ngoài:** Sử dụng VoiceStudio/Kokoro TTS cho giọng nói (`sflib/voicestudio.py`); sử dụng FFmpeg (có compile `h264_videotoolbox` và `libass`) để xử lý caption và render hardware acceleration.
- **Agent Roles:** Quy trình sản xuất được orchestration bởi `sf-director` skill gọi các script qua CLI, các skill khác xử lý các task hẹp hơn như biên kịch (`sf-script`), tạo ảnh (`sf-visual`), cast giọng (`sf-audio`). Toàn bộ skill được viết bằng tiếng Anh.

## 5. Quy ước quan trọng
- **Thêm tính năng mới:** Nếu thêm tính năng cho quy trình tạo video, cần bổ sung logic vào `scripts/` hoặc `scripts/sflib/`. Bất kỳ thay đổi cấu trúc nào của `story.json` đều phải được cập nhật ở `schemas/story.schema.json`.
- **Nguyên tắc Agent:** Các Agent không được tự động sửa những file hoặc metadata được sinh ra tự động bởi scripts (asset path, hash, audio measurements, etc.).
- **Tập trung thực thi (Zero-Drift Execution & No past project analysis):** Khi tạo video mới, Agent BẮT BUỘC dùng lệnh `uv run scripts/sf_init.py projects/<slug>` để khởi tạo. TUYỆT ĐỐI KHÔNG dùng `list_dir` hoặc `view_file` trên thư mục `projects/` để xem lại các dự án cũ. Hãy đi thẳng vào việc điền kịch bản vào `story.json` dựa trên knowledge hiện tại ở `library/` và các kỹ năng (`SKILL.md`) để tiết kiệm thời gian.
- **Ngôn ngữ Skill:** Tất cả file SKILL.md TRONG TOÀN BỘ hệ thống (kể cả `.agents/skills/`) bắt buộc phải ghi bằng tiếng Anh.
- **Ưu tiên công nghệ tạo ảnh (Image Generation Priority):**
  - **Khi chạy trên Antigravity (Single-Turn Mega-Batch + Auto-Sync):** Ưu tiên sinh ảnh bằng Gemini 3.1 Flash Image do chính Agent IDE thực hiện. **Yêu cầu Agent bắt buộc gom toàn bộ prompt của 20–26 slide và phát DUY NHẤT 1 TURN MEGA-BATCH tool calls `generate_image`** (đặt tên `<slug>_s01` ... `<slug>_sXX`). Không chia vụn thành nhiều turn hỏi-đáp. Ngay sau khi batch hoàn thành, Agent kích hoạt `uv run scripts/sf_sync_gemini_images.py projects/<slug>` để tự động đồng bộ ảnh vào `images/`, băm SHA256 input_hash, cập nhật `story.json` và dựng contact sheet trong 1 giây. Tuyệt đối không viết script python thủ công trong chat.
  - **Fallback:** Nếu chạy trên IDE khác (Cursor, Claude Code, Terminal) hoặc agent không thể gọi tool tạo ảnh, fallback về FLUX (ưu tiên giữ model tốt nhất flux2-klein-4b và chạy tuần tự để tránh OOM) qua `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`.
  - **Bố cục ảnh (Full-frame):** Không ép buộc tạo section text hoặc chừa khoảng trống ở đáy ảnh (`no clean lower third margin`); ảnh phải tràn khung tự nhiên và sinh động.
- **Nhịp độ video & Chuyển cảnh (Fast Pacing):** Tăng số lượng ảnh để đẩy nhịp chuyển cảnh nhanh (1.5s – 2.5s / slide cut), giúp video luôn có biến đổi thị giác dồn dập, đẩy mạnh tỷ lệ hoàn thành (completion rate).
- **Quy chuẩn thoại & Giọng đọc (Audio Flow):** Hạn chế tối đa dấu phẩy `,`, triệt tiêu dấu ba chấm `...` và ngoặc kép giữa các vế câu liền mạch; sử dụng liên từ ngữ pháp (`thì`, `và`, `khiến`) để công cụ TTS đọc một mạch tự nhiên, không bị ngắt khựng bất thường.
- **Quy chuẩn Subtext (Karaoke & Highlighting):** Khi làm subtext theo kiểu highlight (Karaoke), BẮT BUỘC dùng cơ chế "Audio-Visual Anticipation" (Pre-roll khoảng 40ms) và hiệu ứng Micro-Flash chuyển màu (\t trong ASS). Tuyệt đối KHÔNG thay đổi font scale, spacing hoặc tắt/bật tag `\b` giữa chừng (nên set bold mặc định) để tránh rục rịch layout chữ.
- **Quy chuẩn Đặt tên Dự án (Timestamped Projects):** Thư mục dự án trong `projects/` BẮT BUỘC có tiền tố timestamp theo định dạng `projects/YYYYMMDD-HHMMSS-<slug>` (lệnh `uv run scripts/sf_init.py projects/<slug>` sẽ tự động chèn timestamp nếu chưa có). Điều này giúp IDE, terminal và hệ điều hành tự động sort danh sách dự án theo thứ tự thời gian tạo một cách trực quan, rõ ràng.
- **Quy chuẩn Merge Video Final & Metadata SEO (In-File SEO Tags):** Khi render video qua `sf_render.py`, file video thành phẩm BẮT BUỘC được đặt tên theo tiêu đề video chuẩn SEO (`out/<sanitized-seo-title>.mp4`), đồng thời hệ thống tự động nhúng toàn bộ siêu dữ liệu ngầm vào container MP4 bằng FFmpeg (`title`, `comment`, `description`, `synopsis`, `keywords`, `artist`, `genre`, `date`, cờ `-movflags +faststart`). Đồng thời tạo alias symlink `out/final.mp4` để tương thích ngược. Điều này giúp thuật toán YouTube và các công cụ tìm kiếm index video chính xác ngay từ lúc upload file thô.
- **Quy chuẩn Thumbnail Viral (Linh hoạt qua Agent Skill - T011/T013):** Sau khi render xong video, Agent trực tiếp áp dụng triệt để kiến thức từ skill `youtube-thumbnail`: (1) Gương mặt biểu cảm tột độ (shock/disbelief/frustration) chiếm 30–50% diện tích khung hình (rõ nét ở kích thước nhỏ), (2) Bắt buộc tích hợp trực tiếp **Text Hook 3–5 từ in hoa cực lớn** (ví dụ: "LEGALLY DEAD", "ALIVE BUT DEAD") với màu sắc tương phản cao (Vàng Hổ Phách `#F5A623` hoặc Trắng viền đen dày) bố trí ở nửa trên để kích nổ CTR ngay khi nhìn lướt trên mobile 320px, (3) Bảng 2 màu tương phản mạnh mẽ (Hổ phách/Vàng vs Đen bóng/Xanh phiến thạch), (4) Một yếu tố phụ trợ kịch tính (búa thẩm phán gõ nảy lửa hoặc cán cân công lý nghiêng lệch), tuyệt đối không để chi tiết quan trọng ở góc phải dưới (tránh bị che bởi thời lượng video). Xuất đồng thời cả 2 tỷ lệ 9:16 và 16:9 vào `out/thumbnail.jpg` và `out/thumbnail_16_9.jpg`.
- **Cơ chế tiến hoá qua Feedback (Continuous Learning):** Mỗi lần người dùng gửi `/story-feedback`, Agent BẮT BUỘC phải cập nhật ngay các quy tắc/note vào `library/taste.md`, `library/checks.md`, `AGENTS.md` và các file `SKILL.md` liên quan để hướng dẫn các Agent thế hệ sau tiến hóa thông minh hơn, không lặp lại lỗi cũ.

## 6. Lưu ý bảo mật/rủi ro
- Không hardcode API key. Cấu hình provider nên nằm trong file `.yaml` tại thư mục `config/` (đã được .gitignore cấu hình nhạy cảm nếu có).
- File `library/checks.md` là nơi chứa knowledge về lỗi để AI tự tránh, KHÔNG phải nơi lưu "taste" (thẩm mỹ).
- Đảm bảo môi trường chạy có đủ FFmpeg và uv trước khi execute pipeline.

---
*Lưu ý cho AI Sessions:* Hãy đọc file này trước tiên khi bắt đầu làm việc. Nếu thay đổi kiến trúc, quy ước, thêm lệnh, HÃY CẬP NHẬT TRỰC TIẾP VÀO FILE NÀY!

