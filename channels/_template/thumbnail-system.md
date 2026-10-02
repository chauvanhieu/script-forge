# Signature Thumbnail Design System: [CHANNEL_NAME]

Tài liệu này định nghĩa hệ thống thiết kế thumbnail chuẩn CTR cao riêng biệt cho kênh **[CHANNEL_NAME]**.

---

## 1. Triết Lý Nhận Diện Thương Hiệu: Màu Sắc & Ánh Sáng

Sự đồng bộ của kênh nằm ở **Bảng Màu (Color Palette)** và **Phong Cách Ánh Sáng (Lighting Mood)**, KHÔNG nằm ở việc bắt buộc có chung một đạo cụ:
1. **Bảng màu chủ đạo:** [Màu tương phản cao theo style-bible]
2. **Typography Text Hook:** 2–4 từ in hoa cỡ đại màu `#[ACCENT_HEX]` với viền đen dày, đặt ở 1/3 phía trên khung hình.

---

## 2. Nguyên Tắc Sáng Tạo Trừu Tượng Cho Bối Cảnh & Đạo Cụ (T018)

> **NGUYÊN TẮC CỐT LÕI (RULE CHUNG): TUYỆT ĐỐI KHÔNG THÊM VÍ DỤ CỤ THỂ VÀO TRONG PROMPT**
> 
> 1. Cấm tuyệt đối mọi ví dụ cụ thể trong prompt sinh ảnh thumbnail (no concrete examples / no 'e.g.').
> 2. Diễn đạt bằng ngôn ngữ trừu tượng về cấu trúc mâu thuẫn, tâm lý nhân vật và quy chuẩn mỹ học.
> 3. AI đọc kịch bản (`script.md` / `story.json`) của video đang sản xuất để tự suy luận hình ảnh độc bản.

1. **Thực Thể Tiêu Điểm (Focal Entity / Hero):** Chiếm 35% – 45% diện tích khung hình với biểu cảm cảm xúc tột độ.
2. **Không Gian Kể Chuyện Tự Nhiên (Narrative Environment):** Bối cảnh chiều sâu phản ánh thế giới của câu chuyện.
3. **Vật Thể Xúc Tác Bước Ngoặt (Catalytic Element):** Đồ vật trung tâm mang tính biểu tượng kích hoạt xung đột.

---

## 3. Vùng An Toàn Bắt Buộc (Safety Exclusion Bounds)

* **Top Safe Margin 10%–15% (T017):** Bắt buộc chừa 10%–15% lề tối trên cùng để tránh bị YouTube Shorts bo góc cắt chữ.
* **Dead Zone (Bottom-Right 20% x 20%):** Để trống hoàn toàn, không đặt chi tiết hay chữ vì bị che bởi timecode.
* **XUẤT DUY NHẤT 1 THUMBNAIL (T015):** Chỉ tạo đúng 1 file theo tỷ lệ video (`out/thumbnail.jpg` cho 9:16 hoặc `out/thumbnail_16_9.jpg` cho 16:9).

---

## 4. Abstract Production Templates

### Template 9:16 Shorts
```text
A viral high-CTR vertical YouTube Shorts cover thumbnail for a documentary titled [STORY_TITLE]. 

CRITICAL TOP SAFE MARGIN: Maintain a mandatory 10% to 15% dark empty headroom at the very top edge of the frame. The typography must never touch or hug the top border, ensuring platform UI elements and rounded card containers never clip the lettering.

In the upper portion, positioned with generous headroom below the top edge, the bold hook phrase "[HOOK_TEXT_2_TO_4_WORDS]" is rendered in massive, heavy embossed [ACCENT_COLOR] sans-serif typography with a sharp black drop-shadow outline, optimized for high legibility at small mobile feed sizes.

Below the typography, occupying 35% to 45% of the frame, [FOCAL_ENTITY_SPECIFICATION: The primary subject at the climax of psychological tension, with intense facial expression and posture capturing the central dilemma].

In the surrounding environment, [STORY_SPECIFIC_ENVIRONMENT: The atmospheric physical setting directly embodying the origin or turning point of the dispute, rendered with cinematic depth and spatial storytelling].

Integrated within the scene, [CATALYTIC_ELEMENT: The tangible object or material evidence driving the narrative conflict, highlighted by subtle secondary edge illumination].

Color grading and lighting: Signature two-color dominant scheme featuring intense [ACCENT_COLOR] highlights against [BASE_DARK_COLOR] shadows, rendered with dramatic contrast. Photorealistic 8k, bottom-right quadrant completely free of focal elements.
```
