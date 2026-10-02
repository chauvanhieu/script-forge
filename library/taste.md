# Taste rules

Written only by `/story-feedback`, from the user's own feedback. Each rule is two lines:
`- T### [scope tags] rule` then `  ← <slug> · YYYY-MM-DD · "<the user's words>"`.
A rule that contradicts an older one of the same or broader scope replaces it (the old line is deleted and the new rule says "replaces T###").

- T001 [audio · vi] For dramatic peak lines (shouting, pleading, strong emotion), write shorter, more fragmented phrasing and lean on punctuation — VoiceStudio's design engine cannot render emotion/tone directly, so the script must carry the intensity.
  ← con-dau-bi-duoi-khoi-ban-tiec · 2026-09-29 · "ngữ điệu/cảm xúc không hợp cảnh (đặc biệt cảnh Bà Tâm quát mắng và Linh nói câu cuối cần cảm xúc mạnh)"
- T002 [image] Do not mandate an empty lower third or text section at the bottom of images; let visual compositions fill the frame naturally without artificial blank margins.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "thêm rule không cần section text ở bottom của ảnh"
- T003 [script · 9:16] Increase image density and pacing by assigning more slide cuts per line (targeting 1.5–2.5 s per slide cut) to maintain rapid visual pacing.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "cần thêm số lượng ảnh để tăng nhịp video chuyển cảnh."
- T004 [audio · vi] Minimize mid-sentence commas and eliminate ellipsis or quotes in continuous lines to avoid unnatural TTS pauses and ensure seamless speech flow.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "audio giọng đọc bị lỗi đọc ngưng ngắt chưa đúng, câu đọc liền mạch nhưng có những đoạn bị ngắt nghỉ không chính xác."
- T005 [image · antigravity] When running in Antigravity, prioritize generating video slide images using the agent's native IDE image tool (Gemini 3.1 flash image); only fallback to local FLUX.2 when running in other IDEs or when the native tool is unavailable.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "viết rule cho bước tạo ảnh, khi đang chạy bằng Antigravity thì ưu tiên tạo ảnh bằng gemini 3.1 flash image do chính agent IDE tạo ảnh cho video, nếu dùng IDE khác hoặc agent không thể tạo ảnh thì mới fallback về chế độ tạo ảnh bằng flux."
- T006 [global · feedback] On every user feedback, actively update and persist rules, notes, and lessons into markdown documentation (AGENTS.md, library/taste.md, and skills) so agents continuously evolve for all future video productions.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "mỗi lần feedback thì phải cập nhật rule/note vào các file markdown để hướng dẫn cho agent tiến hoá thông minh hơn cho mỗi lần tạo video sau này. note các ý của những feedback vào luôn nhé"
- T007 [video · captions] Use highly synchronized, dynamic subtext animations (`animation: "pop_up"` or `"slide_blur"` in story.json) mapped strictly to voice timing (keyword-by-keyword tracking), enhancing visual retention via elastic scales or sliding layers.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "bổ sung thêm thông tin: Cách hiển thị subtext... có mối liên hệ rất chặt chẽ và đồng bộ với giọng đọc... (CapCut - Kiểu Xếp Tầng & Slide Up/Blur)... (Premiere Pro - Kiểu Pop-Up Bouncing)... Mục đích là để não bộ người xem vừa nghe âm thanh vừa bắt trọn mặt chữ của từ khóa trọng tâm mà không cần phải đọc lướt cả câu dài."

- T008 [video · captions] Support "word-by-word" single captioning (`animation: "word_by_word"`) which places exactly one word center-screen, fully synchronized with audio, strictly without any motion transitions (no slide/fade/scale) for maximum direct impact.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "có thể edit subtext như kĩ thuật word-by-word không... Visual: Tại trung tâm màn hình chỉ xuất hiện duy nhất 1 chữ... Transition: None... Tốc độ xuất hiện đập vào mắt cực kì dứt khoát"

- T009 [video · captions] Support "Active Word Highlighting" / "Karaoke Bold" style (`mode: "karaoke"`, `animation: "none"`) where the entire phrase is displayed in a base color (e.g. white), and strictly only the current spoken word turns active (color only, base text must already be bold to avoid line width shifting), matching audio exactly via split event tracking.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "hiệu ứng nổi bật chữ theo kiểu là toàn bộ màu trắng hết, đọc đến chữ nào thì chữ đó bold vàng lên"

- T010 [video · captions] Elevate "Active Word Highlighting" / Karaoke timing to professional perfection by applying Audio-Visual Anticipation (e.g. 40ms pre-roll) and Micro-Flash Effects (\t fading to the target color), ensuring the visual highlight "punches" exactly with the phonetic attack of the vocal sound without layout shifts.
  ← co-che-rua-nao-khi-ngu · 2026-09-30 · "tinh vi hơn nữa để chữ active bold đúng thời điểm giọng đọc hơn nữa. tìm giải pháp nâng cấp giúp tôi"

- T011 [thumbnail · workflow] Generate viral thumbnails via direct Agent skill invocation (`youtube-thumbnail`), not rigid Python scripts — the Agent synthesizes a high-CTR text-to-image prompt dynamically from the script (30–50% expressive face/hero, 3–5 word hook phrase, 2-color dominant contrast), then generates the image directly using Gemini 3.1 Flash Image (`generate_image`) with local FLUX fallback, saving to `out/thumbnail.jpg` and `out/thumbnail_16_9.jpg`.
  ← sieu-nang-luc-tai-sinh-cua-gan · 2026-09-30 · "góp ý điều chỉnh ở bước tạo thumbnail: không cần tạo script để tạo thumbnail image mà chỉ cần agent gọi đến skill youtube-thumbnail để học kiến thức tạo prompt text-to-image rồi lấy prompt đó tạo ảnh với gemini hoặc fallback với flux để sinh ảnh thumbnail. giống như cách tạo ảnh slide vậy. không cần thêm script nào cả. linh hoạt hơn rất nhiều"

- T012 [channel · multi-channel] Channel-specific production formulas (narrative structure, visual mood, brand palette, audio persona) belong strictly in `channels/<channel-slug>.md` (e.g. `channels/the-grey-verdict.md`); core engine standards in `library/` remain strictly channel-agnostic.
  ← the-good-samaritan-trap · 2026-10-02 · "không được áp dụng các quy tắc của channel blueprint cho toàn bộ source dự án, hãy note những rule riêng cho kênh vào file CHANNEL_BLUEPRINT.md thay vì note vào các file chính của source"

- T013 [thumbnail · youtube-thumbnail] Strictly implement the youtube-thumbnail skill standards for high-CTR thumbnails: integrate a bold 2–4 word hook phrase in large high-contrast typography (matching the target channel's brand palette or white with heavy dark stroke) placed in the upper portion away from UI elements, ensure an expressive face filling 35–45% of the frame with high emotional intensity, enforce a two-color dominant contrast, and spotlight a dramatic secondary focal element representing the core conflict catalyst without concrete formulaic props (see T018).
  ← 20261001-202515-the-living-dead-verdict · 2026-10-01 · "tôi muốn thumbnail thu hút hơn, áp dụng sát với skill @youtube-thumbnail"

- T014 [render · video] Output a single video file named directly after the project slug (out/<base_slug>.mp4) with embedded metadata; do not generate or clone/symlink a duplicate final.mp4 file.
  ← the-good-samaritan-trap · 2026-10-02 · "không cần tạo file video final.mp4 rồi clone ra mà hãy tạo thẳng ra file slug.mp4 luôn để khỏi phải có 2 file video"

- T015 [thumbnail · aspect] Generate only one single thumbnail that strictly matches the target video aspect ratio (out/thumbnail.jpg for 9:16 or out/thumbnail_16_9.jpg for 16:9), avoiding duplicate generation of unused aspect ratios.
  ← the-good-samaritan-trap · 2026-10-02 · "khi xác định làm video 9:16 hoặc 16:9 thì chỉ tạo ra 1 thumbnail tương ứng thôi, khỏi phải tạo 2 ảnh thumbnail"

- T016 [publishing · seo] In the final video production report, provide a dedicated "Tags" block formatted as a single comma-separated keyword list (e.g. tag1,tag2,tag3) for instant one-click copy-pasting into YouTube Studio, and append relevant hashtags directly to the end of the video description.
  ← the-good-samaritan-trap · 2026-10-02 · "thêm cho tôi ở phần báo cáo kết quả video 1 đoạn tags: là dãy keywords seo cho video phân cách nhau bởi dấu phẩy viết liền để tôi copy vào tags. hastag kèm vào cuối description luôn"

- T017 [thumbnail · safe-zone] Enforce a mandatory 10%–15% top safe margin (headroom) on vertical (9:16) cover thumbnails so that text overlay is never clipped by YouTube Shorts rounded container corners, top card margins, or mobile UI elements. The text hook must sit comfortably in the upper-third below this safe boundary, with ample dark negative space above it.
  ← the-good-samaritan-trap · 2026-10-02 · "text overlay trên thumbnail khi đăng lên youtube thì bị khất chữ ở trên"

- T018 [thumbnail · creative-diversity] Strictly avoid formulaic visual tropes and never embed concrete examples or specific case keywords (no concrete examples / no 'e.g.') into thumbnail prompts or guidance, which anchors and stifles AI creativity. Maintain brand consistency strictly through the channel's defined color palette, typography style, and visual mood (per `channels/<channel-slug>.md`); define prompt instructions purely through abstract principles of emotional conflict, atmospheric environment, and catalytic objects, empowering AI to synthesize unique imagery tailored to each narrative.
  ← the-good-samaritan-trap · 2026-10-02 · "có vẻ như các hướng dẫn chuẩn hoá đồng bộ thumbnail khiến cho các thumbnail nhìn giống quá mức rồi. 2 video mới đều có búa và người rồi có text ở trên. như vậy thì giống quá mức làm hạn chế sáng tạo của AI, đồng bộ về màu sắc phong cách thumbnail là được rồi"

- T019 [captions · lower-third] Position subtitles cleanly in the lower third of the frame above platform UI safe zones (margin_v_pct around 14%–16% for 9:16) with a refined, moderate font size (72–76pt on 9:16) and subtle outline, enabling viewers to read effortlessly without being visually distracted from or occluding the focal video imagery.
  ← global-feedback · 2026-10-02 · "Hạ vị trí và thu nhỏ phụ đề: Di chuyển phụ đề xuống 1/3 dưới cùng của màn hình và thu nhỏ kích thước của chúng. Điều này sẽ giúp người xem dễ dàng đọc phụ đề mà không bị phân tâm khỏi hình ảnh."

- T020 [visual · character-continuity] Enforce strict character visual continuity throughout each story by establishing immutable anchor traits (exact age, hairstyle/hair color, distinctive wardrobe, facial features) in the character definition and repeating these descriptive anchor tokens verbatim across every prompt where the character appears, reinforced by reference character plates.
  ← global-feedback · 2026-10-02 · "Nhất quán về hình ảnh nhân vật: Sử dụng một hình ảnh (hoặc một số hình ảnh có chung đặc điểm) để đại diện cho mỗi nhân vật trong câu chuyện. Điều này sẽ giúp người xem dễ dàng theo dõi và kết nối với câu chuyện hơn."
