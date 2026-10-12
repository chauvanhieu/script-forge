# Kế hoạch xây kênh: "History for Sleep" (ưu tiên long-form)

> **Mục tiêu dài hạn:** kênh lọt top đầu kết quả tìm kiếm YouTube cho keyword `history for sleep`.
> **Thị trường:** English, Tier-1 (US trước, sau đó UK/CA/AU).
> **Ngày lập:** 11/10/2026.

---

## 1. Vì sao chọn keyword này (dữ liệu đã thu thập)

| Tín hiệu (Google Trends, YouTube Search, US) | Giá trị |
|---|---|
| `history for sleep` trong nhóm Top của `sleep history` (3 tháng) | **100/100** (đứng đầu) |
| `boring history` (cùng nhóm) | 60/100 |
| `sleep history`, tăng trưởng 5 năm | **81x** (tính từ nền rất thấp) |
| `history for sleep` trong Rising của `history documentary` (5 năm) | **+1,200%** |
| `medieval history` trong Rising của `sleep history` (3 tháng) | +80% |
| `history`, keyword mẹ (5 năm, 4 thị trường Tier-1) | lớn nhất trong nhóm kể chuyện, tăng 1.2–1.36x, ổn định nhất |

**Lợi thế riêng của long-form ngủ:** video dài 1–3 giờ, người xem bật lên rồi ngủ, nên watch time mỗi lượt xem rất cao. Mốc YouTube Partner Program (1.000 sub và 4.000 giờ xem công khai trong 12 tháng) đạt nhanh hơn nhiều so với Shorts.

---

## 2. Đánh giá thực tế về mục tiêu "top đầu"

- Keyword chính `history for sleep` đang bị các kênh lâu năm chiếm. Thứ hạng search YouTube phụ thuộc vào CTR, thời lượng xem, mức độ thỏa mãn của người xem và uy tín kênh. **Không có cách nào bảo đảm lên top.**
- **Chiến lược:** thắng các keyword đuôi dài trước (`ancient egypt history for sleep`, `medieval life history for sleep`…). Uy tín kênh tích lũy dần sẽ kéo keyword chính lên.
- **Mốc đo:** vị trí của kênh khi tìm `history for sleep` ở chế độ ẩn danh (US VPN), và báo cáo *YouTube search terms* trong YouTube Studio.

---

## 3. Định vị: khác biệt so với kênh AI "slop"

Điểm yếu đã ghi nhận ở đối thủ (review 02/2026, kênh Boring History Secrets và các kênh tương tự): **nội dung lặp sau khoảng 60 phút**, **"historians say" không có nguồn**, đọc lời kêu gọi like/subscribe giữa video, và câu catchphrase rập khuôn.

Kênh của bạn khác ở 6 điểm:

| # | Cam kết | Cách thực hiện trong pipeline |
|---|---|---|
| 1 | **Không lặp nội dung** | Kịch bản chia chương, kiểm tra trùng lặp giữa các chương trước khi tạo giọng (bổ sung vào bước Gate 1) |
| 2 | **Có nguồn thật** | Mỗi video có mục *Sources* trong description (sách, bài học thuật). Narration gắn với nguồn cụ thể, không dùng "historians say" chung chung |
| 3 | **Không ngắt giấc ngủ** | Không CTA giữa video. Chỉ một câu nhẹ ở 60 giây đầu. Kết thúc bằng fade to black và vài phút ambient |
| 4 | **Âm thanh an toàn cho giấc ngủ** | Không có peak đột ngột, loudness thấp hơn chuẩn Shorts (-16 LUFS), BGM rất nhỏ, không SFX |
| 5 | **Hình ảnh dịu** | Tông ấm và tối (ánh nến, lò sưởi), slide dài 20–30 giây, Ken Burns chậm. Không có ảnh gây giật mình |
| 6 | **Giọng kể nhất quán** | Một giọng duy nhất cho cả kênh, chậm khoảng 120–135 từ/phút. Ngôi thứ hai: *"You wake up in a stone cottage…"* |

---

## 4. Thông số format video

| Thông số | Giá trị |
|---|---|
| Thời lượng | **Pilot 60 phút** → chuẩn **2 giờ** → compilation **6–10 giờ** (ghép các tập cũ) |
| Tỷ lệ khung | 16:9, 1920×1080 |
| Số từ | ~130 từ/phút → 60 phút ≈ 7.800 từ, 2 giờ ≈ 15.600 từ |
| Cấu trúc | Intro dịu 60–90 giây → 8–12 chương (mỗi chương 10–15 phút, một khía cạnh đời sống) → outro fade to black |
| Số ảnh | Slide 20–30 giây → 2 giờ ≈ 240–360 ảnh. Tái sử dụng plate bối cảnh để giảm tải |
| Phụ đề | Tắt (`captions.mode = none`) |
| Chapters | Có, timestamp mỗi chương trong description |
| Âm thanh | Giọng + BGM ambient (gió, mưa, lửa). Không SFX (đúng chuẩn T026) |

**Công thức tiêu đề:** `[Chủ đề cụ thể] | History for Sleep` hoặc `History for Sleep: What Life Was Like in [Thời kỳ/Nơi chốn]`. Keyword chính luôn nằm trong tiêu đề, dòng đầu description, tên playlist và tags.

**Thumbnail:** một template cố định, nhận diện bằng màu sắc. Tối, ấm, một nhân vật hoặc bối cảnh, chữ nhỏ 2–4 từ, tông yên tĩnh. *Lưu ý:* quy chuẩn thumbnail "shock/disbelief" (T011) trong AGENTS.md **không phù hợp** với kênh ngủ, cần ghi đè trong `channels/<slug>/thumbnail-system.md`.

---

## 5. Lộ trình 12 video đầu tiên (từ dữ liệu 3 tháng)

Mỗi video = một keyword đuôi dài + `history for sleep`.

| # | Chủ đề | Dữ liệu căn cứ |
|---|---|---|
| 1 | What Life Was Like in Ancient Egypt | `what was ancient egypt like` +350%, `life in ancient egypt` Top 24 |
| 2 | A Day in a Medieval Village | `medieval history` +80% trong sleep history, `medieval life` Top 8 |
| 3 | The 18th Dynasty of Egypt: Hatshepsut to Tutankhamun | `18th dynasty of ancient egypt` +1,350% |
| 4 | The Fall of the Roman Empire | `fall of the roman empire` Top 35, `roman empire collapse` +70% |
| 5 | The Odyssey, Told Slowly | `the odyssey explained` +450% (sóng phim, làm sớm) |
| 6 | Ancient Mesopotamia: The First Cities | `ancient mesopotamia` +80% |
| 7 | How the Ancients Built: Ancient Engineering | `ancient engineering` Breakout |
| 8 | The Gods and Goddesses of Ancient Egypt | Breakout |
| 9 | Life Inside a Medieval Castle | `medieval castle` Top 18 |
| 10 | The History of Everyday Things: Concrete, Bread, Salt | `history of concrete` +1,800% |
| 11 | Byzantium: Rome's Last Thousand Years | `eastern roman empire` Top 5 |
| 12 | **Compilation 8 giờ** ghép tập 1, 2, 3, 4 | Format compilation phổ biến trong ngách |

**Playlist từ đầu:** *Ancient Egypt for Sleep*, *Medieval Life for Sleep*, *Rome for Sleep*, *Myths for Sleep*.

---

## 6. Lịch đăng và Shorts hỗ trợ

| Giai đoạn | Long-form | Shorts (kéo người xem về video dài) |
|---|---|---|
| Tháng 1 | 1 video/tuần (pilot, sửa pipeline) | 2–3/tuần, cắt từ kịch bản long-form |
| Tháng 2–3 | **2 video/tuần** cố định (ví dụ thứ 3 và thứ 6, đăng tối giờ US) | 3–5/tuần |
| Tháng 4+ | 2 video/tuần + 1 compilation/tháng | 3–5/tuần |

Shorts dùng lại pipeline Shorts hiện có, kèm link *Related video* tới bản long-form.

---

## 7. Việc kỹ thuật cần làm trước (Phase 0)

Pipeline đã có: 16:9, `target_seconds` không giới hạn trên, `captions.mode = none`, Ken Burns (`zoompan`), BGM ducking, logo watermark 16:9.

| # | Việc | Lý do |
|---|---|---|
| 1 | **Tối ưu trộn BGM trong `sf_render.py`** | `mix_audio` đang lặp Python trên từng sample. 2 giờ stereo 48kHz ≈ 690 triệu lần lặp, sẽ rất chậm. Chuyển sang numpy hoặc filter `amix`/`sidechaincompress` của FFmpeg |
| 2 | **Render theo chương rồi nối lại** | Tránh một filter graph FFmpeg với hơn 300 ảnh. Render từng chương, rồi dùng concat demuxer |
| 3 | **Profile format "sleep long-form" theo kênh** | Các quy chuẩn Shorts trong AGENTS.md (T024 48–54s, T027 nhịp hook 1–1.5s, slide 1.5–2.5s, thumbnail shock) phải được ghi đè ở cấp kênh |
| 4 | **Kịch bản theo chương + kiểm tra lặp** | 15.600 từ phải viết theo từng chương. Thêm bước so khớp ngữ nghĩa giữa các chương ở Gate 1 |
| 5 | **Loudness cho giấc ngủ** | Mục tiêu thấp hơn -16 LUFS, không peak. Cần nghe thử để chốt |
| 6 | **Outro fade to black** | Tắt dần hình và giọng, giữ ambient vài phút |
| 7 | **Chạy thử 60 phút** | Đo thời gian tạo giọng, align, render, tạo ảnh FLUX (chạy tuần tự để tránh OOM) |

*Các mục 1–2 là rủi ro đã thấy trong code nhưng chưa đo thực tế; bản pilot 60 phút sẽ xác nhận.*

---

## 8. Thiết lập kênh

- **Tên kênh:** chưa chốt. Phải khác hẳn các tên đã có (Sleepy History, Boring History for Sleep, Really Boring History, Sleep Historyian, History & Sleep). Kiểm tra handle còn trống trước khi tạo.
- **Khởi tạo:** `uv run scripts/sf_channel.py new <slug> --name "<Tên>" --niche "History for Sleep" --lang en`, sau đó viết 6 module kênh với các ghi đè ở mục 4 và 7.
- **Cài đặt YouTube:**
  - Đặt *Not made for kids*.
  - Bật nhãn *Altered or synthetic content* khi ảnh AI trông như thật.
  - Đặt ngôn ngữ video là English.
  - Chọn danh mục Education.
- **Description mẫu:** dòng 1 chứa keyword và chủ đề, sau đó chapters, rồi Sources, rồi tuyên bố dùng AI cho hình minh họa và giọng đọc, cuối cùng là hashtags.

---

## 9. KPI và mốc kiểm tra

| Mốc | Chỉ số cần đo | Hành động nếu không đạt |
|---|---|---|
| Sau 4 video | CTR thumbnail, thời lượng xem trung bình, % người xem quay lại | Đổi template thumbnail, đổi giọng |
| Tháng 3 | Vị trí của kênh khi tìm các keyword đuôi dài; giờ xem tích lũy | Dồn lực vào cụm chủ đề có view tốt nhất |
| Tháng 6 | Đạt điều kiện YPP (1.000 sub + 4.000 giờ xem); bắt đầu xuất hiện khi tìm `history for sleep` | Tăng compilation, tối ưu lại playlist |
| Tháng 12 | Vị trí khi tìm `history for sleep` | Đánh giá lại định vị |

*Các mốc là mục tiêu đề xuất, không phải số liệu chuẩn ngành.*

---

## 10. Rủi ro

| Rủi ro | Giảm thiểu |
|---|---|
| Chính sách "inauthentic content" (bị coi là đúc khuôn) | Nguồn thật, không lặp, cấu trúc chương thay đổi theo chủ đề, giọng và phong cách nhất quán có bản sắc |
| Ngách đang bão hòa nhanh (tăng 81x) | Thắng bằng chất lượng âm thanh và độ chính xác, không thắng bằng số lượng |
| Tài nguyên máy (FLUX + render 2 giờ) | Pilot 60 phút, render theo chương, tái dùng plate |
| Phụ thuộc trend | `history` là keyword mẹ ổn định nhất (cv 0.09–0.13). Format ngủ chỉ là lớp trình bày |
