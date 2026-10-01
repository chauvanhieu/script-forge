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

- T012 [channel · the-grey-verdict] Standardize and preserve "The Grey Verdict" viral production formula: high-stakes legal/institutional paradox, 4-phase narrative curve (Cognitive Shock → System Trap → Institutional Reversal → Irresolvable Fork), fast slide pacing (~2.0–2.4s per cut), Chiaroscuro Noir atmosphere, cold analytical voiceover, karaoke subtext with 40ms pre-roll, and dual-aspect high-CTR thumbnails with binary debate trigger.
  ← the-fine-print-verdict · 2026-10-01 · "video tuyệt vời"

- T013 [thumbnail · youtube-thumbnail] Strictly implement the youtube-thumbnail skill standards for high-CTR thumbnails: integrate a bold 3–5 word hook phrase (e.g. "LEGALLY DEAD") in large high-contrast typography (Verdict Amber #F5A623 or White with heavy dark stroke) placed in the upper portion away from UI elements, ensure an expressive face filling 30–50% of the frame with high emotional shock/disbelief, enforce a two-color dominant contrast (amber gold vs obsidian blue), and spotlight one dramatic secondary focal element (striking gavel or uneven scale of justice).
  ← 20261001-202515-the-living-dead-verdict · 2026-10-01 · "tôi muốn thumbnail thu hút hơn, áp dụng sát với skill @youtube-thumbnail"

