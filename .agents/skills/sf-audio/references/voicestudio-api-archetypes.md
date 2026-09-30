# Tài Liệu API: GET /archetypes (VoiceStudio Catalog Search)

Endpoint tra cứu và lọc danh mục hơn 1.100 giọng nói mẫu (Voice Archetypes) trong VoiceStudio engine.

- **Base URL:** `http://127.0.0.1:3900`
- **Method:** `GET`
- **Path:** `/archetypes`
- **Header:** `Accept: application/json`

---

## 1. Tổng Quan Về Query Filter

Endpoint này hỗ trợ tổng cộng **11 Query Parameters** (gồm **9 bộ lọc nghiệp vụ / facet** và **2 tham số phân trang**).

### Bảng Tổng Hợp 11 Query Parameters

| # | Tên Tham Số | Kiểu Dữ Liệu | Mặc Định | Ràng Buộc / Giá Trị Hợp Lệ | Mô Tả Chức Năng |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | `q` | `string` | `null` | Chuỗi tự do | Tìm kiếm toàn văn (free-text substring match) trên `name` và `instruct`. Cho phép tìm kiếm bất kỳ từ khóa nào trong hơn 1.100 giọng. |
| 2 | `use_case` | `string` | `null` | 7 giá trị danh mục | Lọc theo 1 trong 7 thể loại ứng dụng: `narration`, `informative`, `conversational`, `social`, `entertainment`, `advertisement`, `characters`. |
| 3 | `gender` | `string` | `null` | `male` \| `female` | Lọc theo giới tính sinh học của giọng đọc. |
| 4 | `age` | `string` | `null` | 5 nhóm tuổi | Lọc theo độ tuổi: `child`, `teenager`, `young adult`, `middle-aged`, `elderly`. |
| 5 | `pitch` | `string` | `null` | 5 mức cao độ | Lọc theo cao độ âm vực: `very low pitch`, `low pitch`, `moderate pitch`, `high pitch`, `very high pitch`. |
| 6 | `accent` | `string` | `null` | 10+ chất giọng | Lọc theo chất giọng / phương ngữ: `american accent`, `british accent`, `australian accent`, `canadian accent`, `chinese accent`, `indian accent`, `japanese accent`, `korean accent`, `portuguese accent`, `russian accent`. |
| 7 | `whisper` | `boolean` | `null` | `true` \| `false` | Lọc giọng thì thầm (ASMR / bí ẩn). |
| 8 | `lang` | `string` | `null` | Tên ngôn ngữ | Lọc theo ngôn ngữ gốc của mẫu giọng (`English`, `Chinese`, `French`, `German`, `Italian`, `Portuguese`, `Russian`, `Hindi`, `Japanese`, `Korean`,...). |
| 9 | `featured` | `boolean` | `null` | `true` \| `false` | Lọc các giọng tuyển chọn cao cấp được gắn nhãn tinh chỉnh đặc biệt. |
| 10 | `limit` | `integer` | `60` | `1 <= limit <= 500` | Số lượng bản ghi tối đa trả về trên 1 lần gọi (hỗ trợ tối đa lên đến 500). |
| 11 | `offset` | `integer` | `0` | `offset >= 0` | Vị trí bắt đầu bản ghi (phân trang). |

---

## 2. Chi Tiết Giá Trị Các Bộ Lọc (Facet Values)

### 2.1. `use_case` (7 Thể loại ứng dụng)
- `narration`: Kể chuyện, phim tài liệu, lịch sử, khoa học, tự sự, sách nói.
- `informative`: Tin tức, bài giảng kiến thức, phân tích tài chính/kinh tế.
- `conversational`: Podcast tâm sự, phỏng vấn, đối thoại bạn bè.
- `social`: Mạng xã hội sôi động, TikTok / Reels / Shorts năng lượng cao.
- `entertainment`: Gameshow, bình luận viên thể thao, MC giải trí.
- `advertisement`: TVC quảng cáo thương mại, giới thiệu thương hiệu sang trọng.
- `characters`: Lồng tiếng nhân vật game, phim hoạt hình, quái vật, dị nhân.

### 2.2. `pitch` (5 Mức cao độ âm thanh)
- `very low pitch`: Trầm sâu, điện ảnh, bí ẩn, trang nghiêm.
- `low pitch`: Trầm ấm, điềm đạm, đáng tin cậy.
- `moderate pitch`: Tự nhiên, rõ ràng, dứt khoát.
- `high pitch`: Tươi sáng, nhiệt huyết, sôi nổi.
- `very high pitch`: Rất cao, hoạt hình ngộ nghĩnh.

### 2.3. `age` (5 Nhóm tuổi)
- `child`: Trẻ em.
- `teenager`: Thiếu niên (học đường).
- `young adult`: Thanh niên 20–35 tuổi (podcast, vlog, tech).
- `middle-aged`: Trung niên 35–55 tuổi (chuyên gia, tài liệu, tin tức).
- `elderly`: Người già trên 55 tuổi (thông thái, cổ tích, lịch sử).

---

## 3. Cấu Trúc Dữ Liệu Trả Về (Response Schema)

### Thành công: `200 OK`
```json
{
  "total": 1126,
  "limit": 60,
  "offset": 0,
  "items": [
    {
      "id": "feat_01_the_documentarian",
      "name": "The Documentarian",
      "icon": "Mic",
      "use_case": "narration",
      "instruct": "male, middle-aged, low pitch, american accent",
      "attrs": {
        "Gender": "male",
        "Age": "middle-aged",
        "Pitch": "low pitch",
        "Style": "Auto",
        "EnglishAccent": "american accent",
        "ChineseDialect": "Auto"
      },
      "facets": {
        "gender": "male",
        "age": "middle-aged",
        "pitch": "low pitch",
        "accent": "american accent",
        "whisper": false,
        "lang": "English"
      },
      "sample_script": "The valley had been quiet for a hundred years...",
      "preview_url": null,
      "is_featured": true,
      "language": "English"
    }
  ]
}
```

---

## 4. Ví Dụ Truy Vấn Thực Tế

### Ví dụ 1: Tìm giọng nam tài liệu trầm ấm chuẩn Mỹ
```bash
curl -s "http://127.0.0.1:3900/archetypes?use_case=narration&gender=male&pitch=low%20pitch&accent=american%20accent&limit=10"
```

### Ví dụ 2: Tìm giọng thì thầm huyền bí (Whisper / ASMR)
```bash
curl -s "http://127.0.0.1:3900/archetypes?whisper=true&gender=female&limit=10"
```

### Ví dụ 3: Tìm kiếm tự do theo từ khóa
```bash
curl -s "http://127.0.0.1:3900/archetypes?q=documentary&limit=20"
```

### Ví dụ 4: Lấy tối đa 500 giọng để Agent phân tích tự động
```bash
curl -s "http://127.0.0.1:3900/archetypes?use_case=narration&limit=500"
```
