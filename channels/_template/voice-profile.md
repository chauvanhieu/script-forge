# Voice Profile & Audio Persona: [Tên Kênh]

Tài liệu này định nghĩa hệ thống âm thanh, lựa chọn giọng đọc và quy chuẩn phát âm dành cho Agent âm thanh (`sf-audio`) khi sản xuất nội dung cho kênh **[Tên Kênh]**.

---

## 1. Persona Giọng Đọc (Audio Persona)

* **Phong cách:** [Ví dụ: Energetic, Fast-paced, Tech-savvy / Calm, Authoritative, Documentary].
* **Ngôn ngữ:** [English / Vietnamese / v.v.] (Accent, tone, cảm xúc).
* **Nguyên tắc cảm xúc:**
  - Đoạn mở đầu (Hook): [Cách nhấn nhá trong 1.5s đầu để giữ chân người xem].
  - Thân bài: [Nhịp điệu và năng lượng].
  - Đoạn kết: [Call to Action hoặc cao trào].

---

## 2. Thông Số Kỹ Thuật (Audio Calibration)

* **Tốc độ phát âm khuyến nghị:** ~[13.0 – 16.0] ký tự/giây.
* **Khoảng ngắt nghỉ (`pause_after_ms`):**
  - Giữa các câu thoại liền mạch: 200ms – 300ms.
  - Tại bước ngoặt chuyển cảnh: 400ms – 600ms.
* **Quy chuẩn thoại liền mạch (T004):** Triệt tiêu hoàn toàn dấu phẩy ngắt dòng sai, loại bỏ `...` hoặc ngoặc kép giữa các vế câu liền mạch để công cụ TTS đọc một mạch tự nhiên.

---

## 3. Cấu Hình Cast Giọng Mẫu (VoiceStudio / Kokoro TTS)

```yaml
voice_casting:
  provider: voicestudio
  voice_id: "[voice_id_tuỳ_chọn]"
  speed: 1.0
  pitch: 1.0
  target_speaking_rate_chars_per_s: 14.5
```
