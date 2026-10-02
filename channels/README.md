# Multi-Channel Architecture (`channels/`)

Thư mục này quản lý toàn bộ các vùng trí tuệ độc lập (Domain-Specific Intelligence) định vị thương hiệu, phong cách thị giác, cấu trúc nội dung và học hỏi tiến hoá riêng biệt cho từng kênh YouTube/TikTok/Reels được sản xuất bởi **StoryForge Engine**.

---

## 1. Triết Lý Phân Chia Vùng Trí Tuệ (Isolated Intelligence Domain)

- **Core Engine (Mã nguồn & Quy chuẩn kỹ thuật lõi):**
  - Các file chính của source (`AGENTS.md`, `scripts/`, `library/checks.md`, `library/taste.md`, `.agents/skills/`) định nghĩa **các quy chuẩn kỹ thuật phổ quát** áp dụng cho mọi video (pipeline 10 giai đoạn, 1 video duy nhất `out/<slug>.mp4`, 1 thumbnail đúng aspect, karaoke subtext 40ms pre-roll, safe zones, cấm đưa ví dụ cụ thể vào prompt).
  - **Tuyệt đối KHÔNG hardcode quy chuẩn thẩm mỹ hay phong cách riêng của bất kỳ kênh nào vào mã nguồn chính.**

- **Channel Workspace (Thư mục độc lập cho từng kênh):**
  - Mỗi kênh sở hữu một thư mục riêng: `channels/<channel-slug>/`.
  - Toàn bộ bản sắc thương hiệu, bảng màu, typography, persona giọng đọc, công thức kịch bản và **đặc biệt là bài học feedback (`taste.md`)** được lưu trữ độc lập tại thư mục của kênh đó.
  - Phản hồi từ người dùng cho một video cụ thể sẽ được ghi trực tiếp vào `channels/<channel-slug>/taste.md`, hoàn toàn không gây ô nhiễm (no cognitive bleed) sang các kênh khác hay source tổng.

---

## 2. Cấu Trúc Thư Mục Một Kênh Chuẩn (`channels/<channel-slug>/`)

Mỗi kênh bao gồm 6 tài liệu markdown chuẩn hoá, ánh xạ 1:1 với vai trò của từng AI Agent:

```
channels/<channel-slug>/
├── blueprint.md          # Tổng quan định vị kênh, bio, keywords, danh sách phát (sf-director)
├── style-bible.md        # Bảng màu hex nhận diện, ánh sáng, typography, karaoke colors (sf-visual)
├── narrative-dna.md      # Công thức kịch bản, cấu trúc nhịp độ, pinned comment trap (sf-script)
├── thumbnail-system.md   # Prompt template thuần trừu tượng, safe margin, visual hooks (youtube-thumbnail)
├── voice-profile.md      # Audio persona, tốc độ đọc, pause calibration (sf-audio)
└── taste.md              # Bài học feedback & quy tắc thẩm mỹ riêng tiến hoá qua từng video (sf-learn)
```

Ngoài ra, ở thư mục gốc `channels/` có thể lưu file symlink/index `channels/<channel-slug>.md` trỏ vào thư mục kênh để tương thích ngược.

---

## 3. Tạo Kênh Mới

Để tạo một kênh mới, chỉ cần sao chép toàn bộ thư mục mẫu `channels/_template/`:

```bash
cp -r channels/_template channels/<tên-kênh-mới>
```

Sau đó điền thông tin vào 6 file markdown tương ứng.

---

## 4. Danh Sách Kênh Hiện Tại

| Kênh | Thư Mục | Ngách Nội Dung | Thị Trường |
| :--- | :--- | :--- | :--- |
| **The Grey Verdict** | [`channels/the-grey-verdict/`](the-grey-verdict/) | Tranh chấp pháp lý, lỗ hổng doanh nghiệp & nghịch lý đạo đức | US/UK/CA/AU (Tier-1) |
| **_template** | [`channels/_template/`](_template/) | Thư mục mẫu khởi tạo kênh mới | Chuẩn hoá đa kênh |
