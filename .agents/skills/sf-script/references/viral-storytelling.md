# Viral Storytelling & Retention Framework for StoryForge

Tài liệu này đúc kết các quy luật giữ chân (retention) và dẫn dắt cảm xúc của video ngắn triệu view (Short-form Video) từ bộ tri thức Vyral Framework, được bản địa hóa và cấu trúc riêng cho hệ thống sản xuất video AI tự động của StoryForge.

---

## 1. Xương Sống Giữ Chân (The Retention Spine)

Một kịch bản video ngắn (30s – 60s) thất bại không phải vì nội dung dở, mà vì **nhịp phân bổ thông tin sai thời điểm**. Mọi kịch bản StoryForge bắt buộc phải xây dựng dựa trên 4 đốt sống chuẩn:

```
[0s - 3s: Hook 3 Lớp] 
    └── Khơi mào khoảng trống tò mò hoặc cú sốc nhận thức
[4s - 45s: Leo Thang Xung Đột - Escalation]
    └── Chuỗi quan hệ "Nhưng..." & "Vì thế...", loại bỏ hoàn toàn "Và rồi..."
[46s - 55s: Cao Trào & Thỏa Mãn - Payoff]
    └── Giải tỏa sự tò mò đã hứa ở giây đầu tiên, tạo cú lật (twist) hoặc bài học đắt giá
[56s - 60s: Single CTA / Seamless Loop]
    └── 1 mục tiêu hành động duy nhất hoặc móc nối câu kết ngược về câu mở đầu
```

---

## 2. Nguyên Lý Leo Thang South Park: "Nhưng..." và "Vì thế..."

Căn bệnh phổ biến nhất của kịch bản AI là **kể chuyện liệt kê (And Then)**:
> *"Cậu bé làm đèn ông sao. VÀ RỒI trời đổ mưa. VÀ RỒI cái đèn bị ướt. VÀ RỒI cậu bé khóc."*
> → **Hậu quả:** Người xem lướt qua ngay ở giây thứ 5 vì não bộ nhận thấy nhịp điệu dễ đoán, không có xung đột dồn dập.

**Quy tắc bắt buộc:** Mọi bước chuyển giữa các phân cảnh/slide phải được kết nối bằng **"NHƯNG" (Xung đột cản trở)** hoặc **"VÌ THẾ" (Hành động phản ứng/Hệ quả tất yếu)**:
> *"Cậu bé nhịn ăn cả tuần để làm chiếc đèn ông sao đẹp nhất làng. **NHƯNG** khi chỉ còn một giờ trước lễ rước, ngọn nến bất ngờ bốc cháy thiêu rụi toàn bộ khung tre. **VÌ THẾ**, thay vì ngồi khóc, cậu quyết định làm một điều điên rồ mà chưa đứa trẻ nào trong xóm dám thử..."*

### Cách kiểm tra kịch bản (Escalation Check):
- Nếu gạch nối giữa Slide $N$ và Slide $N+1$ có thể thay thế bằng từ *"Và rồi"*, kịch bản đó **chưa đạt**.
- Hãy sửa lại bằng cách đặt nhân vật vào một trở ngại mới (*Nhưng*) hoặc buộc nhân vật phải trả giá cho lựa chọn trước đó (*Vì thế*).

---

## 3. Ba Lỗi Chí Mạng Phá Hủy Tỷ Lệ Giữ Chân (Retention Killers)

| Lỗi chí mạng | Biểu hiện trong kịch bản | Cách khắc phục trong StoryForge |
|---|---|---|
| **1. Hook Yếu / Chậm (Weak / Slow Hook)** | Mất hơn 2 giây mới vào chuyện; mở đầu bằng chào hỏi rườm rà, đặt bối cảnh lan man ("Ngày xửa ngày xưa...", "Hôm nay mình sẽ kể..."). | Cắt phăng bối cảnh. Đặt thẳng câu hỏi sốc, con số nghịch lý, hoặc ném người xem vào giữa tình huống hiểm nghèo ngay Slide 1. |
| **2. Leo Thang Nhạt Nhòa (Flat Escalation)** | Nhịp độ bằng phẳng sau hook; các slide tiếp theo chỉ đơn thuần giải thích dài dòng mà không tăng độ căng thẳng hay mở thêm thông tin mới. | Cứ mỗi 3-5 giây (mỗi slide mới) phải tung ra một mảnh ghép thông tin bất ngờ (Micro-reveal) hoặc đẩy áp lực thời gian lên cao hơn. |
| **3. Payoff Bị Chôn Vùi (Buried / Delayed Payoff)** | Câu trả lời cho hook bị kéo dài quá muộn, hoặc kết thúc lửng lơ khiến người xem cảm thấy bị "lừa nhấp" (clickbait rẻ tiền). | Trả lời trọn vẹn lời hứa ở giây đầu tiên. Phần thưởng cảm xúc (bất ngờ, xúc động, giác ngộ) phải xứng đáng với thời gian người xem đã nán lại. |

---

## 4. Kỹ Thuật Giữ Chân Đặc Thù Cho AI-Generated Video

Trong video AI (hình ảnh tĩnh tạo bởi ComfyUI + giọng đọc Kokoro TTS), người xem không thấy khẩu hình nhân vật hay biểu cảm tự nhiên của người thật. Để khắc phục điểm yếu này, kịch bản phải sử dụng 3 đòn bẩy:

### 4.1. Vòng Lặp Mở (Open Loops)
- Đừng bao giờ giải quyết trọn vẹn một bí mật trước khi gieo một nghi vấn mới.
- **Mô hình:** Mở vòng lặp A (giây 1) → Mở vòng lặp B (giây 15) → Đóng vòng lặp A (giây 35) → Đóng vòng lặp B & mở cú lật C (giây 50).
- Người xem sẽ không thể vuốt đi khi não bộ chưa được thỏa mãn vòng lặp đang dang dở.

### 4.2. Kể Chuyện Kép (Dual Narrative: Lời Nói vs Hình Ảnh)
- **Sai lầm:** Lời thoại nói "Cậu bé đang buồn", hình ảnh vẽ cậu bé cúi đầu buồn bã (thông tin bị trùng lặp 100%, gây nhàm chán).
- **Quy chuẩn StoryForge:** Lời dẫn và Hình ảnh phải bổ trợ nhau tạo nên tầng nghĩa thứ ba:
  * *Lời thoại:* Nói về áp lực tinh thần hoặc sự dối trá ("Ai cũng nghĩ đó chỉ là một tai nạn vô hại...").
  * *Hình ảnh (Visual Prompt):* Thể hiện bằng chứng vật lý hoặc ánh mắt ẩn ý ("Cận cảnh bàn tay run rẩy giấu chiếc bật lửa sau lưng, bóng đổ dài trên sàn gỗ").

### 4.3. Đổi Nhịp Thị Giác & Thính Giác (Micro-Pattern Resets mỗi 3-5s)
- **Thị giác (Visual Motion):** Luân phiên linh hoạt các lệnh chuyển động trong `story.json` (`push_in`, `pull_out`, `pan_left`, `pan_right`, `static`). Cấm để 2 slide liên tiếp cùng một kiểu shot (ví dụ: 2 cận cảnh liên tiếp).
- **Thính giác (Audio Cadence):** Đặt dấu ngắt nghỉ chủ động (`pause_after_ms` từ 250ms – 600ms). Xen kẽ câu thoại ngắn dồn dập (3-5 chữ) với câu tự sự chậm rãi để thay đổi nhịp tim người nghe.

---

## 5. Hướng Dẫn Kịch Bản Cho Hai Thể Loại

### 5.1. Thể loại Hư Cấu (Fiction Drama / Narrative)
- **Trọng tâm:** Xung đột nhân vật, thế tiến thoái lưỡng nan (Dilemma), và sự đồng cảm đạo đức.
- **Công thức:**
  1. *Hook:* Một quyết định sai lầm hoặc bí mật bị vỡ lở.
  2. *Escalation:* Mỗi nỗ lực che đậy lại dẫn đến hậu quả tồi tệ hơn (Nhưng... Vì thế...).
  3. *Climax:* Nhân vật buộc phải đối diện với sự thật đắt giá nhất.
  4. *Ending:* Bài học nhân sinh sâu sắc hoặc sự chuộc lỗi xúc động.

### 5.2. Thể loại Phi Hư Cấu (Factual / Explainer / Document)
- **Trọng tâm:** Phá vỡ định kiến (Counter-intuitive), khoảng cách kiến thức, và cơ chế hoạt động bất ngờ.
- **Công thức:**
  1. *Hook:* Nêu một sự thật hiển nhiên mà 99% mọi người đều hiểu sai.
  2. *Escalation:* Đưa ra bằng chứng lịch sử/khoa học chứng minh niềm tin cũ sụp đổ (Nhưng...).
  3. *Mechanism:* Giải thích cơ chế cốt lõi bằng hình ảnh ẩn dụ dễ hiểu (Vì thế...).
  4. *Takeaway:* Một bài học ứng dụng thực tế hoặc góc nhìn thay đổi thế giới quan.
