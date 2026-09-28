**Stack tôi chọn cho ràng buộc của bạn:**

```text
Chủ đề + nguồn kiểm chứng
        ↓
ChatGPT/Claude thủ công hoặc LLM local
        ↓
Kịch bản có cấu trúc JSON
        ↓
Kokoro local + ComfyUI/model ảnh local
        ↓
Đo thời lượng audio → dựng timeline
        ↓
FFmpeg: chuyển động ảnh + phụ đề + nhạc/SFX
        ↓
Kiểm tra tự động + duyệt bản nháp
        ↓
YouTube + đo hiệu suất
```

**Có thể đưa phí API về 0 nếu chạy model trên máy sẵn có.** Điện, phần cứng, lưu trữ và thời gian kiểm duyệt vẫn là chi phí thực.

Bốn điều cần sửa trong giả định ban đầu, theo tài liệu kiểm tra ngày **28/09/2026**:

| Giả định                                       | Thực tế                                                                                                                                |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Edge-TTS là model localhost                    | Script chạy local nhưng gọi dịch vụ TTS **online của Microsoft Edge**.                                                                 |
| XTTS-v2 miễn phí nên dùng kiếm tiền được       | Giấy phép mặc định CPML giới hạn **phi thương mại**, bao gồm đầu ra.                                                                   |
| Nano Banana API miễn phí                       | Các model ảnh Nano Banana hiện được niêm yết **không có free tier API**. Quyền dùng thử trên giao diện không tương đương API miễn phí. |
| Zoom, đổi ảnh, phụ đề giúp vượt reused content | Không có công thức hiệu ứng bảo đảm duyệt kiếm tiền. Phải có nội dung gốc và giá trị biên tập.                                         |

Nguồn: [Edge-TTS](https://github.com/rany2/edge-tts), [giấy phép XTTS-v2](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt), [giá Gemini API](https://ai.google.dev/gemini-api/docs/pricing), [chính sách YouTube](https://support.google.com/youtube/answer/1311392?hl=en).

---

**PHẦN 1 — CHỌN NGÁCH PHÙ HỢP ẢNH AI + TTS**

**1. Đừng chọn ngách chỉ từ bảng RPM trên mạng**

Không có dữ liệu công khai đáng tin cậy cho phép kết luận một kênh ảnh AI trong ngách X sẽ đạt RPM $5–20.

Tôi xếp hạng dưới đây theo ba tiêu chí chiến lược:

- Có thể truyền tải tốt bằng minh họa và lời kể.
- Có nhu cầu quốc tế và khả năng làm thành chuỗi.
- Có sản phẩm/dịch vụ liên quan để kiếm tiền ngoài quảng cáo.

**RPM $5–20 là mục tiêu cần kiểm chứng sau khi bật kiếm tiền, không phải thuộc tính bảo đảm của ngách.** Mỹ, Anh và các thị trường châu Âu cũng không có cùng mức doanh thu.

**2. Năm ngách đề xuất**

Các mốc AVD dưới đây là **mục tiêu thử nghiệm do tôi đề xuất cho video dài 8 phút**, không phải benchmark ngành hay dự báo.

| Ngách tiếng Anh                                    | Khán giả mục tiêu                                       | Cơ chế giữ chân                                               | Mục tiêu AVD thử nghiệm       | Kiếm tiền kép                                                |
| -------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| **Everyday Technology Explained**                  | 25–44 tuổi; người mua công nghệ, làm việc từ xa         | Hiện tượng quen thuộc → cơ chế bất ngờ → đánh đổi → cách chọn | 3:12–4:00, tương đương 40–50% | Ads + affiliate backup, lưu trữ, thiết bị mạng, sách/công cụ |
| **Business History & Hidden Incentives**           | 25–54 tuổi; người thích kinh doanh, kinh tế             | Nghịch lý → quyết định → hậu quả → bài học có giới hạn        | 3:12–4:24, tương đương 40–55% | Ads + sách, newsletter, case-study pack, sponsor phần mềm    |
| **Cybersecurity Stories & Digital Self-Defense**   | 25–54 tuổi; người dùng Internet, doanh nghiệp nhỏ       | Sự cố → manh mối → cơ chế → phòng tránh                       | 3:36–4:24, tương đương 45–55% | Ads + password manager, backup, security keys, checklist     |
| **Engineering History & Infrastructure Explained** | 25–54 tuổi; người thích công nghệ, lịch sử, khoa học    | Bài toán vật lý → giới hạn → phát minh → tác động             | 3:12–4:24, tương đương 40–55% | Ads + sách, khóa học đã đánh giá, poster/sơ đồ nguyên bản    |
| **Practical Philosophy for Work & Decisions**      | 25–44 tuổi; người đi làm quan tâm quyết định, thói quen | Tình huống cụ thể → hai lựa chọn → nguyên lý → ứng dụng       | 2:48–4:00, tương đương 35–50% | Ads + sách, decision journal, worksheet, sản phẩm số         |

**Ưu tiên thương mại:** công nghệ và an toàn số.  
**Ưu tiên kể chuyện bằng ảnh:** lịch sử kinh doanh và kỹ thuật.  
**Dễ làm nhưng dễ trở nên đại trà:** triết lý thực hành.

**3. Cách triển khai từng ngách**

**A. Everyday Technology Explained — khuyến nghị số 1**

Ví dụ:

- _Why Your Wi-Fi Gets Worse in the Next Room_
- _Sync Is Not a Backup_
- _What Happens to Your Files When a Cloud Service Shuts Down?_

Visual: căn nhà cắt lớp, sơ đồ dữ liệu, thiết bị minh họa, chuỗi sự kiện. Có thể hoàn toàn không quay phim.

**Lợi thế:** chủ đề gắn với quyết định mua hàng.  
**Giới hạn:** ảnh AI chỉ minh họa. Thông số, biểu đồ và kết luận sản phẩm phải lấy từ nguồn thật. Không gọi video là “hands-on review” nếu chưa dùng sản phẩm.

**B. Business History & Hidden Incentives**

Ví dụ:

- _Why Some Companies Want You to Subscribe_
- _How a Simple Container Changed Global Trade_

Visual: bối cảnh tái hiện, timeline, sơ đồ dòng hàng và cơ chế doanh thu.

**Điểm giữ chân:** giải đáp “tại sao điều tưởng vô lý lại có lợi cho doanh nghiệp?”.  
**Giới hạn:** phải nghiên cứu kỹ; không dựng phát ngôn, tài liệu hay số liệu giả.

**C. Cybersecurity Stories**

Ví dụ:

- _How One Reused Password Can Expose Several Accounts_
- _Why Account Recovery Can Become the Weakest Link_

Visual: tình huống giả lập, đường đi của thông tin, sơ đồ tài khoản.

**Điểm giữ chân:** người xem lần theo nguyên nhân.  
**Giới hạn:** phân biệt rõ sự kiện thật và ví dụ minh họa; không gieo sợ hãi để bán VPN hoặc phần mềm.

**D. Engineering History**

Ví dụ:

- _Why Old Cities Were Built Around Water_
- _The Engineering Problem Behind Long Suspension Bridges_

Visual: tái hiện công trình, bản đồ tự dựng, mặt cắt kỹ thuật.

**Điểm giữ chân:** mỗi phần giải quyết một ràng buộc mới.  
**Giới hạn:** AI thường vẽ sai cơ cấu, tỷ lệ và hình học. Đồ thị, bản đồ, sơ đồ chịu lực phải được kiểm tra.

**E. Practical Philosophy**

Ví dụ:

- _A Stoic Way to Handle Criticism at Work_
- _When Persistence Becomes a Bad Decision_

Visual: tình huống đời thường và hình ẩn dụ; không cần duy trì gương mặt nhân vật qua nhiều cảnh.

**Điểm giữ chân:** lựa chọn có hậu quả cụ thể.  
**Giới hạn:** tránh “10 quotes that will change your life”, trích dẫn bịa và đọc lại bản dịch sách có bản quyền.

**Tại sao không ưu tiên True Crime hoặc Sci-Fi Lore?**

- **True Crime:** có thể hấp dẫn, nhưng bạo lực, bi kịch và nội dung nhạy cảm làm tăng rủi ro hạn chế quảng cáo. Không phải lựa chọn đơn giản để tối ưu doanh thu bền vững. [Hướng dẫn advertiser-friendly](https://support.google.com/youtube/answer/6162278?hl=en).
- **Sci-fi nguyên bản:** rất hợp ảnh AI và dễ xây tài sản trí tuệ riêng, nhưng khả năng gắn affiliate thương mại thường yếu hơn công nghệ.
- **Lore của thương hiệu có sẵn:** không đồng nghĩa được tự do dùng nhân vật, nhạc, hình và cốt truyện của thương hiệu đó.

**Định vị kênh đề xuất:**

> **“Illustrated explanations of everyday technology, digital risks, and smarter tech decisions.”**

Chọn một trụ cột hẹp trong định vị này cho 5 video đầu.

---

**PHẦN 2 — THIẾT LẬP TECH STACK FREE/LOCAL**

**1. Stack tối thiểu**

| Lớp                   | Lựa chọn chính                                   | Vai trò                                           |
| --------------------- | ------------------------------------------------ | ------------------------------------------------- |
| Lập kế hoạch/kịch bản | ChatGPT/Claude dùng thủ công; sau này LLM local  | Tạo kịch bản có cấu trúc                          |
| LLM local             | Ví dụ Qwen3-8B qua runtime tương thích           | Sinh nháp/JSON; cần kiểm tra tiếng Anh và sự thật |
| TTS                   | **Kokoro-82M**                                   | Voice tiếng Anh local                             |
| TTS dự phòng          | **Piper**, sau khi kiểm tra model card của giọng | Chạy trên máy hạn chế tài nguyên                  |
| Sinh ảnh              | **ComfyUI + SDXL Base**                          | API sinh ảnh trên máy                             |
| Model ảnh thay thế    | **FLUX.1-schnell**, nếu máy phù hợp              | Sinh ảnh theo giấy phép của model cụ thể          |
| Điều phối             | **Python**                                       | JSON, gọi TTS, hàng đợi ảnh, cache, gọi FFmpeg    |
| Render                | **FFmpeg + ffprobe**                             | Video, âm thanh, phụ đề, kiểm tra duration        |
| Caption nâng cao      | Whisper hoặc công cụ alignment local             | Căn thời gian từ/cụm từ                           |
| Nhạc/SFX              | Thư viện đã tải, có quyền thương mại             | Tra cứu bằng ID cố định                           |

Qwen3-8B và FLUX.1-schnell công bố giấy phép Apache-2.0; SDXL Base dùng OpenRAIL++ với điều kiện sử dụng riêng. Không áp dụng giấy phép của model gốc cho mọi checkpoint hoặc LoRA tải thêm. [Qwen](https://huggingface.co/Qwen/Qwen3-8B), [FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell), [SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0).

**Khuyến nghị triển khai:** một tiến trình Python, một thư mục cho mỗi video. Chưa cần Docker, Redis, database, n8n hay nhiều agent.

**Phần cứng là biến số chưa biết:** trước khi chọn model ảnh, benchmark 10 ảnh và 60 giây TTS trên máy thực tế. Nếu chỉ có CPU, phí API vẫn có thể bằng 0 nhưng thời gian sinh ảnh có thể không đáp ứng lịch sản xuất. Chạy LLM, TTS và model ảnh lần lượt để tránh tranh bộ nhớ.

**2. Chọn TTS**

| Công cụ        | Offline sau khi tải model? | Quyền thương mại                                              | Quyết định                         |
| -------------- | -------------------------- | ------------------------------------------------------------- | ---------------------------------- |
| **Kokoro-82M** | Có                         | Model công bố Apache-2.0                                      | Chọn làm lõi                       |
| **Piper**      | Có                         | Kiểm tra từng voice model; engine và voice có giấy phép riêng | Dự phòng                           |
| **Edge-TTS**   | Không                      | Không suy ra quyền dùng dịch vụ từ giấy phép thư viện         | Không lấy làm lõi offline          |
| **XTTS-v2**    | Có                         | CPML mặc định phi thương mại                                  | Loại khỏi stack kiếm tiền miễn phí |

Nguồn: [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [Piper voices](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md).

**Cấu hình khởi đầu cho Kokoro**

- Thử `af_heart` cho US; chọn giọng UK từ danh sách chính thức nếu muốn UK.
- Giữ một giọng kể cố định.
- `speed` bắt đầu ở **0.95–1.0**, điều chỉnh sau khi nghe.
- Mỗi dòng thường **12–22 từ**, diễn đạt một ý hoàn chỉnh.
- Dùng dấu câu và câu văn để điều khiển nhịp.
- Chèn khoảng nghỉ ngắn bằng timeline; không nhét `[breath]`, `[sad]` vào text nếu engine không hỗ trợ.
- Giữ audio gốc ở sample rate của model; chỉ resample ở công đoạn mix cuối.

API mẫu của Kokoro hỗ trợ lựa chọn giọng và tốc độ; ví dụ chính thức xuất audio 24 kHz. [Tài liệu Kokoro](https://github.com/hexgrad/kokoro).

**Để có cảm xúc:** viết tình huống, động từ và điểm nhấn tốt; giữ tương phản giữa câu ngắn và câu dài. Thay đổi tốc độ ngẫu nhiên hoặc thêm tiếng thở giả vào mọi câu thường làm giọng kém tự nhiên.

Không có model nào bảo đảm “không bị nhận ra là AI”, và đó không phải điều kiện kỹ thuật để được kiếm tiền.

**3. Sinh ảnh: phân biệt Nano, Banana và công cụ điều phối**

- **Gemini Nano:** dòng model phục vụ tác vụ trên thiết bị; không phải tên chung của API sinh ảnh. [Android Developers](https://developer.android.com/ai/gemini-nano).
- **Nano Banana:** tên cho khả năng sinh ảnh Gemini. API ảnh hiện có tính phí.
- **Codex:** có thể hỗ trợ viết script và điều phối công cụ được cấp quyền; không phải nguồn GPU sinh ảnh offline miễn phí.

Ví dụ hiện tại, Nano Banana 2 Lite niêm yết khoảng **$0.0336/ảnh 1K**, hoặc **$0.0168 qua Batch**, chưa cộng các chi phí liên quan. Với 80 ảnh: khoảng **$2.69** hoặc **$1.34** tiền đầu ra ảnh, trước tạo lại. Vì vậy, đường đi thật sự không mất phí API là model local. [Bảng giá Google](https://ai.google.dev/gemini-api/docs/pricing).

**4. Giữ visual consistency**

Tạo một `style_bible` cố định:

```text
Medium: editorial technical illustration
Palette: navy, muted teal, warm amber
Lighting: soft directional light
Composition: one dominant subject, uncluttered background
Aspect ratio: 16:9
Detail: readable silhouettes, restrained textures
Typography: added later by renderer
Avoid: photorealistic evidence, logos, watermarks, generated text
```

Công thức prompt:

```text
[STYLE]
+ [SUBJECT / CHARACTER SPECIFICATION]
+ [ACTION]
+ [SETTING / PERIOD]
+ [SHOT SIZE / CAMERA ANGLE]
+ [LIGHT]
+ [CONTINUITY DETAILS]
+ [EXCLUSIONS]
```

**Đồng bộ thực tế cần:**

- Giữ model, checkpoint, workflow và style.
- Lưu seed để tái tạo cảnh; **cùng seed không bảo đảm cùng nhân vật**.
- Nếu model/workflow hỗ trợ, dùng ảnh tham chiếu cho nhân vật hoặc vật thể lặp lại.
- Ưu tiên vật thể, cảnh quan và sơ đồ nếu muốn giảm chi phí kiểm tra gương mặt.
- Vẽ chữ, số, mũi tên và biểu đồ bằng renderer, không giao AI vẽ dữ liệu chính xác.

ComfyUI có mẫu API để gửi workflow từ Python; có thể xuất workflow ở định dạng API rồi thay prompt và seed. [Ví dụ chính thức](https://github.com/Comfy-Org/ComfyUI/blob/master/script_examples/basic_api_example.py).

**5. FFmpeg, MoviePy hay CapCut?**

| Công cụ     | Khi dùng                                                               |
| ----------- | ---------------------------------------------------------------------- |
| **FFmpeg**  | Lõi render ổn định, chạy không giao diện, dễ xử lý theo batch          |
| **MoviePy** | Khi cần thao tác timeline bằng Python và chấp nhận thêm dependency     |
| **CapCut**  | Chỉnh tay bản nháp; không lấy làm phụ thuộc bắt buộc của pipeline free |

Nếu chọn MoviePy, dùng tài liệu đúng phiên bản: v2 có thay đổi API so với các tutorial v1. [Hướng dẫn chuyển sang MoviePy v2](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html).

CapCut có tính năng auto-caption/AI thuộc Pro; không mặc định mọi bản cài đều xuất được miễn phí. [Giải thích của CapCut](https://www.capcut.com/help/capcut-pro-prompt-standard-user).

---

**PHẦN 3 — SOP 6 BƯỚC**

**Bước 1 — Ý tưởng → title → thumbnail → nguồn**

**Đầu vào:** một câu hỏi cụ thể của khán giả.

**Thực hiện:**

1. Tìm kiếm bằng tiếng Anh trên YouTube.
2. Xem Google Trends ở chế độ YouTube Search, theo từng thị trường.
3. Đọc khoảng 10 video liên quan và bình luận.
4. Tìm phần giải thích còn thiếu.
5. Chốt một lời hứa có thể giải đáp trong 6–9 phút.
6. Thu thập nguồn gốc: tài liệu kỹ thuật, nghiên cứu, bảo tàng, báo cáo hoặc trang hãng.

**Ví dụ:**

```text
Topic: Sync versus backup

Viewer question:
If my files are in the cloud, why could I still lose them?

Title concept:
Sync Is Not a Backup

Thumbnail:
Two illustrated folders connected by arrows;
one deletion symbol affects both.
Text added later: "BOTH GONE?"

Original contribution:
Explain three failure scenarios with a clear decision diagram.
```

**Đầu ra:** brief, danh sách nguồn, 5 title nháp, concept thumbnail.

**Điều kiện qua bước:** có đóng góp biên tập rõ ràng. “Đọc lại ba bài viết” không phải đóng góp đủ tốt.

---

**Bước 2 — Script line-by-line**

Khung kể chuyện:

```text
Hook → Problem → Mechanism → Complication → Resolution → CTA
```

| Phần                | Mục đích                                           |
| ------------------- | -------------------------------------------------- |
| Hook, khoảng 3 giây | Nêu nghịch lý hoặc hậu quả                         |
| 3–25 giây           | Xác nhận vấn đề và lời hứa                         |
| Phần giữa           | Giải thích bằng ví dụ, nguyên nhân và hệ quả       |
| Complication        | Chỉ ra trường hợp mà câu trả lời đơn giản không đủ |
| Resolution          | Cho người xem mô hình hiểu hoặc cách quyết định    |
| CTA                 | Một bước tiếp theo liên quan                       |

Hook mẫu:

> “Sync can copy your mistakes.”

Câu tiếp:

> “Delete a file on one device, and that deletion may follow it to the others.”

Sau đó giải thích điều kiện, version history và cơ chế khôi phục theo dịch vụ thực tế; tránh kết luận quá rộng.

**Quy chuẩn:**

- Khoảng **950–1.150 từ** cho một video nhắm 7–9 phút, tùy nhịp đọc.
- Mỗi dòng có ID và một ý trực quan.
- Thường 12–22 từ/dòng; hook có thể ngắn hơn.
- Một đoạn không được tồn tại chỉ để kéo dài thời lượng.
- Trích dẫn trực tiếp phải xác minh; lời diễn giải phải được viết lại bằng lập luận riêng.

**Hợp đồng dữ liệu của một dòng:**

```json
{
  "id": "L001",
  "section": "hook",
  "narration": "Sync can copy your mistakes.",
  "claim_ids": ["C001"],
  "visual_prompt": "Editorial technical illustration, two identical blue file folders on separate devices, a deletion symbol propagating between them, dark navy background, amber accent, one clear focal point, 16:9, no text, no logos.",
  "visual_kind": "conceptual",
  "on_screen_text": "SYNC ≠ BACKUP",
  "motion": "slow_push",
  "pause_after_ms": 200,
  "sfx_query": "soft digital click",
  "bgm_cue": "tension_low"
}
```

Đây là cấu trúc đề xuất, chưa phải dữ liệu đã render hoặc nguồn đã kiểm chứng.

---

**Bước 3 — TTS → audio thật → timing**

**Thứ tự bắt buộc:**

1. Làm sạch text cho TTS.
2. Tạo WAV theo từng ID.
3. Nghe và tạo lại các câu lỗi.
4. Chuẩn hóa format để ghép.
5. Đo duration của file thật.
6. Xây timeline từ duration đo được.

**Không dùng timestamp do LLM đoán làm timeline cuối.**

Ví dụ cấu trúc tài sản:

```text
audio/L001.wav
images/L001.png
clips/L001.mp4
```

Công thức:

```text
slot_duration = measured_audio_duration + pause_after
next_start = current_start + slot_duration
```

Sau đó chuyển mốc thời gian sang frame ở FPS cố định; tránh làm tròn từng clip theo cách khiến sai lệch tích lũy.

Có thể lấy duration bằng `ffprobe`; công cụ hỗ trợ đầu ra JSON. [Tài liệu ffprobe](https://ffmpeg.org/ffprobe.html).

**Khử tiếng ồn**

TTS sạch thường không cần denoise. Nếu có lỗi âm thanh, ưu tiên tạo lại câu đó; lọc mạnh có thể làm giọng méo.

**BGM/SFX**

- Dùng thư viện tải sẵn có giấy phép.
- LLM chỉ xuất mood hoặc từ khóa.
- Pipeline ánh xạ sang asset ID trong thư viện đã duyệt.
- Không cho LLM tự bịa URL nhạc hoặc kết luận “royalty-free”.

YouTube Audio Library cho phép kiếm tiền với nhạc/SFX của thư viện; một số track cần ghi công. [Hướng dẫn Audio Library](https://support.google.com/youtube/answer/3376882?hl=en).

---

**Bước 4 — Batch sinh ảnh theo dòng**

Mỗi dòng thoại có **một visual prompt đầy đủ**, đúng yêu cầu của bạn.

Quy trình:

1. Sinh 6 ảnh thử đại diện: cận, trung, toàn; sáng, tối; nhân vật/vật thể.
2. Kiểm tra style.
3. Khóa workflow.
4. Sinh batch còn lại theo ID.
5. Tạo contact sheet để duyệt nhanh toàn bộ.
6. Chỉ tạo lại ảnh lỗi.

**Lưu cho từng ảnh:**

```text
line_id
prompt
model/checkpoint version
workflow version
seed
image path
license reference
review status
```

**Giới hạn số lần thử:** ví dụ tối đa 2 lần tạo lại tự động; sau đó chuyển trạng thái cần kiểm tra. Không để vòng lặp sửa ảnh tiêu tốn tài nguyên vô hạn.

**Quan trọng về chi phí:** video 8 phút nếu thay ảnh mới mỗi 3 giây cần khoảng **160 ảnh**. Nếu một dòng 15 từ ở 150 từ/phút, mỗi dòng khoảng 6 giây; cùng thời lượng chỉ cần khoảng **80 ảnh**.

Vì thế, dùng chuyển động/crop trong cảnh để tạo nhịp khi phù hợp; không cần sinh ảnh mới mỗi 2–3 giây.

---

**Bước 5 — Render tự động**

**Cấu hình khởi đầu**

| Thành phần      | Thiết lập đề xuất                                          |
| --------------- | ---------------------------------------------------------- |
| Video           | 1920×1080, 30 fps, 16:9                                    |
| Encode          | H.264, pixel format yuv420p                                |
| Audio cuối      | AAC, 48 kHz                                                |
| Chuyển động ảnh | Zoom khoảng 1.00 → 1.06–1.10 trong một cảnh                |
| Chuyển cảnh     | Hard cut mặc định; dissolve ngắn khi có lý do              |
| Phụ đề          | 1–2 dòng, tương phản cao, không che phần giải thích        |
| Mix             | Tham khảo −16 đến −14 LUFS integrated, true peak ≤ −1 dBTP |

Các thông số này là preset kỹ thuật để bắt đầu, không phải yêu cầu bật kiếm tiền.

**Ánh xạ tác vụ sang FFmpeg**

| Tác vụ                 | Thành phần                                 |
| ---------------------- | ------------------------------------------ |
| Ken Burns              | `zoompan`                                  |
| Chuẩn kích thước/tỷ lệ | `scale`, `crop`, `setsar`                  |
| Phụ đề                 | `subtitles`/`ass`, cần build hỗ trợ libass |
| Chuyển cảnh            | `xfade`                                    |
| Ghép âm                | `amix`                                     |
| Hạ nhạc dưới lời       | `sidechaincompress` hoặc automation volume |
| Chuẩn loudness         | `loudnorm`, nên đo hai lượt cho bản cuối   |

[Tài liệu bộ lọc FFmpeg](https://www.ffmpeg.org/ffmpeg-filters.html).

**Bẫy đồng bộ cần xử lý**

`xfade` làm các clip chồng thời gian lên nhau. Nếu chỉ ghép các clip có độ dài bằng audio rồi thêm crossfade, video sẽ ngắn dần so với lời đọc.

Bản đầu nên dùng **hard cut** để giữ timing chính xác. Khi thêm dissolve, tạo phần hình dư và đặt overlap quanh mốc chuyển cảnh, giữ nguyên timeline lời đọc.

**Phụ đề tự động**

- Bản đơn giản: dùng chính `narration` và thời gian của từng WAV để tạo caption theo dòng.
- Bản karaoke/nhấn từng từ: cần timestamp từ audio hoặc forced alignment.
- Không chia đều duration theo số từ rồi coi là căn thời gian chính xác.
- Với câu dài, chia caption theo cụm nghĩa; không thu nhỏ chữ để nhét toàn bộ câu.

**Pacing**

- 2–3 giây thích hợp cho một số hook hoặc đoạn montage.
- Cảnh giải thích có thể 5–8 giây.
- Sơ đồ cần giữ đủ lâu để đọc.
- Mỗi chuyển động phải giúp theo dõi ý; không dùng zoom ngẫu nhiên để “đánh lừa bộ quét”.

**Kiểm tra trước xuất bản**

```text
Có đủ audio/image cho mọi line ID?
Có file hỏng hoặc duration bằng 0?
Caption có vượt khỏi timeline?
Có mất câu cuối hoặc khoảng im lặng bất thường?
Ảnh có sai dữ kiện hoặc lỗi nghiêm trọng?
Nguồn và giấy phép đã đủ?
Video cuối có khớp title/thumbnail?
```

---

**Bước 6 — SEO, upload và đo lại**

**Metadata tiếng Anh**

- Title: một lời hứa cụ thể.
- Description: hai dòng đầu giải thích video trả lời gì.
- Sources: nguồn quan trọng và ngày kiểm tra khi cần.
- Chapters: sinh lại từ timeline đã render.
- Tags: một ít từ liên quan, tên riêng, cách viết sai thường gặp.
- Thumbnail: một ý, 0–4 từ, chữ thêm bằng renderer.

**Giờ đăng thử nghiệm**

| Lịch thử | Miền Đông Mỹ | Miền Tây Mỹ | Việt Nam khi Mỹ dùng EDT/PDT | Việt Nam khi Mỹ dùng EST/PST |
| -------- | ------------ | ----------- | ---------------------------- | ---------------------------- |
| A        | 12:00 ET     | 09:00 PT    | 23:00 cùng ngày              | 00:00 hôm sau                |
| B        | 18:00 ET     | 15:00 PT    | 05:00 hôm sau                | 06:00 hôm sau                |

Trong script, dùng timezone **`America/New_York`** hoặc **`America/Los_Angeles`**, không hard-code offset quanh năm.

Không có “giờ vàng” bảo đảm tăng trưởng. YouTube nói thời điểm đăng không được biết là yếu tố quyết định hiệu suất dài hạn của video thông thường; tags cũng có vai trò nhỏ. [FAQ YouTube](https://support.google.com/youtube/answer/141805?hl=en).

**Vòng phản hồi**

| Kết quả                                   | Hành động                                 |
| ----------------------------------------- | ----------------------------------------- |
| Người xem click nhưng bỏ ngay             | Sửa hook, âm thanh hoặc độ khớp lời hứa   |
| Rơi ở đoạn dài                            | Cắt ý lặp, thêm hình giải thích đúng chỗ  |
| Xem khá lâu nhưng không xem tiếp          | Xây video tiếp nối sát vấn đề             |
| Thumbnail thử nghiệm không có kết luận rõ | Giữ lựa chọn hợp lý, đợi thêm dữ liệu     |
| Viewer đúng nhu cầu nhưng affiliate yếu   | Kiểm tra sản phẩm, quốc gia và vị trí CTA |

So sánh video cùng độ dài, tuổi và nguồn traffic; không áp một mốc CTR/AVD cho mọi tình huống.

---

**PHẦN 4 — MASTER INPUT TEMPLATE PROMPT**

Prompt dưới đây tạo **kịch bản đầy đủ và dữ liệu có thể đưa vào pipeline**. Bạn thay `[Topic/Ý tưởng]`. Mặc định dùng ngách công nghệ giải thích; sửa phần định vị một lần nếu chọn ngách khác.

```text
You are an English-language documentary writer and a production-data
designer for an illustrated, faceless YouTube channel.

TOPIC: [Topic/Ý tưởng]

CHANNEL DEFAULTS
- Audience: English-speaking adults, primarily in the US, UK,
  Canada and Europe.
- Positioning: clear explanations of everyday technology,
  digital risks and smarter technology decisions.
- Format: original narration + AI illustrations + original diagrams
  + licensed music and sound effects.
- No filming, no presenter and no self-recorded voice.
- Narration engine: local Kokoro.
- Image generation: local model or an explicitly authorized API.
- Rendering: Python orchestration and FFmpeg.
- Target: approximately 7–9 minutes, 950–1,150 spoken words.
  Shorten the video if the topic cannot sustain that length.
- Language: natural, conversational American English.
- Budget: zero paid API usage by default.

EDITORIAL RULES
1. Answer one specific viewer question.
2. Use a concrete hook in the first approximately three seconds.
3. Structure the story as:
   Hook → Problem → Mechanism → Complication → Resolution → CTA.
4. Add an original explanation, comparison, causal model or interpretation.
5. Avoid generic motivational language, recycled listicles, fake suspense,
   sensational claims and repetitive chapter openings.
6. Never invent personal experience, tests, quotations, statistics,
   credentials, customer stories or product performance.
7. Label hypothetical examples and reconstructions clearly.
8. Do not use an invented expert persona.
9. Do not promise monetization, RPM, CTR or algorithmic distribution.

RESEARCH RULES
- If browsing is available, verify material factual claims using primary
  sources and include real URLs and dates checked.
- Distinguish source facts from editorial interpretations.
- If browsing is unavailable, do not fabricate verification or URLs.
  Mark unresolved claims as "unverified".
- Use null for unknown values.
- Do not put unverified numerical claims in titles or thumbnails.
- For fiction, identify it as original fiction and maintain internal
  continuity instead of inventing factual citations.
- Unresolved material claims must appear in publication_blockers.

SCRIPT AND TTS RULES
- Write the complete spoken script, not an outline or sample.
- Split it into ordered narration lines.
- Use IDs L001, L002 and so on.
- Most lines should contain 12–22 words and one clear idea.
  Hooks and occasional emphasis lines may be shorter.
- Every line must have exactly one complete visual_prompt.
- Keep stage directions and source citations out of spoken narration.
- Use contractions, natural sentence variation and pronounceable wording.
- Do not insert unsupported emotion or breathing tags into narration.
- Give pronunciation substitutions separately.
- Do not invent final timestamps. Audio duration will be measured
  after synthesis.

VISUAL RULES
- Define one coherent style_bible before writing the scene prompts.
- Default style: editorial technical illustration, navy and muted teal
  with warm amber accents, readable silhouettes, uncluttered composition.
- Every visual_prompt must be self-contained and repeat essential
  style and continuity details.
- Include subject, action, setting, framing, lighting and exclusions.
- Use 16:9 composition and leave safe space for captions where appropriate.
- Avoid generated text, logos, fake documents and fake evidence.
- Supply exact on_screen_text separately for the renderer.
- For factual diagrams, provide verified labels/data separately;
  do not rely on an image model to draw them accurately.
- Repeated characters or objects must retain their defined appearance.
- A seed alone must not be treated as an identity guarantee.
- AI illustrations must not imply that fictional scenes were recorded
  in the real world.

AUDIO AND EDIT RULES
- Suggest SFX search terms, not invented filenames or license claims.
- Use SFX only when they support an event or transition.
- Define a small number of BGM cues with mood and energy.
- Do not recommend recognizable copyrighted music.
- Select motion from:
  "static", "slow_push", "slow_pull", "pan_left", "pan_right".
- Use subtle motion. Do not force a new image every two seconds.
- Provide pause_after_ms as an editorial suggestion, not measured timing.
- Keep music and asset selection pending until matched to a licensed library.

RETURN ONE VALID JSON OBJECT, WITHOUT MARKDOWN, USING THIS STRUCTURE:

{
  "schema_version": "1.0",
  "topic": "string",
  "viewer": "string",
  "central_question": "string",
  "promise": "string",
  "original_contribution": "string",
  "content_type": "factual_explainer",
  "estimated_word_count": 0,
  "style_bible": {
    "medium": "string",
    "palette": ["string"],
    "lighting": "string",
    "composition": "string",
    "continuity": ["string"],
    "exclusions": ["string"]
  },
  "sources": [
    {
      "id": "S001",
      "title": "string",
      "url": null,
      "checked_on": null
    }
  ],
  "claims": [
    {
      "id": "C001",
      "text": "string",
      "source_ids": [],
      "status": "verified_or_unverified_or_interpretation",
      "limitations": "string"
    }
  ],
  "pronunciation": [
    {
      "written": "string",
      "tts_substitution": "string"
    }
  ],
  "bgm_cues": [
    {
      "id": "B001",
      "mood": "string",
      "energy": "low_or_medium",
      "search_terms": ["string"]
    }
  ],
  "lines": [
    {
      "id": "L001",
      "section": "hook",
      "narration": "Full spoken line",
      "claim_ids": [],
      "visual_kind": "conceptual",
      "visual_prompt": "Complete self-contained image prompt",
      "on_screen_text": "",
      "diagram_data": null,
      "motion": "slow_push",
      "pause_after_ms": 200,
      "sfx_query": null,
      "bgm_cue": "B001",
      "disclosure_note": null
    }
  ],
  "metadata": {
    "titles": ["Exactly five accurate title options"],
    "recommended_title_index": 0,
    "description": "Complete English description",
    "tags": ["5–10 relevant tags"],
    "chapter_starts": [
      {
        "label": "string",
        "line_id": "L001"
      }
    ],
    "thumbnail_concepts": [
      {
        "concept": "string",
        "text_overlay": "0–4 words",
        "image_prompt": "Complete thumbnail image prompt"
      }
    ],
    "affiliate_disclosure": null,
    "ai_disclosure_review": "Specific assessment and uncertainties"
  },
  "publication_blockers": [],
  "human_review_tasks": [],
  "completion": {
    "complete": true,
    "last_line_id": "string"
  }
}

OUTPUT REQUIREMENTS
- Expand lines to include the entire script.
- Produce exactly five distinct title options and three thumbnail concepts.
- Metadata must match the delivered story.
- Do not invent links, sponsors, affiliate relationships or available downloads.
- Use empty arrays rather than fabricated sources.
- The example strings describe field requirements; replace them with content.
- If the full script cannot fit in the response, return a valid JSON object
  with completion.complete set to false and clearly identify where to resume.
- Never silently truncate the script or label an incomplete package complete.
```

**Ba kiểm tra bắt buộc khi pipeline đọc JSON:**

1. Parse được; ID duy nhất; mọi `claim_id`, `source_id`, `bgm_cue` tham chiếu hợp lệ.
2. Mỗi dòng có thoại và prompt; không có file thiếu; chỉ chấp nhận các motion đã cho phép.
3. `completion.complete = true` và không còn blocker nghiêm trọng trước khi phát hành.

Không chạy mã hoặc shell command lấy từ output LLM. Pipeline tự xây lệnh FFmpeg từ trường dữ liệu đã kiểm tra.

---

**PHẦN 5 — KIẾM TIỀN BỀN VỮNG VÀ ĐÚNG TỆP KHÁN GIẢ**

**1. Ba quy tắc thay cho “lách bộ quét”**

**Quy tắc 1: Nội dung riêng phải tồn tại trong kịch bản và lập luận.**

Ảnh mới, giọng mới và hiệu ứng mới không cứu được một bài đọc lại nội dung có sẵn. Mỗi video cần câu hỏi, cách giải thích và kết luận riêng.

**Quy tắc 2: Dùng template sản xuất, không nhân bản nội dung.**

Giữ JSON schema, font và preset âm thanh. Thay đổi thực chất tình huống, bằng chứng, diễn biến và điều người xem học được. Chính sách hiện hành nêu rõ nội dung theo khuôn mẫu thiếu giá trị và các video có thể thay thế cho nhau là vấn đề kiếm tiền. [Chính sách YouTube](https://support.google.com/youtube/answer/1311392?hl=en).

**Quy tắc 3: Tách quyền sử dụng, tính xác thực và khai báo AI thành các kiểm tra riêng.**

Lưu model card, license, nguồn dữ kiện và bản dựng. Tái hiện chân thực có thể cần khai báo AI; không xóa watermark hoặc metadata để che nguồn gốc. YouTube nói khai báo AI tự nó không làm mất điều kiện kiếm tiền. [Hướng dẫn AI use](https://support.google.com/youtube/answer/14328491?hl=en).

**Không có ba thủ thuật kỹ thuật nào bảo đảm bật kiếm tiền 100%.**

**2. Định hướng khán giả Mỹ/Anh trong 3–5 video đầu**

Điều bạn kiểm soát được là **tín hiệu về nội dung và người xem phù hợp**, không phải quốc gia phân phối bắt buộc.

Làm năm video cùng một cụm:

| Video | Ý tưởng                                              |
| ----- | ---------------------------------------------------- |
| 1     | _Sync Is Not a Backup_                               |
| 2     | _What Happens When You Delete a Cloud File?_         |
| 3     | _Why an External Drive Is Not the Whole Backup Plan_ |
| 4     | _The Difference Between Backup and Version History_  |
| 5     | _A Simple Way to Think About Protecting Your Files_  |

Mỗi tập cần phân biệt rõ phạm vi và có nguồn; tránh năm bản kể lại cùng một ý.

Thiết lập:

- Tiếng Anh nhất quán ở narration, title, thumbnail và captions.
- Ví dụ sản phẩm/dịch vụ có mặt ở thị trường mục tiêu.
- Giá và điều kiện ghi đúng quốc gia nếu đề cập.
- Một giọng kể, một phong cách hình ảnh, một lời hứa kênh.
- End screen nối sang câu hỏi tiếp theo.
- Chia sẻ ở cộng đồng phù hợp khi được phép, không spam.
- Không mua view, trao đổi sub hoặc ép người không quan tâm xem video.

Không cần đổi vị trí kênh sang Mỹ hoặc dùng VPN để “huấn luyện thuật toán”; YouTube nói vị trí kênh không dùng để quyết định đề xuất. [FAQ phân phối](https://support.google.com/youtube/answer/141805?hl=en).

**Sau 3–5 video:** xem geography, nguồn traffic, retention và lượt xem tiếp; coi đây là tín hiệu ban đầu. Chưa đủ dữ liệu không đồng nghĩa chọn sai quốc gia hoặc sai ngách.

**3. Thiết kế vận hành gần 0 đồng**

```text
Một video = một manifest + các tài sản theo ID.

Cache theo nội dung và cấu hình.
Sửa một câu → chỉ tạo lại câu đó và phần phụ thuộc.
Sửa một ảnh → chỉ render lại clip liên quan.
Lỗi giữa chừng → tiếp tục từ bước đã hoàn thành.
Hết quota → dừng hoặc chuyển sang local, không tự bật tính phí.
```

Cache phải gồm phiên bản model, giọng, tốc độ, prompt và workflow; chỉ kiểm tra “file đã tồn tại” là chưa đủ.

**Thứ tự xây hệ thống hợp lý:**

1. Làm một video hoàn chỉnh bằng các công cụ đã chọn.
2. Chốt JSON và quy tắc đặt ID.
3. Tự động hóa TTS, sinh ảnh và render.
4. Thêm cache, kiểm tra duration và khả năng chạy tiếp.
5. Chỉ thêm upload tự động sau khi bản nháp đầu ra đã ổn định.

**Cấu hình khởi đầu nên chốt:** một kênh _Everyday Technology Explained_, Kokoro + ComfyUI/SDXL + Python/FFmpeg, video 6–9 phút, khoảng 60–90 dòng/ảnh, một video mỗi tuần. Đây là phạm vi đủ nhỏ để kiểm tra chất lượng, thời gian máy chạy và phản ứng khán giả trước khi tăng sản lượng.
