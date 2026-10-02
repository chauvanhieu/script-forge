# Voice Profile & Audio Persona: The Grey Verdict

Tài liệu này định nghĩa hệ thống âm thanh, lựa chọn giọng đọc và quy chuẩn phát âm dành cho Agent âm thanh (`sf-audio`) khi sản xuất nội dung cho kênh **The Grey Verdict**.

---

## 1. Persona Giọng Đọc (The Analytical Inquisitor)

* **Phong cách:** Deep, calm, authoritative, cold analytical documentary narrator (Người dẫn chuyện tài liệu sâu lắng, điềm tĩnh, uy quyền và phân tích sắc lạnh).
* **Ngôn ngữ:** English (Neutral Global Accent - Giọng Anh-Mỹ hoặc Anh-Quốc tế trung tính, phát âm chuẩn xác, không dùng từ lóng địa phương).
* **Nguyên tắc cảm xúc:**
  - Không thiên vị hay thể hiện sự phán xét chủ quan.
  - Đoạn mở đầu (Line 1): Đọc dứt khoát, cắt nhịp bất ngờ, kích hoạt sự tò mò trong 1.5s đầu.
  - Đoạn cao trào (Pha 3): Nhấn mạnh vào những tình tiết đảo ngược và con số chấn động.
  - Đoạn kết (Pha 4): Giọng hạ trầm, để ngỏ câu hỏi nhị phân đầy sức nặng.

---

## 2. Thông Số Kỹ Thuật (Audio Calibration)

* **Tốc độ phát âm khuyến nghị:** ~14.0 – 15.0 ký tự/giây (Tiếng Anh).
* **Khoảng ngắt nghỉ (`pause_after_ms`):**
  - Giữa các câu thoại liền mạch: 200ms – 300ms.
  - Tại bước ngoặt chuyển cảnh (Scene turns): 400ms – 600ms.
* **Quy chuẩn thoại liền mạch (T004):** Triệt tiêu hoàn toàn dấu phẩy ngắt dòng sai, loại bỏ `...` hoặc ngoặc kép giữa các vế câu liền mạch để công cụ TTS đọc một mạch tự nhiên, không bị vấp.

---

## 3. Cấu Hình Cast Giọng Chính Thức Của Kênh (Official Channel Signature Voice)

Giọng đọc chính thức của kênh The Grey Verdict được chốt chuẩn từ video `the-good-samaritan-trap` (VoiceStudio / Kokoro TTS):

```json
{
  "id": "narrator",
  "name": "Narrator",
  "role": "narrator",
  "caption_color": "#F5A623",
  "voice": {
    "source": "design",
    "design_prompt": "male, middle-aged, low pitch",
    "instruct": "male, middle-aged, low pitch",
    "profile_id": "6d80d98d"
  }
}
```

```yaml
voice_casting:
  provider: voicestudio
  source: design
  design_prompt: "male, middle-aged, low pitch"
  instruct: "male, middle-aged, low pitch"
  profile_id: "6d80d98d"
  caption_color: "#F5A623"
  speed: 1.05
  pitch: 0.98
  target_speaking_rate_chars_per_s: 14.5
```
