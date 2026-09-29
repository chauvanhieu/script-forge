# Gate 1 Rubric (All Must Pass)

Một kịch bản đạt chuẩn bàn giao của `sf-script` bắt buộc phải vượt qua toàn bộ 14 tiêu chí kiểm duyệt dưới đây (bao gồm 9 tiêu chí Kỹ thuật cơ bản và 5 tiêu chí Viral Readiness).

---

## Phần A: Tiêu Chí Kỹ Thuật Cơ Bản (Technical Baseline)

1. **Hook:** Line 1 creates a question, mystery, or stake within ~1.5 s of speech (theo tốc độ đọc chuẩn `calibration.json`).
2. **Arc:** Cấu trúc setup → turn → resolution hoàn chỉnh trong thời lượng video; câu kết hạ cánh vững chãi ở dòng thoại cuối.
3. **Length:** Ước tính thời lượng (theo công thức budget formula) nằm trong phạm vi ±5 % của `target_seconds`.
4. **Native Language:** Đọc tự nhiên như người bản xứ viết; dấu thanh chuẩn xác tiếng Việt; tuyệt đối không có giọng văn dịch thuật (translationese).
5. **TTS-Ready:** Không có chỉ dẫn sân khấu trong lời thoại, số và ký hiệu phải được viết bằng chữ như khi đọc, chỉ dùng các thẻ hợp lệ (`[pause]`, `[pause 500ms]`, `[[written|spoken]]`).
6. **Captions:** Không có dòng thoại nào cần quá ~3 caption cues (Định dạng 9:16: ≤ 18 ký tự mỗi hàng, tối đa 2 hàng).
7. **Slides:** Mỗi slide là một khoảnh khắc vẽ được (one drawable moment); hai slide liên tiếp không được trùng lặp bối cảnh, tư thế hoặc góc máy.
8. **Canon Trace:** Mọi slide `source` đều tồn tại trong canon; thoại phải khớp với sự kiện trong canon (với fiction).
9. **Taste & Checks Rules:** Thỏa mãn 100% các quy tắc trong `library/taste.md` (thuộc scope `script`, ngôn ngữ, thể loại) và không phạm các lỗi trong `library/checks.md`.

---

## Phần B: Tiêu Chí Viral Readiness (Bắt Buộc - Vyral Framework)

10. **Định Danh Hook Archetype:** Kịch bản phải khai báo rõ loại Hook được sử dụng trong `story.json` (thuộc 1 trong 10 dạng chuẩn trong `hook-archetypes-storyforge.md`).
11. **Đồng Bộ 3 Lớp Hook (3-Layer AI Hook):**
    - *Verbal Hook:* Dưới 1.5s đầu, câu thoại sắc bén, giật nảy sự chú ý.
    - *Visual Hook:* Prompt ảnh slide 1 thể hiện khoảnh khắc hành động lửng lơ (frozen action), góc máy kịch tính, tương phản cao, không có chữ thừa.
    - *Text Hook:* Có trường `text_hook` chứa câu chữ xuất hiện nổi bật trên màn hình, mang tính bổ trợ thông tin thay vì lặp lại y nguyên câu nói.
12. **Nguyên Lý Leo Thang (Escalation Rule):** Mọi bước chuyển giữa các slide phải được gắn kết bằng quan hệ nhân quả *"Nhưng..."* (xung đột) hoặc *"Vì thế..."* (hệ quả). Loại bỏ 100% cấu trúc kể chuyện liệt kê *"Và rồi..."*.
13. **Payoff Thỏa Mãn Lời Hứa (Promise Fulfilled):** Cao trào và đoạn kết của câu chuyện phải giải quyết trọn vẹn sự tò mò hoặc lời hứa đã gieo ở giây đầu tiên. Tuyệt đối không clickbait lừa dối người xem.
14. **Single-Action CTA & Platform Fit:** Lời kêu gọi hành động duy nhất, nhắm trúng chỉ số mục tiêu của nền tảng (Share / Save / Comment / Loop) theo tài liệu `platform-tuning.md`. Cấm dùng CTA gộp nhiều hành động.
