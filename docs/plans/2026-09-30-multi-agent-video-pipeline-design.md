# StoryForge Multi-Agent Pipeline & Zero-Drift Video Production Design

- **Date:** 2026-09-30
- **Status:** Validated & Approved via `/brainstorming`
- **Scope:** Architecture & Execution of `/create-video` in StoryForge

---

## 1. Executive Summary & Root Cause Analysis

### Vấn đề thực tế phát hiện:
1. **Agent vẫn đọc dữ liệu `projects/` cũ:**
   - Trong `.agents/skills/sf-script/SKILL.md` (dòng 37) tồn tại chỉ thị yêu cầu copy cấu trúc từ `projects/den-ong-sao/story.json` hoặc `projects/smoke-test/story.json`.
   - Hệ thống thiếu công cụ scaffolding (`sf_init.py`), khiến Agent phải tìm đến các file `story.json` cũ để tham khảo mẫu.
2. **Quá trình sinh ảnh Gemini 3.1 Flash Image bị chậm và tuần tự:**
   - Dù Agent gọi tool `generate_image` song song trong 1 message, backend của IDE vẫn thực thi tuần tự các tool call (~10–14s / ảnh).
   - Agent chia 24 ảnh thành 4 lượt hội thoại (turns) riêng rẽ, mỗi lượt 6 ảnh, dẫn đến việc phải chờ đợi qua 4 vòng suy nghĩ và phản hồi (~5 phút).
   - Sau khi sinh ảnh xong, Agent phải mất thêm nhiều lượt viết code Python thủ công để di chuyển file từ thư mục brain sang `projects/<slug>/images/`, băm sha256 và cập nhật `story.json`.

---

## 2. Decision Log (Nhật ký quyết định)

| STT | Quyết định | Các phương án đã cân nhắc | Lý do chọn |
|---|---|---|---|
| 1 | **Mô hình Assembly Line 4 Vai Trò** | Option 1 (Assembly Line), Option 2 (Divide & Conquer), Option 3 (Engine-heavy CLI) | Đảm bảo tính chuyên trách cao nhất, luồng rõ ràng, dễ bảo trì và mở rộng. |
| 2 | **100% Zero-API-Key ngoài** | Hướng A (Dùng Gemini API qua Google AI Studio key), Hướng B (Dùng tool nội bộ IDE) | Tiết kiệm chi phí, không phụ thuộc cấu hình môi trường bên ngoài, an toàn bảo mật. |
| 3 | **Giữ nguyên mật độ 20–26 ảnh** | Giảm xuống 8 Keyframe + Zoom, Giữ nguyên 20-26 ảnh | Người dùng yêu cầu giữ độ phong phú thị giác và chuyển cảnh nhanh (1.5s–2.5s) cho video viral. |
| 4 | **Single-Turn Mega-Batch + Auto-Sync** | Chia nhiều batch 6 ảnh trong chat, Viết code copy thủ công | Gom toàn bộ tool call vào 1 turn duy nhất và dùng script `sf_sync_gemini_images.py` để xử lý file trong 1 giây. |
| 5 | **Scaffolding độc lập** | Đọc project cũ, Đọc story.schema.json, Chạy `sf_init.py` | Tạo ngay khung rỗng chuẩn schema, cấm 100% việc đọc `projects/`. |

---

## 3. Kiến Trúc Multi-Agent Chi Tiết (Architecture)

### 3.1. Các Vai Trò Chuyên Biệt

1. **`sf-script` (Script & Story Specialist):**
   - Chạy `uv run scripts/sf_init.py projects/<slug>` để khởi tạo thư mục và skeleton `story.json`.
   - Tuyệt đối không gọi `list_dir` hoặc `view_file` trên `projects/`.
   - Viết kịch bản `script.md` và điền 20–26 lines & visual prompts vào `story.json`.
   - Tự động validate bằng `uv run scripts/sf_validate.py projects/<slug>`.

2. **`sf-director` (Pipeline Conductor & Gatekeeper):**
   - Chấm 14 tiêu chí rubric Gate 1 (Kỹ thuật + Viral Readiness).
   - Khi Gate 1 thông qua, kích hoạt nhánh sản xuất song song (Parallel Production).
   - Kiểm duyệt Gate 2 (Contact sheet).

3. **`sf-audio` (Voice & Audio Specialist):**
   - Quản lý casting giọng qua VoiceStudio (port 3900).
   - Chạy ngầm `uv run scripts/sf_voice.py projects/<slug>` dưới dạng background task.
   - Giám sát tiến độ và kiểm tra lỗi phát âm/CER/CPS.

4. **`sf-visual` (Visual & Image Specialist):**
   - Tiếp nhận danh sách prompts từ `story.json`.
   - Gửi **Mega-Batch tool call `generate_image`** cho toàn bộ 20–26 slide trong **1 turn duy nhất**.
   - Chạy `uv run scripts/sf_sync_gemini_images.py projects/<slug>` để đồng bộ ảnh ngay khi batch hoàn tất.

5. **`sf-assembly` (Finisher & Packaging Specialist):**
   - Chạy căn chỉnh: `sf_align.py`.
   - Đóng phụ đề karaoke highlight: `sf_captions.py`.
   - Render video tăng tốc phần cứng: `sf_render.py`.
   - QC toàn diện: `sf_qc.py` và học lỗi: `sf_learn.py`.
   - Tạo thumbnail viral 9:16 và 16:9 theo skill `youtube-thumbnail`.
   - Xuất Publishing Package hoàn chỉnh (Tiêu đề, Mô tả, Hashtags, Pinned Comment).

---

## 4. Đặc Tả Các Công Cụ Bổ Sung (Tooling Specs)

### 4.1. `scripts/sf_init.py`
- **Mục đích:** Khởi tạo cấu trúc dự án mới mà không cần tham chiếu bất kỳ dự án cũ nào.
- **Đầu vào:** `projects/<slug>` và `--type` (mặc định `factual`).
- **Nhiệm vụ:**
  - Tạo các thư mục con: `audio/`, `images/`, `clips/`, `logs/`, `out/`, `prompts/`.
  - Tạo file `story.json` đầy đủ các trường bắt buộc theo `schemas/story.schema.json`.
  - Tạo file `script.md` mẫu chứa sẵn khung các phần.

### 4.2. `scripts/sf_sync_gemini_images.py`
- **Mục đích:** Tự động hóa khâu hậu kỳ ảnh sinh từ tool `generate_image` của IDE.
- **Đầu vào:** `projects/<slug>`.
- **Nhiệm vụ:**
  - Quét tìm các file ảnh đã sinh trong thư mục brain của conversation hiện tại (`~/.gemini/antigravity-ide/brain/<convo-id>/<slug>_s*.jpg`).
  - Convert từ JPG sang PNG, resize về đúng chuẩn (1080x1920 cho 9:16 hoặc 1920x1080 cho 16:9).
  - Lưu vào `projects/<slug>/images/S01.png` ... `S24.png`.
  - Tính SHA256 `input_hash` của từng ảnh và cập nhật `story.json` với trạng thái `status: "done"`.
  - Tự động gọi `sf_contact_sheet.py` để tạo `out/contact_sheet.png`.

---

## 5. Cập Nhật Quy Tắc Hệ Thống (Rules & Skills Update)

1. **`AGENTS.md`:**
   - Cập nhật quy tắc: Khi tạo video mới, Agent bắt buộc chạy `sf_init.py`, tuyệt đối không đọc thư mục `projects/`.
   - Bổ sung hướng dẫn: Khi sinh ảnh qua Gemini trong IDE, phát lệnh Mega-Batch cho tất cả slides trong 1 turn, sau đó chạy `sf_sync_gemini_images.py`.
2. **`.agents/skills/sf-script/SKILL.md`:**
   - Xóa bỏ câu lệnh tham chiếu tới `projects/den-ong-sao/story.json`.
3. **`.agents/skills/sf-visual/SKILL.md`:**
   - Thêm quy chuẩn đặt tên ảnh theo pattern `<slug>_s01` đến `<slug>_sXX`.
   - Quy định chạy `sf_sync_gemini_images.py` ngay sau khi batch `generate_image` trả về kết quả.
