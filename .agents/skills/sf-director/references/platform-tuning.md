# Platform Tuning & Distribution Specs for StoryForge

Tài liệu này định nghĩa các quy chuẩn kỹ thuật và thuật toán phân phối cho 3 nền tảng video ngắn hàng đầu: **YouTube Shorts**, **TikTok**, và **Instagram Reels**. Tài liệu được sử dụng bởi `sf-director` ở Stage 1 (Brief) để xác định mục tiêu và Stage 9 (Report) để tạo gói xuất bản (Publishing Package).

---

## 1. So Sánh Ma Trận Thuật Toán Phân Phối

| Chỉ số / Đặc thù | YouTube Shorts | TikTok | Instagram Reels |
|---|---|---|---|
| **Chỉ số Vàng (North Star Metric)** | **VVSA** (Viewed vs Swiped Away > 70%) & **APV** (Average % Viewed > 100%) | **Completion Rate** (15s: 100%, 60s: >70%) & **Comment Rate** | **Sends Per Reach** (> 3%) & **Save Rate** (> 2%) |
| **Hành vi người xem** | Lướt cực nhanh, đánh giá giá trị trong 1s đầu | Tương tác xã hội, bình luận tranh luận, bắt trend | Chia sẻ riêng tư (DM bạn bè), lưu lại làm tư liệu |
| **Kỹ thuật giữ chân chủ đạo** | **Seamless Looping** (vòng lặp vô tận không điểm dừng) | **Open Loops dồn dập** & Chi tiết gây tranh luận nhẹ | **Value Density** (Mật độ giá trị cao) & Đồng cảm cá nhân |
| **Độ dài tối ưu** | 45s – 58s (giữ dưới 60s để tối đa APV) | 30s – 45s (hoặc >60s cho Series) | 30s – 60s |
| **Phong cách Caption** | Ngắn gọn (< 100 ký tự), tập trung vào từ khóa tìm kiếm (SEO) | Hài hước / khơi mào tranh luận, 3-5 hashtag ngách | Dài, chi tiết (Micro-blog), cung cấp thêm thông tin chưa có trong video |

---

## 2. Quy Chuẩn Kỹ Thuật Chi Tiết Từng Nền Tảng

### 2.1. YouTube Shorts Tuning
- **Mục tiêu cốt lõi:** Đánh bại tỷ lệ lướt qua (VVSA) ngay ở 1.5 giây đầu và giữ chân để người xem xem lại lần 2 (APV > 100%).
- **Kỹ thuật Seamless Looping (Vòng lặp vô tận):**
  * Câu cuối cùng của video được viết như một vế mở của câu đầu tiên.
  * *Ví dụ:*
    - Câu kết: *"Và lý do vì sao mọi chuyện bắt đầu lại chính là vì..."*
    - Câu mở (quay lại từ đầu): *"...một chiếc đèn ông sao dính máu trên tay Thắng."*
  * Khi người xem chưa kịp nhận ra video đã hết, họ đã vô tình xem lại 2-3 giây đầu của lượt thứ hai, đẩy APV vượt mốc 100%.
- **Chiến lược CTA:**
  * Không xin like chung chung.
  * Dẫn hướng: *"Xem toàn bộ hồ sơ vụ án ở video liên kết bên dưới"* hoặc *"Đăng ký kênh để không bỏ lỡ phần 2"*.

### 2.2. TikTok Content Tuning
- **Mục tiêu cốt lõi:** Completion Rate và Khơi mào phần bình luận (Comment Section là trái tim của TikTok).
- **Kỹ thuật kích hoạt bình luận (Comment Triggers):**
  * Đặt một câu hỏi lưỡng nan đạo đức ở cuối video ("Nếu là Thắng, bạn sẽ thú tội hay tiếp tục im lặng?").
  * Cài cắm chi tiết "bất thường" hoặc gây tranh cãi nhẹ ở slide 3-4 (ví dụ: con số lịch sử gây bất ngờ, chi tiết ẩn trong ảnh). Người xem sẽ dừng lại để gõ bình luận, giúp thời gian xem thực tế tăng vọt.
- **Chiến lược CTA:**
  * Kêu gọi tranh luận: *"Bạn chọn cách 1 hay cách 2? Để lại câu trả lời bên dưới."*

### 2.3. Instagram Reels Tuning
- **Mục tiêu cốt lõi:** Lượt gửi qua tin nhắn Direct Message (Sends per reach). Thuật toán Meta đánh giá 1 lượt Share qua DM có giá trị phân phối cao gấp 5 lần 1 lượt Like.
- **Kỹ thuật kích hoạt chia sẻ:**
  * Tính liên hệ (Relatability): *"Gửi video này cho đứa bạn luôn trễ hẹn"*.
  * Mật độ tri thức (Value): Kịch bản Factual giải thích cô đọng khiến người xem muốn lưu lại để học hoặc chia sẻ cho đồng nghiệp/người thân.
- **Chiến lược Caption Micro-Blog:**
  * Video nêu vấn đề và cơ chế chính.
  * Caption trình bày thêm: 3 bước hành động cụ thể, trích dẫn tài liệu gốc, hoặc bối cảnh lịch sử chuyên sâu.

---

## 3. Bộ Mẫu Single-Action CTA (Quy Tắc 1 Hành Động Duy Nhất)

Tuyệt đối cấm sử dụng lời kêu gọi gộp: *"Nhớ like, subscribe, bấm chuông, bình luận và chia sẻ video nhé!"* (Quá tải nhận thức → người xem không làm gì cả).

Mỗi video chỉ được chọn đúng **1 mục tiêu duy nhất**:

| Mục tiêu chuyển đổi | Nền tảng ưu tiên | Mẫu câu thoại kết thúc (Verbal CTA) |
|---|---|---|
| **Kích thích Chia sẻ (Share / Send)** | Instagram Reels | *"Gửi câu chuyện này cho người thân mà bạn muốn cùng đón Trung Thu năm nay."* |
| **Kích thích Lưu lại (Save)** | Instagram Reels / TikTok | *"Lưu video này lại trước khi bạn cần dùng đến nó trong lần tới."* |
| **Kích thích Bình luận (Comment)** | TikTok | *"Bạn đứng về phía người mẹ hay người con? Hãy để lại ý kiến bên dưới."* |
| **Xem tiếp Phần 2 / Follow** | YouTube Shorts / TikTok | *"Theo dõi kênh để đón xem kết cục ở phần 2 vào tối mai."* |
| **Seamless Loop (Không CTA)** | YouTube Shorts | Kết thúc bằng câu nối lửng lơ để vòng lặp tự động quay lại đầu. |

---

## 4. Gói Xuất Bản Hoàn Chỉnh (Publishing Package Blueprint)

Ở Stage 9 của `sf-director`, đạo diễn phải xuất bản tài liệu metadata theo mẫu sau:

```markdown
### 📦 Gói Xuất Bản (Publishing Package) - [Tên Slug]
- **Nền tảng mục tiêu:** [youtube_shorts | tiktok | instagram_reels]
- **Tiêu đề Video (Title):** [Tiêu đề giật tò mò, < 60 ký tự, có từ khóa chính]

#### 1. Caption Xuất Bản
[Đoạn mở đầu giật hook]
[Nội dung tóm tắt giá trị hoặc câu hỏi khơi mào tranh luận]
[Lời kêu gọi hành động Single-Action CTA]

#### 2. Hashtags Chuẩn Ngách (3 - 5 thẻ)
#[TừKhóaChính] #[ThểLoại] #[ĐốiTượngMụcTiêu] #[StoryForge]

#### 3. Pinned Comment (Bình luận ghim đầu trang)
[Câu hỏi dẫn dắt hoặc gợi mở góc nhìn đa chiều để thúc đẩy cộng đồng thảo luận ngay dưới video]
```
