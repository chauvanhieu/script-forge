# Kiến thức dự án: StoryForge 🎬⚡

## 1. Tổng quan dự án
- **Mục đích:** StoryForge là một AI Video Production Engine tự động (Autonomous) tập trung vào Viral Retention Architecture (Kiến trúc giữ chân người xem) và Multi-Slide Pacing (Nhịp độ đa slide). Giúp tạo các video dọc (Shorts/TikTok/Reels) và ngang chất lượng cao, sẵn sàng publish từ một ý tưởng ban đầu thành file `.mp4`.
- **Đối tượng:** Dành cho các AI Agents (đặc biệt là sf-director, sf-script, sf-visual, sf-audio, v.v.) và các developer/creator muốn tự động hóa việc tạo video với tỷ lệ hoàn thành (completion rate) cao.

## 2. Cấu trúc thư mục chính
- `channels/`: Chứa các file blueprint quy chuẩn thương hiệu, phong cách thị giác và định vị nội dung riêng biệt của từng kênh (mỗi kênh 1 file markdown, ví dụ `channels/the-grey-verdict.md`).
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
- **Lệnh Slash Commands:**
  - **Lên Ý Tưởng Video:** `/create-idea [chủ đề/kênh/từ khóa spark]` — Agent đọc các quy chuẩn hệ thống (`library/taste.md`, `library/checks.md`), blueprint của kênh tương ứng trong `channels/` (nếu có chỉ định) và các skill sáng tạo (`premise-workshop`, `hook-generator`, `content-matrix`, `sf-script`, `youtube-thumbnail`) để sinh 5 ý tưởng kịch tính với cấu trúc giữ chân người xem cao, hook 3 lớp và thumbnail concept.
  - **Sản Xuất Video Tự Động:** `/create-video "<slug> - <ý tưởng>"` — Chạy toàn bộ pipeline StoryForge từ kịch bản, ảnh, voice, phụ đề đến render và thumbnail.
- **Quản lý & Khởi Tạo Kênh (Multi-Channel Operations):**
  - Liệt kê kênh: `uv run scripts/sf_channel.py list`
  - Tạo kênh mới chuẩn 6-module: `uv run scripts/sf_channel.py new <slug> [--name "Tên Kênh"] [--niche "Ngách"] [--lang en|vi]`
  - Kiểm tra tính hợp lệ module: `uv run scripts/sf_channel.py validate [slug]`
- **Quy trình chạy 1 dự án (thư mục `projects/<slug>`):**
  - Khởi tạo sạch (Zero-Drift Scaffolding): `uv run scripts/sf_init.py projects/<slug> [--channel <channel-slug>] [--type factual|fiction|adaptation]`
  - Validate: `uv run scripts/sf_validate.py projects/<slug>`
  - Tạo ảnh qua Gemini IDE: Phát Single-Turn Mega-Batch `generate_image`, sau đó chạy: `uv run scripts/sf_sync_gemini_images.py projects/<slug>`
  - Tạo ảnh qua FLUX (Fallback): `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`
  - Xem trước ảnh: `uv run scripts/sf_contact_sheet.py projects/<slug>`
  - Tạo giọng nói: `uv run scripts/sf_voice.py projects/<slug>`
  - Khớp chữ & Subtitle: `uv run scripts/sf_align.py projects/<slug>` và `uv run scripts/sf_captions.py projects/<slug>`
  - Render Video: `uv run scripts/sf_render.py projects/<slug>`
  - QC & Cập nhật: `uv run scripts/sf_qc.py projects/<slug>` và `uv run scripts/sf_learn.py projects/<slug>`
  - Tạo Thumbnail Viral: Agent học kiến thức từ skill `youtube-thumbnail` để tạo prompt linh hoạt, sau đó sinh ảnh trực tiếp qua `generate_image` (Gemini 3.1 Flash Image) hoặc FLUX local fallback, lưu vào `out/thumbnail.jpg` (9:16) hoặc `out/thumbnail_16_9.jpg` (16:9) tương ứng đúng tỷ lệ của video (chỉ tạo 1 thumbnail). Không dùng script cứng.

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
- **Quy chuẩn Vị trí & Kích thước Phụ đề (Captions Placement & Balance - T019):** Di chuyển phụ đề xuống **1/3 dưới cùng của màn hình** (`margin_v_pct` ~ 14%–16% cách mép đáy, tương đương ~288px trên khung dọc 1080x1920) để nằm ngay trên vùng an toàn của thanh điều hướng TikTok/Shorts nhưng tuyệt đối không đẩy lên trung tâm che lấp khuôn mặt và tiêu điểm hành động của hình ảnh. Kích thước font chữ thu nhỏ thanh thoát (khoảng 72–76pt trên 9:16, outline 5–6px) giúp người xem đọc mượt mà, dễ chịu mà không bị phân tâm khỏi trải nghiệm thị giác của video. Khi làm subtext theo kiểu highlight (Karaoke), BẮT BUỘC dùng cơ chế "Audio-Visual Anticipation" (Pre-roll khoảng 40ms) và hiệu ứng Micro-Flash chuyển màu (\t trong ASS). Tuyệt đối KHÔNG thay đổi font scale, spacing hoặc tắt/bật tag `\b` giữa chừng để tránh rục rịch layout chữ.
- **Quy chuẩn Nhất quán Thị giác Nhân vật (Character Visual Continuity & Anchor Traits - T020):** Để khán giả dễ dàng theo dõi và kết nối cảm xúc với câu chuyện, khi kịch bản có các nhân vật xuất hiện lặp lại (nhân vật chính, nhân chứng, nạn nhân...), Agent biên kịch và tạo ảnh (`sf-script`, `sf-visual`) BẮT BUỘC: (1) Thiết lập bộ **Đặc Điểm Nhận Diện Neo Cố Định (Anchor Traits)** trong `story.cast` (độ tuổi chính xác, kiểu tóc, màu tóc, đặc điểm khuôn mặt, trang phục cố định, phụ kiện bất biến), (2) Lặp lại NGUYÊN VĂN các từ khóa mô tả diện mạo này trong TẤT CẢ các slide prompt có nhân vật xuất hiện, (3) Tận dụng cơ chế `plates/` làm ảnh chân dung tham chiếu (`ImagePaths` trong Gemini IDE hoặc reference plates trong FLUX) để đảm bảo nhân vật giữ nguyên ngoại hình nhất quán từ đầu đến cuối video.
- **Quy chuẩn Đặt tên Dự án (Timestamped Projects):** Thư mục dự án trong `projects/` BẮT BUỘC có tiền tố timestamp theo định dạng `projects/YYYYMMDD-HHMMSS-<slug>` (lệnh `uv run scripts/sf_init.py projects/<slug>` sẽ tự động chèn timestamp nếu chưa có). Điều này giúp IDE, terminal và hệ điều hành tự động sort danh sách dự án theo thứ tự thời gian tạo một cách trực quan, rõ ràng.
- **Kiến trúc Đa Kênh & Phân Vùng Trí Tuệ (Multi-Channel & Isolated Intelligence Architecture):** StoryForge là Autonomous Production Engine dùng chung cho nhiều kênh khác nhau với các ngách nội dung, ngôn ngữ và phong cách thị giác khác biệt. Các quy chuẩn ở `AGENTS.md`, `scripts/`, `library/` là quy chuẩn kỹ thuật cốt lõi (Core Engine Standards) áp dụng cho mọi video (ví dụ: pipeline 10 giai đoạn, 1 video duy nhất mang tên slug, 1 thumbnail đúng aspect, karaoke subtext 40ms pre-roll, vùng an toàn safe zones, cấm ví dụ cụ thể trong prompt). **MỌI QUY TẮC RIÊNG CỦA TỪNG KÊNH BẮT BUỘC ĐƯỢC LƯU TRONG THƯ MỤC RIÊNG BIỆT `channels/<channel-slug>/` (gồm 6 file module: `blueprint.md`, `style-bible.md`, `narrative-dna.md`, `thumbnail-system.md`, `voice-profile.md`, `taste.md`)**, tuyệt đối KHÔNG hardcode vào các file chính của source.
- **Quy chuẩn Xuất Video Duy Nhất & Siêu Dữ Liệu SEO (Single Video & In-File SEO Tags - T014):** Khi render video qua `sf_render.py`, file video thành phẩm BẮT BUỘC được xuất trực tiếp ra DUY NHẤT 1 file mang tên slug sạch của dự án (`out/<base_slug>.mp4`), tuyệt đối KHÔNG tạo hay nhân bản/symlink thêm file `final.mp4` để tránh dư thừa dung lượng và phân mảnh. Hệ thống tự động nhúng toàn bộ siêu dữ liệu ngầm vào container MP4 bằng FFmpeg (`title`, `comment`, `description`, `synopsis`, `keywords`, `artist`, `genre`, `date`, cờ `-movflags +faststart`), giúp thuật toán YouTube và các công cụ tìm kiếm index video chính xác ngay từ lúc upload file thô.
- **Quy chuẩn Thumbnail Viral Chuẩn Aspect, Vùng An Toàn & Sáng Tạo Bối Cảnh (Single Aspect, Safe Margin & Creative Diversity - T011/T013/T015/T017/T018):** Sau khi render xong video, Agent trực tiếp áp dụng triệt để kiến thức từ skill `youtube-thumbnail` kết hợp với quy chuẩn thương hiệu của kênh trong `channels/<channel-slug>/`: (1) Gương mặt hoặc chủ thể biểu cảm tột độ (shock/disbelief/intensity/curiosity) chiếm 35–45% diện tích khung hình (rõ nét ở kích thước nhỏ), (2) Bắt buộc tích hợp trực tiếp **Text Hook 2–4 từ in hoa cực lớn** với màu sắc tương phản cao (theo bảng màu nhận diện của kênh hoặc Trắng viền đen dày), (3) **Quy tắc Vùng An Toàn Đỉnh (Top Safe Margin - T017):** Với thumbnail dọc (9:16), BẮT BUỘC chừa lề trống an toàn 10%–15% ở mép đỉnh trên cùng (dark headroom), chữ hook phải nằm gọn gàng ở phần trên nhưng KHÔNG ĐƯỢC chạm sát viền trên, tránh bị bo góc hoặc khung card của YouTube Shorts cắt cụt chữ ("bị khuất chữ ở trên"), (4) **Đa dạng hóa sáng tạo bối cảnh & đạo cụ theo nguyên tắc trừu tượng (Creative Diversity - T018):** TUYỆT ĐỐI KHÔNG THÊM VÍ DỤ CỤ THỂ VÀO PROMPT. Không rập khuôn bất kỳ đạo cụ hay bối cảnh cố định nào cho mọi video. Đồng bộ nhận diện thương hiệu chỉ tập trung vào Bảng màu và phong cách typography của từng kênh (quy định tại `channels/<channel-slug>/style-bible.md` và `thumbnail-system.md`); còn bối cảnh, đạo cụ và nhân vật phải được mô tả trừu tượng để AI tự do suy luận linh hoạt bám sát nội dung kịch bản thực tế, (5) Tuyệt đối không để chi tiết quan trọng ở góc phải dưới (tránh bị che bởi thời lượng video). **CHỈ XUẤT DUY NHẤT 1 THUMBNAIL** tương ứng với tỷ lệ của video (`out/thumbnail.jpg` cho 9:16 hoặc `out/thumbnail_16_9.jpg` cho 16:9), không sinh thừa thumbnail cho tỷ lệ không dùng.
- **Quy chuẩn Báo cáo Xuất bản (Publishing Package Reporting - T016):** Ở bước báo cáo kết quả cuối cùng, Agent BẮT BUỘC xuất: (1) Khối **Tags** chuẩn bị sẵn dưới dạng chuỗi các từ khóa SEO ngăn cách nhau bởi dấu phẩy (`tag1,tag2,tag3...`) không ngắt dòng để người dùng copy 1-click dán thẳng vào ô Tags của YouTube Studio (giới hạn 500 ký tự), (2) Các **Hashtags** liên quan được đính kèm trực tiếp vào cuối phần Description (mô tả video) thay vì để rời rạc.
- **Cơ chế Phân Luồng Feedback 2 Cấp & Tiến Hoá Độc Lập (2-Tier Feedback Routing - T019):** Mỗi lần người dùng gửi `/story-feedback <slug> "<feedback>"`, Agent BẮT BUỘC thực hiện phân luồng tri thức chính xác:
  1. *Feedback thuộc về bản sắc, thẩm mỹ, kịch bản, giọng đọc, quy tắc thumbnail của riêng kênh:* BẮT BUỘC ghi vào `channels/<channel-slug>/taste.md`. Tuyệt đối KHÔNG ghi vào `library/taste.md` của source tổng để tránh ô nhiễm chéo giữa các kênh.
  2. *Feedback thuộc về lỗi kỹ thuật khách quan của core engine (FFmpeg, Whisper alignment, ASS syntax):* Ghi vào `library/checks.md`.
  3. *Feedback thuộc về quy chuẩn kỹ thuật phổ quát toàn hệ thống (áp dụng cho mọi video bất kể kênh nào):* Ghi vào `library/taste.md` và `AGENTS.md`.

## 6. Lưu ý bảo mật/rủi ro
- Không hardcode API key. Cấu hình provider nên nằm trong file `.yaml` tại thư mục `config/` (đã được .gitignore cấu hình nhạy cảm nếu có).
- File `library/checks.md` là nơi chứa knowledge về lỗi để AI tự tránh, KHÔNG phải nơi lưu "taste" (thẩm mỹ).
- Đảm bảo môi trường chạy có đủ FFmpeg và uv trước khi execute pipeline.

---
*Lưu ý cho AI Sessions:* Hãy đọc file này trước tiên khi bắt đầu làm việc. Nếu thay đổi kiến trúc, quy ước, thêm lệnh, HÃY CẬP NHẬT TRỰC TIẾP VÀO FILE NÀY!

