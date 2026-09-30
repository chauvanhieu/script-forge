---
name: agent-voice-selection
description: Hướng dẫn agent tự động tìm kiếm, phân tích và cảm nhận để chọn giọng phù hợp từ VoiceStudio bằng curl thay vì script python.
---

# Agent Voice Selection Skill

User muốn CHÍNH AGENT tự "cảm nhận" kịch bản và chọn giọng, không phụ thuộc vào một script chọn giọng tự động (`sf_audition.py` đã bị xoá). Agent sẽ dùng `curl` để tương tác trực tiếp với API của VoiceStudio, đọc metadata của các giọng, tự đánh giá và chốt giọng phù hợp nhất với kịch bản.

## Quy trình Agent tự chọn giọng:

### 1. Hiểu kịch bản (Contextualize)
- Đọc `script.md` hoặc phần `brief` trong `story.json` để hiểu:
  - Thể loại (genre), mood (tâm trạng), target audience (khán giả), và nội dung câu hook.
- Xác định các tiêu chí tìm kiếm:
  - `lang` (ví dụ: `vi` cho tiếng Việt, `en` cho tiếng Anh).
  - `age` (ví dụ: `middle-aged` cho trung niên, `young adult` cho thanh niên).
  - `gender` (ví dụ: `male`, `female`).
  - `pitch` (ví dụ: `low pitch` cho giọng trầm ấm điện ảnh, `high pitch` cho năng lượng cao).
  - `use_case` (ví dụ: `narration` cho kể chuyện/tài liệu, `informative` cho giải thích/bóc phốt, `social` cho Tiktok/Shorts, `advertisement` cho quảng cáo).

### 2. Tìm kiếm ứng viên bằng `curl`
- Dùng công cụ `run_command` để gọi `curl` tới VoiceStudio (chạy tại `http://127.0.0.1:3900`).
- Endpoint: `GET /archetypes`
- Tham số truy vấn (URL encoded): `use_case`, `gender`, `age`, `pitch`, `lang`, `limit`.
- Ví dụ mẫu:
  ```bash
  curl -G "http://127.0.0.1:3900/archetypes" \
    --data-urlencode "lang=vi" \
    --data-urlencode "use_case=narration" \
    --data-urlencode "gender=male" \
    --data-urlencode "limit=10"
  ```
- *Lưu ý: Nếu API VoiceStudio không phản hồi, bạn có thể cần kiểm tra xem server có đang chạy không hoặc yêu cầu user khởi động.*

### 3. Cảm nhận và Đánh giá (Agent Intuition)
- Phân tích kết quả JSON trả về. Mỗi archetype có các trường `id`, `name`, `use_case`, `instruct`, `facets`.
- **ĐÂY LÀ BƯỚC QUAN TRỌNG NHẤT:** Dựa trên trí tuệ và sự nhạy bén của bạn (Agent), hãy đọc trường `instruct` và `name` để *cảm nhận* xem giọng nào toát lên đúng thần thái của kịch bản nhất. 
  - *Ví dụ 1:* Kịch bản Phật giáo cần giọng trầm ấm, chậm rãi, uy nghiêm $\rightarrow$ Ưu tiên `middle-aged`, `low pitch`, instruct chứa "calm", "wisdom".
  - *Ví dụ 2:* Kịch bản bóc phốt/cảnh báo lừa đảo cần giọng đanh thép, rõ ràng, dứt khoát $\rightarrow$ Ưu tiên `informative`, instruct chứa "urgent", "clear", "authoritative".
- Chọn ra **1 giọng xuất sắc nhất** (có thể là archetype ID hoặc trực tiếp đoạn `instruct`).

### 4. Chốt giọng vào `story.json`
- Khi đã chọn được giọng ưng ý, hãy dùng công cụ chỉnh sửa file (như `replace_file_content` hoặc `multi_replace_file_content`) để cập nhật trực tiếp vào file `story.json` của dự án hiện tại.
- Tìm object của nhân vật trong mảng `cast` (thường là narrator).
- Sửa phần `"voice"` thành cấu trúc `design`:
  ```json
  "voice": {
    "source": "design",
    "profile_id": "",
    "design_prompt": "<giá trị của trường instruct từ archetype bạn chọn>",
    "instruct": "<giá trị của trường instruct từ archetype bạn chọn>",
    "selected_name": "<giá trị của trường name>"
  }
  ```
- Việc để trống trường `"profile_id": ""` (chuỗi rỗng) rất quan trọng, nó sẽ báo hiệu cho kịch bản sinh giọng (`sf_voice.py`) biết cần tự động tạo/lấy profile mới từ `design_prompt` này khi chạy bước tổng hợp giọng tiếp theo.

### 5. Thông báo kết quả
- Trả lời user rằng bạn đã dùng sự nhạy bén của mình để gọi API, tìm kiếm các ứng viên, và chốt giọng nào.
- Trích dẫn ngắn gọn lý do tại sao giọng đó (dựa trên `instruct`) lại là mảnh ghép hoàn hảo cho kịch bản lần này.

## Tham khảo thêm
- Bạn có thể đọc toàn bộ spec của VoiceStudio API tại file: `docs/api-1.yaml` để hiểu rõ hơn về các endpoint (như `/archetypes`, `/health`) và cấu trúc trả về nếu cần.
