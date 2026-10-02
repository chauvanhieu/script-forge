# Signature Thumbnail Design System: The Grey Verdict

Tài liệu này định nghĩa hệ thống thiết kế ảnh Thumbnail nhận diện thương hiệu cho kênh **The Grey Verdict**. Agent trực tiếp áp dụng kiến thức từ skill `youtube-thumbnail` kết hợp với các quy chuẩn dưới đây.

---

## 1. Triết Lý Nhận Diện Thương Hiệu: Màu Sắc & Ánh Sáng (Brand Core)

Sự đồng bộ của kênh nằm ở **Bảng Màu (Color Palette)** và **Phong Cách Ánh Sáng (Lighting Mood)**, KHÔNG nằm ở việc bắt buộc có chung một đạo cụ:
1. **Nền Tối Chiaroscuro Noir:** Obsidian Black (`#0B0E14`) kết hợp Ánh Sáng Lạnh Xanh Thép (`#8E9AA8` / Ice Cyan / Midnight Rain) bao phủ không gian câu chuyện.
2. **Điểm Nhấn Phát Sáng:** Verdict Amber Gold (`#F5A623`) bao phủ viền sáng chủ thể (rim lighting), các quầng sáng định hướng (spotlight glow) và toàn bộ Text Hook.
3. **Độ Tương Phản Điện Ảnh:** Tối sâu, sáng sắc nét, chất lượng 35mm film still chân thực, tuyệt đối không dùng màu pastel hay ánh sáng phẳng.

---

## 2. Nguyên Tắc Sáng Tạo Trừu Tượng Cho Bối Cảnh & Đạo Cụ (T018)

> **NGUYÊN TẮC CỐT LÕI (RULE CHUNG): TUYỆT ĐỐI KHÔNG THÊM VÍ DỤ CỤ THỂ VÀO TRONG PROMPT**
> 
> 1. **Cấm tuyệt đối mọi ví dụ cụ thể:** Không đưa ra ví dụ cụ thể, tình huống mẫu hay từ khóa đạo cụ cố định (no concrete examples / no 'e.g.') vào trong lời nhắc hướng dẫn và prompt template.
> 2. **Chỉ sử dụng mô tả trừu tượng:** Toàn bộ chỉ dẫn phải diễn đạt bằng ngôn ngữ trừu tượng về cấu trúc mâu thuẫn, bản chất xung đột, tâm lý nhân vật và quy chuẩn mỹ học.
> 3. **AI tự do suy luận độc bản từ kịch bản:** AI đọc nội dung kịch bản (`script.md` / `story.json`) của video đang sản xuất, tự động phân tích để xác định: thực thể chịu áp lực lớn nhất, không gian khởi phát xung đột, và vật thể kích hoạt bước ngoặt, từ đó tự sinh prompt độc bản cho từng video.

1. **Thực Thể Tiêu Điểm (Focal Entity / Protagonist):** Nhân vật hoặc thực thể trực tiếp gánh chịu sức ép lớn nhất từ mâu thuẫn cốt lõi của câu chuyện. Biểu cảm và tư thế phải ở điểm bùng phát cảm xúc cao nhất (mức độ căng thẳng tâm lý, sững sờ hoặc giằng xé nội tâm tột cùng). Chiếm 35% – 45% diện tích khung hình để bảo đảm tác động thị giác ngay tức thì ở kích thước thu nhỏ 320px.
2. **Không Gian Kể Chuyện Tự Nhiên (Narrative Environment):** Bối cảnh không gian vật lý trực tiếp làm phát sinh sự kiện hoặc là nơi diễn ra nút thắt của câu chuyện. Thiết lập chiều sâu thị giác phân lớp (foreground, midground, background) với ánh sáng môi trường tạo cảm giác chân thực và kịch tính.
3. **Vật Thể Xúc Tác Xung Đột (Catalytic Element):** Bất kỳ đồ vật, văn bản hoặc dấu hiệu vật chất nào là mấu chốt kích hoạt tranh chấp hoặc đại diện cho sự phán xét mang tính bước ngoặt của câu chuyện. Được chiếu sáng bằng nguồn sáng viền hoặc phản quang để tạo điểm nhấn thị giác thứ hai sau gương mặt chủ thể.

---

## 3. Bản Đồ Vùng An Toàn & Vùng Cấm (Safety Exclusion Bounds)

* **VÙNG AN TOÀN ĐỈNH TRÊN (Top Safe Margin 10%–15% - T017):** BẮT BUỘC chừa lề trống an toàn (headroom màu tối) 10%–15% ở mép đỉnh trên cùng của ảnh 9:16. Text Hook phải được bố trí ở 1/3 phía trên nhưng TUYỆT ĐỐI KHÔNG chạm sát mép đỉnh, nhằm triệt tiêu hoàn toàn nguy cơ bị bo góc container hoặc khung card thumbnail của YouTube Shorts cắt cụt chữ ("bị khuất chữ ở trên").
* **VÙNG CẤM (Dead Zone):** **Góc dưới bên phải (Bottom-Right 20% x 20%)** BẮT BUỘC để trống hoàn toàn (chỉ có nền tối mờ hoặc không gian trống không chứa tiêu điểm). Tuyệt đối KHÔNG đặt chữ, logo, khuôn mặt hay đạo cụ quan trọng tại đây vì sẽ bị YouTube che phủ bởi biểu tượng đếm thời lượng video (`0:58` / `Shorts`).
* **VÙNG AN TOÀN SHORTS (9:16):** Nửa trên dành cho Text Hook (dưới Top Safe Margin) và Chủ thể chính. 25% phía dưới cùng để thoáng nhằm tránh bị che bởi Tiêu đề video và nút bấm giao diện của TikTok/Shorts.
* **XUẤT DUY NHẤT 1 THUMBNAIL (Single Output - T015):** Chỉ sinh DUY NHẤT 1 ảnh thumbnail theo đúng tỷ lệ của video (`out/thumbnail.jpg` cho 9:16 hoặc `out/thumbnail_16_9.jpg` cho 16:9), tuyệt đối không sinh thừa file cho tỷ lệ không dùng.

---

## 4. Khuôn Mẫu Prompt Chuẩn Hóa Cho Agent (Abstract Production Templates)

> **HƯỚNG DẪN ĐIỀN PROMPT CHO AGENT:** Tuyệt đối không chèn ví dụ mẫu hay đạo cụ có sẵn vào các placeholder bên dưới. Agent đọc kịch bản hiện tại và tự điền các mô tả trừu tượng cụ thể tương ứng với câu chuyện đó.

### Template Cho Shorts Cover (Tỷ lệ 9:16 - Mô tả Trừu tượng Hoàn toàn)
```text
A viral high-CTR vertical YouTube Shorts cover thumbnail for a documentary titled [CASE_TITLE]. 

CRITICAL TOP SAFE MARGIN: Maintain a mandatory 10% to 15% dark empty headroom at the very top edge of the frame. The typography must never touch or hug the top border, ensuring platform UI elements and rounded card containers never clip the lettering.

In the upper portion, positioned with generous headroom below the top edge, the bold hook phrase "[HOOK_TEXT_2_TO_4_WORDS]" is rendered in massive, heavy embossed golden-amber sans-serif typography (#F5A623) with a sharp black drop-shadow outline, optimized for high legibility at small mobile feed sizes.

Below the typography, occupying 35% to 45% of the frame, [FOCAL_ENTITY_SPECIFICATION: The primary subject at the climax of psychological tension, with intense facial expression and posture capturing the central dilemma].

In the surrounding environment, [STORY_SPECIFIC_ENVIRONMENT: The atmospheric physical setting directly embodying the origin or turning point of the dispute, rendered with cinematic depth and spatial storytelling].

Integrated within the scene, [CATALYTIC_ELEMENT: The tangible object or material evidence driving the narrative conflict, highlighted by subtle secondary edge illumination].

Color grading and lighting: Signature two-color dominant scheme featuring intense amber-gold (#F5A623) highlights against deep obsidian shadows and cold slate-blue undertones, rendered with dramatic Chiaroscuro noir contrast. Cinematic 35mm film still aesthetic, photorealistic 8k, bottom-right quadrant completely free of focal elements.
```

### Template Cho Video Dài / Widescreen (Tỷ lệ 16:9 - Mô tả Trừu tượng Hoàn toàn)
```text
A viral high-CTR widescreen YouTube video thumbnail for a documentary titled [CASE_TITLE].

On the left side, occupying 35% to 45% of the frame, [FOCAL_ENTITY_SPECIFICATION: The primary subject at the climax of psychological tension, with intense facial expression and posture capturing the central dilemma].

In the upper center-right, the bold hook phrase "[HOOK_TEXT_2_TO_4_WORDS]" appears in massive, thick 3D golden-yellow uppercase block typography (#F5A623) with a deep black outline and sharp rim glow, ultra-readable at thumbnail size.

Across the wider background, [STORY_SPECIFIC_ENVIRONMENT: The atmospheric physical setting directly embodying the origin or turning point of the dispute, rendered with cinematic architectural depth and spatial storytelling].

Integrated within the scene, [CATALYTIC_ELEMENT: The tangible object or material evidence driving the narrative conflict, catching directional rim lighting].

Color grading and lighting: Dominant two-color contrast of incandescent amber-gold highlights (#F5A623) against deep obsidian black and shadowy slate-blue tones, dramatic Chiaroscuro noir composition. Hyper-realistic, 8k resolution, cinematic 35mm film still, bottom-right quadrant completely clear of text, logos, or critical focal details.
```
