# Visual Style Bible: [CHANNEL_NAME]

Tài liệu này định nghĩa hệ thống nhận diện thị giác, ánh sáng và thẩm mỹ riêng biệt cho kênh **[CHANNEL_NAME]**.

---

## 1. Bảng Màu Nhận Diện Thương Hiệu (Brand Palette)

| Tên Màu | Mã Hex | Vai Trò & Tác Dụng Thị Giác |
| :--- | :--- | :--- |
| **Primary Base** | `#[HEX1]` | Màu nền tảng chủ đạo bao phủ toàn bộ cảnh phim |
| **Secondary Tone** | `#[HEX2]` | Màu chuyển tiếp / đổ bóng môi trường |
| **Accent Glow** | `#[HEX3]` | **Điểm nhấn thương hiệu**: Viền sáng, quầng sáng và Text Hook |
| **Contrast Punch** | `#[HEX4]` | Màu cảnh báo hoặc điểm nút kịch tính |

---

## 2. Ngôn Ngữ Ánh Sáng & Góc Máy Điện Ảnh

* **Phong cách ánh sáng cốt lõi:** [Ví dụ: Cyberpunk Neon, Natural Daylight, Dramatic Chiaroscuro, Pastel Soft Light...]
* **Chất liệu hình ảnh:** [Ví dụ: 35mm film still, 3D Octane Render, Studio Photography, Vintage VHS...]
* **Bố cục khung hình (Full-frame 9:16):** Tràn khung tự nhiên, không ép lề trắng hay chừa section text giả tạo ở đáy ảnh (T002).

---

## 3. Hệ Thống Typography & Phụ Đề Karaoke

* **Display / Title Font (Thumbnail):** [Tên font in hoa, dày, rõ nét]
* **Body / Subtitle Font (Captions):** [Tên font tròn trịa, siêu dễ đọc trên mobile]
* **Màu sắc Subtitle:**
  - Base Word: `#[BASE_HEX]`
  - Active Word Highlight: `#[ACTIVE_HEX]` (Pre-roll timing: `-40ms` - T010)

---

## 4. Quy Chuẩn Lịch Sử Thời Kỳ & Chống Lệch Vai Tác Chiến (Era Anchoring & Role Sanitization - T022)

- **Neo Mốc Thời Gian (Era Anchoring):** Khi câu chuyện diễn ra ở một giai đoạn lịch sử cụ thể, bắt buộc neo mốc thời gian và đạo cụ đặc trưng của thời kỳ đó vào prompt (ví dụ: `1970s vintage era, retro analog props, no modern LED lights, no modern digital devices`).
- **Bộ Lọc Loại Trừ Vai Đối Lập (Negative Archetype Filters):** Khi tạo hình nhân vật dân sự, trộm vặt hoặc nông dân, dùng từ vựng dân sự (`petty prowler`, `civilian trespasser`) và cấm triệt để từ vựng đặc nhiệm: `no SWAT, no tactical gear, no bulletproof armor, no modern police badges, no combat helmets, no modern weapons`.

---

## 5. Tính Hợp Lý Cơ Học & Đạo Cụ Vật Lý (Physical Plausibility & 2-Shot Mechanics - T023)

- Tuyệt đối không nhồi nhét một cơ cấu cơ học phức tạp (bẫy, ròng rọc, dây giật) vào 1 khung hình duy nhất để tránh AI vẽ sai hướng lực hoặc dây lơ lửng.
- **Áp dụng Cặp Cảnh 2-Shot Cause-and-Effect:**
  - *Shot 1 (Điểm Tỳ Lực - Setup):* Cận cảnh (Macro) điểm tiếp xúc cơ học cụ thể với hướng lực rõ ràng (ví dụ: dây gai thắt nút phía sau cò súng, tỳ qua cọc gỗ).
  - *Shot 2 (Góc Đón Lõng - Threat/Vector):* Góc nhìn thuận theo hướng tác động vật lý (ví dụ: từ họng súng chĩa dốc xuống sàn đón lõng vị trí chân cửa).
