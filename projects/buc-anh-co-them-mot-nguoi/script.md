# Bức ảnh có thêm một người

## Story summary

Khải một mình nuôi em trai An từ khi mẹ mất mười năm trước. Trên tường phòng khách, tấm ảnh gia
đình cũ vẫn treo đó, vốn chỉ có ba người. Một buổi sáng, Khải sững người thấy trong ảnh có thêm
một bóng người phụ nữ thứ tư — dáng đứng quen thuộc, chính là mẹ. Anh tưởng ai đó chỉnh sửa ảnh để
trêu đùa, nhưng nhìn kỹ hơn thấy bóng dáng mẹ đang chỉ tay lên trần nhà. Ngước lên, Khải phát hiện
một sợi dây điện đang âm ỉ cháy ngay phía trên chỗ An đang ngủ say. Anh vội bế em chạy ra ngoài,
hô hoán gọi người giúp; chỉ vài phút sau khói đen đã tràn ngập căn phòng. Khi mọi việc qua đi, tấm
ảnh được lau lại — bóng người thứ tư đã biến mất. Lật mặt sau khung ảnh, Khải thấy một dòng chữ mẹ
viết từ nhiều năm trước: "Mẹ luôn dõi theo hai anh em." Cú lật: bóng người xuất hiện thêm không
phải điều đáng sợ, mà là lời cảnh báo của người mẹ đã khuất, cứu hai anh em khỏi một vụ cháy do
chập điện.

Canon: `stories/buc-anh-co-them-mot-nguoi` (chapter-01, 6 scenes).

## Cast

| ID | Name | Role | Voice design |
|----|------|------|---------------|
| narrator | Khải | narrator / protagonist (POV) | male, adult, moderate-low pitch, warm and reflective tone |
| C01 | An | supporting (em trai, không lời thoại) | male, child, high pitch (không sử dụng — An không có lời thoại) |

Mẹ (Thư) không có trong `cast`: bà chỉ xuất hiện như một bóng dáng mờ ảo trong tấm ảnh (không lời
thoại, không cần plate riêng) — mô tả trực tiếp trong từng `visual.prompt` để giữ cast tối giản.

## Lines by slide

### S01 — chapter-01-scene-01 · medium · static · beat: setup
- **L001 (narrator):** "Mẹ tôi mất đã mười năm." *(pause 350ms)*
- **L002 (narrator):** "Từ đó, một mình tôi nuôi An, dưới tấm ảnh gia đình cũ — chỉ ba người." *(pause 450ms)*

### S02 — chapter-01-scene-02 · close-up · push_in · beat: question
- **L003 (narrator):** "Sáng nay, tôi sững người: ảnh có thêm một bóng người." *(pause 450ms)*

### S03 — chapter-01-scene-02 · extreme-close · static · beat: reveal
- **L004 (narrator):** "Nhìn kỹ, tôi nhận ra dáng đứng quen thuộc ấy — là mẹ." *(pause 400ms)*
- **L005 (narrator):** "Mẹ đã mất mười năm trước, sao giờ lại xuất hiện trong ảnh?" *(pause 500ms)*

### S04 — chapter-01-scene-03 · medium · pull_out · beat: question
- **L006 (narrator):** "Tôi nghĩ chắc ai đó chỉnh sửa ảnh để trêu chọc mình." *(pause 400ms)*

### S05 — chapter-01-scene-03 · extreme-close · static · beat: reveal
- **L007 (narrator):** "Nhưng nhìn kỹ, mẹ trong ảnh đang chỉ tay lên trần nhà." *(pause 500ms)*

### S06 — chapter-01-scene-04 · medium · push_in · beat: reveal
- **L008 (narrator):** "Tôi ngước lên. Một sợi dây điện trên trần đang âm ỉ cháy." *(pause 500ms)*

### S07 — chapter-01-scene-04 · wide · static · beat: reversal
- **L009 (narrator):** "Ngay phía dưới, An — em tôi — vẫn đang ngủ say." *(pause 500ms)*

### S08 — chapter-01-scene-05 · wide · push_in · beat: emotional
- **L010 (narrator):** "Tôi lao tới, bế thốc An lên, chạy thẳng ra cửa." *(pause 300ms)*
- **L011 (narrator):** "Cháy! Cứu! Có ai không?!" *(pause 400ms)*

### S09 — chapter-01-scene-05 · extreme-wide · pan_left · beat: emotional
- **L012 (narrator):** "Chỉ vài phút sau, khói đen đã tràn ngập cả căn phòng." *(pause 500ms)*

### S10 — chapter-01-scene-06 · medium · push_in · beat: reveal
- **L013 (narrator):** "Lửa được dập, tôi quay vào lau lại tấm ảnh." *(pause 400ms)*
- **L014 (narrator):** "Bóng người thứ tư... đã biến mất, như chưa từng xuất hiện." *(pause 500ms)*

### S11 — chapter-01-scene-06 · extreme-close · static · beat: reveal
- **L015 (narrator):** "Tôi lật mặt sau khung ảnh, thấy một dòng chữ mẹ viết từ rất lâu." *(pause 500ms)*

### S12 — chapter-01-scene-06 · wide · pull_out · beat: resolution
- **L016 (narrator):** "\"Mẹ luôn dõi theo hai anh em.\"" *(pause 600ms)*

## Budget

- Calibration: `vi.chars_per_s = 11.469184063668088` (`library/calibration.json`, 89 lines measured)
- Target: 60s · Σ pause_after_ms = 7250ms (7.25s)
- Budget: (60 − 7.25) × 11.469184063668088 ≈ **605.0 display characters** (no spaces)
- Actual: **620 display characters** (no spaces) → **102.5% of budget** (within the 100–108%,
  never-under aim from K012 — not a symmetric ±5%)
- Estimated spoken duration: 620 / 11.469184063668088 ≈ 54.06s + 7.25s pauses ≈ **61.3s**
  (102.2% of the 60s target — within the Gate 1 rubric's ±5% length check)
- L001 ("Mẹ tôi mất đã mười năm.") is 18 display characters ≈ 1.57s of speech — the immediate hook,
  landing within the rubric's ~1.5s window and stating the stake (loss) directly with no
  scene-setting first.

## Taste rules applied

- **T001** [audio · vi]: L011 ("Cháy! Cứu! Có ai không?!") is the story's one dramatic-peak line —
  written short, fragmented, and punctuation-heavy (three exclamations/question in five words) so
  the urgency reads even though VoiceStudio can't render tone directly.

## Notes for later stages

- **K005 / K009 / K011** are already baked into every slide's `visual.prompt`: the photo and the
  handwritten note are described as indistinct/abstract (no legible text requested anywhere), the
  three- and four-person photo counts are stated explicitly with a distinguishing feature per
  figure, and the ceiling wire prompt explicitly says "no hand or person touching the wire."
- The final line's exact quote ("Mẹ luôn dõi theo hai anh em") is carried by narration/captions
  only — no slide asks the image model to render that sentence as in-image text.
- Mẹ (Thư) has no `cast` entry or voice; she is visual-only (a soft translucent silhouette in the
  photo). If a future gate wants her fingerprinted for consistency across slides, add a
  non-speaking cast entry (e.g. `C02`) with just an `appearance` field.
