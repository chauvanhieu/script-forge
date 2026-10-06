# Visual Style Bible: The Grey Verdict

Tài liệu này định nghĩa hệ thống nhận diện thị giác, ánh sáng và thẩm mỹ điện ảnh dành riêng cho kênh **The Grey Verdict**. Agent phụ trách phần hình ảnh (`sf-visual`) bắt buộc tuân thủ tài liệu này khi chế tác prompt cho từng slide.

---

## 1. Bảng Màu Nhận Diện Thương Hiệu (Brand Color Palette)

Toàn bộ hình ảnh và thumbnail của kênh phải được neo chặt vào bảng màu chủ đạo sau:

| Tên Màu | Mã Hex | Vai Trò & Tác Dụng Thị Giác |
| :--- | :--- | :--- |
| **Obsidian Black** | `#0B0E14` | Màu nền tối cơ bản, tượng trưng cho tính nghiêm minh của thể chế, chiều sâu bóng đổ điện ảnh. |
| **Cold Steel Grey** | `#8E9AA8` | Màu trung tính, tượng trưng cho tính khách quan, bộ máy quan liêu và vùng xám đạo đức. |
| **Verdict Amber Gold** | `#F5A623` | **Điểm nhấn thương hiệu chính**: Viền sáng chủ thể (rim light), quầng sáng spotlight, ánh kim loại và Text Hook. |
| **Crimson Alert** | `#D9383A` | Điểm nhấn phụ: Sử dụng cho các điểm xung đột gay gắt, chi tiết cảnh báo hoặc phán quyết mang tính trừng phạt. |

---

## 2. Ngôn Ngữ Ánh Sáng & Góc Máy Điện Ảnh (Chiaroscuro Noir)

* **Phong cách cốt lõi:** Hard Chiaroscuro Noir kết hợp Volumetric Lighting (luồng sáng thể tích xuyên qua bóng tối).
* **Độ tương phản:** Độ tương phản sáng - tối cực đại (Deep blacks, sharp focused highlights). Không bao giờ sử dụng ánh sáng phẳng (flat lighting) hay màu pastel mềm mại.
* **Chất liệu hình ảnh:** 35mm film still aesthetic, hạt grain điện ảnh tinh tế, độ chi tiết siêu thực (photorealistic 8k, Panavision anamorphic lens look).
* **Bố cục khung hình (Full-frame 9:16):** Tràn khung tự nhiên, không ép lề trắng hay chừa section text giả tạo ở đáy ảnh (T002).

---

## 3. Hệ Thống Typography Nhận Diện

* **Display / Title Font (Dành cho Thumbnail & Đồ họa):**  
  *Cinzel Decorative* hoặc *Montserrat Black* (Chữ in hoa, dập nổi 3D, kerning rộng, uy nghi, quyền lực).
* **Body / Subtitle Font (Dành cho Phụ đề Karaoke):**  
  *Inter Bold* hoặc *Outfit SemiBold* (Nét chữ dày, tròn trịa, cực kỳ dễ đọc trên màn hình điện thoại di động).
* **Quy chuẩn màu sắc Phụ đề Karaoke (T009/T010):**  
  Base text: `#FFFFFF` (Trắng), Active Word: `#F5A623` (Vàng Hổ Phách), Pre-roll timing: `-40ms`.

---

## 4. Ma Trận Phối Cảnh Trừu Tượng Theo Tiến Trình (Visual Grammar)

1. **Giai đoạn Mở màn (Shock 0s–6s - Hyper-Fast Visual Cuts & Ultra-Contrast Chiaroscuro T025/T027/T-GV08):**
   * *Nhịp chuyển cảnh:* **Cắt cảnh siêu nhanh 1.0s – 1.5s / slide cut**. Bắt buộc gán **3 đến 4 slide hình ảnh biến đổi góc máy liên tục** cho câu thoại mở đầu (Line 1):
     - *Slide 1 (0.0s - 1.3s):* Extreme Macro Close-up vật thể xúc tác hoặc hành động xung đột giật gân.
     - *Slide 2 (1.3s - 2.6s):* Wide Cinematic Dutch Tilt hiện trường nghẹt thở trong màn đêm.
     - *Slide 3 (2.6s - 4.0s):* Cận cảnh ánh mắt / biểu cảm bàng hoàng tột độ của nhân vật trung tâm.
     - *Slide 4 (4.0s - 5.5s):* Góc chéo thể chế / vật phẩm pháp lý mang tính phán quyết.
   * *Ngôn ngữ Ánh sáng:* Ultra-High Contrast Chiaroscuro Noir. Tỷ lệ quang học bắt buộc: 80% bóng tối Obsidian (`#0B0E14`) đối kháng rực rỡ với 20% ánh sáng vàng hổ phách (`#F5A623`) hoặc vệt đèn pha chém rách bóng đêm.
   * *Tokens bắt buộc cho Slide Hook:* `ultra-high contrast chiaroscuro noir, blinding amber rim lighting against ink obsidian black, extreme macro focus, visceral tension, hyper-crisp 8k documentary still, no washed-out tones, zero flat lighting`.
2. **Giai đoạn Bằng chứng & Hệ thống (Build-up 6s–28s):**
   * *Nhịp chuyển cảnh:* 1.8s – 2.2s / slide cut.
   * *Góc máy:* Symmetrical Medium Shot hoặc Over-the-shoulder phối cảnh kiến trúc lớn.
   * *Ánh sáng:* Overhead Fluorescent / Cold Institutional Shadow.
   * *Không gian:* Bối cảnh chứa đựng nguồn gốc sự kiện hoặc trung tâm vận hành hệ thống, tái hiện độ sâu kiến trúc và chiều sâu không gian điện ảnh.
3. **Giai đoạn Phán quyết & Bùng nổ (Climax 29s–44s):**
   * *Nhịp chuyển cảnh:* 1.5s – 2.0s / slide cut.
   * *Góc máy:* Wide Cinematic Master Shot đối lập với Cận cảnh ánh mắt nhân vật.
   * *Ánh sáng:* Warm Tungsten Spotlight cắt xuyên qua màn đêm đen sâu thẳm.
   * *Chi tiết biểu cảm:* Đỉnh điểm biểu đạt tâm lý của các bên đối đầu, chuyển động dứt khoát của hành động đưa ra quyết định, vật thể xúc tác chịu tác động trực tiếp tại thời khắc phán quyết.


---

## 5. Quy Chuẩn Lịch Sử Thời Kỳ & Chống Lệch Vai Tác Chiến (Era Anchoring & Role Sanitization - T022)

Các vụ án của kênh The Grey Verdict thường diễn ra trong các bối cảnh lịch sử có thật (thập niên 1960–1990 hoặc tiền án lệ thế kỷ 20). Để triệt tiêu hoàn toàn lỗi AI vẽ sai thành cảnh sát đặc nhiệm SWAT hay đồ công nghệ hiện đại:

1. **Khóa Mốc Thời Kỳ & Đạo Cụ Lịch Sử (Era Anchoring):**
   - Luôn neo rõ mốc thời gian trong prompt: ví dụ `1970s vintage era`, `period-accurate 1971 Midwest America`.
   - Đạo cụ phải phù hợp cơ học cổ điển: Đèn pin vỏ sắt dùng bóng sợi đốt ánh vàng cam (`vintage metal flashlight with warm incandescent yellow beam`), dây thừng gai sợi thô (`hemp rope/cord`), khóa cơ khí gỉ sét (`rusty iron latch/tumbler`), kính thủy tinh dày.
   - Tuyệt đối cấm đồ công nghệ hiện đại: `no LED light bars, no modern flashlights, no plastic tools, no digital gadgets, no modern vehicles`.
2. **Bộ Lọc Loại Trừ Tác Chiến Hiện Đại (Negative Archetype Filters):**
   - Khi tạo hình nhân vật trộm vặt, người đột nhập, nạn nhân hoặc nông dân:
   - Dùng từ vựng dân sự: `petty prowler`, `civilian trespasser`, `vintage burglar in worn jacket`, `Iowa farmer in denim chore coat`.
   - Cấm triệt để từ vựng đặc nhiệm: `no tactical gear, no SWAT team, no modern police armor, no helmets, no Kevlar vest, no modern weaponry, no balaclava`.

---

## 6. Tính Hợp Lý Cơ Học Trong Chứng Cứ & Hiện Trường (Physical Plausibility & 2-Shot Mechanics - T023)

Đối với các vụ án liên quan đến bẫy cơ học (spring-gun, tripwire), vũ khí tự chế hoặc chứng cứ hiện trường:
- Không bao giờ bắt AI vẽ toàn bộ một hệ thống truyền động cơ học phức tạp trong 1 khung hình duy nhất (tránh lỗi dây buộc ngược phía trước cò súng, dây bay lơ lửng).
- **Áp dụng Cặp Cảnh Nguyên Nhân - Kết Quả (2-Shot Cause-and-Effect):**
  - *Shot 1 (Điểm Tỳ Lực):* Macro cận cảnh điểm tiếp xúc cơ học cụ thể với hướng lực rõ ràng (ví dụ: sợi dây gai luồn phía sau vấu cò súng, tỳ qua cọc gỗ chân giường). Mô tả chuẩn xác: `"taut hemp cord looped securely behind the curved iron trigger shoe, passing firmly around an anchor post"`.
  - *Shot 2 (Góc Đón Lõng):* Cận cảnh góc thấp từ họng súng chĩa dốc xuống sàn gỗ đón lõng vị trí cánh cửa khép hờ ở tầm mắt cá chân.
- Não bộ người xem sẽ tự ghép 2 shot này thành một hệ thống cơ học hoàn hảo, tạo cảm giác thuyết phục tuyệt đối.
