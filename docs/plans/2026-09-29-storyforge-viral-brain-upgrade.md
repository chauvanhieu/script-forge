# StoryForge Viral Brain Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Nâng cấp "bộ não" sản xuất kịch bản và điều phối của StoryForge bằng cách tích hợp tri thức video ngắn triệu view từ `content-skills` (Vyral Framework), tối ưu hóa retention và thuật toán cho YouTube Shorts, TikTok, Instagram Reels trên cả hai thể loại Fiction và Factual.

**Architecture:** Tích hợp tri thức viral thành các reference documents chuyên sâu được bản địa hóa cho AI video pipeline (3-layer hook: Prompt ảnh + Thoại dẫn nhập + Text overlay), đưa các tiêu chí viral readiness vào Gate 1 Rubric của `sf-script`, bổ sung nền tảng mục tiêu và gói xuất bản (publishing package) vào `sf-director`, đồng thời bảo toàn 100% cơ chế học thẩm mỹ (`taste.md`, `checks.md`) và engine kỹ thuật sẵn có.

**Tech Stack:** StoryForge Agent Skills (Markdown / YAML frontmatter), Python 3.11+ / uv, JSON Schema, Story maintenance tools.

---

### Task 1: Tạo `sf-script/references/viral-storytelling.md`

**Files:**
- Create: `.agents/skills/sf-script/references/viral-storytelling.md`
- Reference: `content-skills/skills/viral-short-form/references/retention.md`

**Step 1: Xác định cấu trúc tài liệu cần đạt**
Tài liệu phải bao gồm:
1. Xương sống giữ chân (Retention Spine): Hook (0-3s) → Escalation (Nhưng / Vì thế) → Payoff → Quick CTA.
2. Quy tắc quan hệ nhân quả South Park: Thay thế liên kết "Và rồi..." (And then) bằng "Nhưng..." (But) và "Vì vậy..." (Therefore).
3. 3 lỗi chí mạng phá vỡ retention (Weak Hook, Flat Escalation, Buried Payoff).
4. Kỹ thuật AI-Video Retention: Open Loops (vòng lặp mở), Dual Narrative (phân bổ thông tin giữa hình ảnh và giọng đọc), Micro-pattern resets mỗi 3-5 giây (chuyển động camera prompt, ngắt nhịp thoại).
5. Hướng dẫn áp dụng riêng biệt cho Fiction (Tâm lý, xung đột) và Factual (Nghịch lý, cơ chế giải thích).

**Step 2: Viết nội dung file `.agents/skills/sf-script/references/viral-storytelling.md`**
Tạo file với đầy đủ các phân tích chuyên sâu và nguyên tắc thực hành cụ thể.

**Step 3: Kiểm tra định dạng và tính rõ ràng**
Đảm bảo file markdown chuẩn xác, không có liên kết hỏng, thuật ngữ tiếng Việt tự nhiên và bám sát kỹ thuật video ngắn.

**Step 4: Commit**
```bash
git add .agents/skills/sf-script/references/viral-storytelling.md
git commit -m "feat(sf-script): add viral storytelling retention reference"
```

---

### Task 2: Tạo `sf-script/references/hook-archetypes-storyforge.md`

**Files:**
- Create: `.agents/skills/sf-script/references/hook-archetypes-storyforge.md`
- Reference: `content-skills/skills/viral-hooks/references/hook-archetypes.md`

**Step 1: Xác định cấu trúc 10 Archetypes được chuyển hóa cho AI Pipeline**
Mỗi archetype phải có 3 thành phần đồng bộ (3-Layer AI Hook):
- `Verbal Hook`: Câu thoại dẫn nhập (< 1.5s, ngắn, giật nảy, kích hoạt tò mò).
- `Visual Hook`: Prompt ảnh slide 1 cho ComfyUI (hành động lửng lơ, góc máy cận kịch tính, cảm xúc mạnh).
- `Text Hook`: Câu text overlay xuất hiện trên màn hình (bổ trợ ngữ cảnh, không lặp lại nguyên văn lời nói).

10 dạng Hook kinh điển gồm:
1. The Curiosity Gap (Khoảng trống tò mò)
2. Direct Challenge / Contrarian (Phản trực giác / Thách thức niềm tin)
3. High Stakes / Immediate Danger (Hiểm họa cận kề / Nguy cơ tức thì)
4. The Unbelievable Fact (Sự thật khó tin nhưng có thật)
5. In Media Res (Ném thẳng vào giữa đỉnh điểm xung đột)
6. Secret / Insider Knowledge (Bí mật ngành / Thông tin nội bộ)
7. Before / After Contrast (Đối lập cực đoan Quá khứ - Hiện tại)
8. Big Numbers / Absurd Scale (Con số gây choáng ngợp)
9. Question with High Stakes (Câu hỏi chạm đúng nỗi đau / tò mò tột độ)
10. The Micro-Story Hook (Mồi câu truyện vi mô 3 giây)

Mỗi archetype phải có ít nhất 2 ví dụ thực tế bằng tiếng Việt: 1 Fiction (truyện hư cấu) và 1 Factual (kiến thức fact).

**Step 2: Viết nội dung file `.agents/skills/sf-script/references/hook-archetypes-storyforge.md`**

**Step 3: Kiểm tra tính khả thi của Visual Hook Prompts với ComfyUI/FLUX**
Đảm bảo các prompt sinh ảnh gợi ý tuân thủ quy chuẩn của `sf-visual` (không chứa text rác, mô tả rõ bố cục, ánh sáng, góc máy).

**Step 4: Commit**
```bash
git add .agents/skills/sf-script/references/hook-archetypes-storyforge.md
git commit -m "feat(sf-script): add 10 AI-adapted hook archetypes with vi examples"
```

---

### Task 3: Tạo `sf-director/references/platform-tuning.md`

**Files:**
- Create: `.agents/skills/sf-director/references/platform-tuning.md`
- Reference: `content-skills/skills/viral-youtube-shorts/`, `viral-tiktok-content/`, `viral-instagram-reels/`, `viral-captions-and-ctas/`

**Step 1: Xác định các quy chuẩn tối ưu hóa theo từng nền tảng**
1. **YouTube Shorts**:
   - Mục tiêu: VVSA (Viewed vs Swiped Away) > 70%, Average Percentage Viewed (APV) > 100%.
   - Kỹ thuật: Seamless Looping (câu kết nối mượt mà vào câu đầu tiên), Nhịp ngắt không để khoảng lặng chết.
   - Chiến lược CTA: Kêu gọi Subscribe kèm lý do rõ ràng hoặc trỏ sang Long-form video liên quan.
2. **TikTok**:
   - Mục tiêu: Completion Rate (100% cho video 15-30s, 70%+ cho video 60s), Comment trigger.
   - Kỹ thuật: Mở nhiều Open Loops nhỏ, chèn chi tiết gây tranh luận nhẹ (Easter egg hoặc câu hỏi mở) để kích thích bình luận.
   - Chiến lược CTA: Kích hoạt bình luận ("Bạn sẽ chọn phe nào?", "Đoán xem chuyện gì xảy ra tiếp?").
3. **Instagram Reels**:
   - Mục tiêu: Sends per Reach > 3% (Lượt chia sẻ qua Direct Message) và Save Rate cao.
   - Kỹ thuật: Giá trị nhận thức cao (Relatability hoặc Value Density) để người xem gửi cho bạn bè hoặc lưu lại nghiền ngẫm.
   - Chiến lược CTA: Kêu gọi chia sẻ ("Gửi video này cho đứa bạn...") hoặc lưu ("Lưu lại khi cần").
   - Caption: Cấu trúc dài, giàu giá trị, bổ sung thông tin chi tiết mà video chưa kịp nói hết.
4. **Bộ mẫu Single-Action CTA & Pinned Comment Blueprint**:
   - Mẫu CTA chuẩn 1 mục tiêu duy nhất theo từng nền tảng.
   - Chiến lược Pinned Comment dẫn dắt thảo luận để thuật toán đẩy video lên For You / Explore.

**Step 2: Viết nội dung file `.agents/skills/sf-director/references/platform-tuning.md`**

**Step 3: Kiểm tra tính đồng bộ với pipeline của StoryForge**

**Step 4: Commit**
```bash
git add .agents/skills/sf-director/references/platform-tuning.md
git commit -m "feat(sf-director): add platform-tuning specs for Shorts, TikTok, Reels"
```

---

### Task 4: Nâng cấp Gate 1 Rubric trong `.agents/skills/sf-script/references/rubric.md`

**Files:**
- Modify: `.agents/skills/sf-script/references/rubric.md`

**Step 1: Rà soát 9 tiêu chí hiện hữu**
Bảo toàn nguyên vẹn 9 tiêu chí: Hook (~1.5s), Arc (setup→turn→resolution), Length (±5%), Native language, TTS-ready, Captions (≤18 chars/row, 2 rows), Slides (drawable moments), Canon trace, Taste rules.

**Step 2: Thêm "Phần B: Tiêu Chí Viral Readiness (Bắt Buộc)"**
Bổ sung các tiêu chí đánh giá chất lượng giữ chân:
10. **Định danh Hook Archetype**: Kịch bản phải ghi chú rõ loại hook sử dụng (thuộc 1 trong 10 archetypes).
11. **Đồng bộ 3 Lớp Hook (3-Layer AI Hook)**:
    - Verbal: Dưới 1.5 giây đầu, kích hoạt tò mò tức thì.
    - Visual: Prompt slide 1 thể hiện rõ khoảnh khắc kịch tính/lửng lơ.
    - Text Hook: Text overlay ngắn gọn trên màn hình bổ trợ ý nghĩa.
12. **Nguyên lý leo thang But/Therefore**: Nhịp nối giữa các slide/sự kiện chuyển tải mối liên hệ "Nhưng..." hoặc "Vì vậy...", không dùng chuỗi kể liệt kê "Và rồi...".
13. **Payoff thỏa mãn lời hứa (Promise Fulfilled)**: Điểm cao trào hoặc kết thúc phải giải đáp thỏa đáng câu hỏi/khoảng trống tò mò đã mở ra ở giây đầu tiên.
14. **Single-Action CTA & Looping**: Lời kêu gọi hành động duy nhất, nhắm trúng chỉ số mục tiêu của nền tảng (Share/Save/Comment) hoặc thiết kế loop liền mạch (đối với Shorts).

**Step 3: Kiểm tra format file `rubric.md`**

**Step 4: Commit**
```bash
git add .agents/skills/sf-script/references/rubric.md
git commit -m "feat(sf-script): add viral readiness criteria to Gate 1 rubric"
```

---

### Task 5: Cập nhật `sf-script/SKILL.md`

**Files:**
- Modify: `.agents/skills/sf-script/SKILL.md`

**Step 1: Rà soát cấu trúc hiện tại của `sf-script/SKILL.md`**
Hiện tại gồm: Inputs, Canon (fiction), Budget, story.json, Gate 1.

**Step 2: Tích hợp Viral Brain Workflow vào `sf-script`**
- Tại mục **Inputs**: Bổ sung tham chiếu `references/viral-storytelling.md`, `references/hook-archetypes-storyforge.md`, và nền tảng mục tiêu từ brief (`platform_target`: `youtube_shorts` | `tiktok` | `instagram_reels`).
- Tại mục **Canon & Script Spine**:
  - Hướng dẫn xây dựng kịch bản theo Retention Spine: Hook (0-3s) → Escalation (Nhưng/Vì thế) → Payoff → Single CTA.
  - Áp dụng kỹ thuật Open Loops và Dual Narrative giữa lời dẫn (narration) và hình ảnh (visual prompt).
- Tại mục **story.json**:
  - Slide 1 bắt buộc có metadata hoặc prompt thể hiện `Visual Hook`.
  - Line 1 phải là `Verbal Hook`, kèm chú thích `text_hook` cho caption overlay.
  - Đảm bảo thời lượng từng câu khớp chuẩn ngân sách `calibration.json` (12.92 ký tự/s).
- Tại mục **Gate 1**:
  - Tự chấm điểm với `references/rubric.md` (cả 9 tiêu chí kỹ thuật và 5 tiêu chí Viral Readiness).

**Step 3: Cập nhật file `.agents/skills/sf-script/SKILL.md`**

**Step 4: Commit**
```bash
git add .agents/skills/sf-script/SKILL.md
git commit -m "feat(sf-script): integrate viral storytelling workflow and schema metadata"
```

---

### Task 6: Cập nhật `sf-director/SKILL.md`

**Files:**
- Modify: `.agents/skills/sf-director/SKILL.md`

**Step 1: Rà soát các Stage của `sf-director/SKILL.md`**
Xác định 3 điểm cần nâng cấp:
1. **Stage 1 (brief)**: Bổ sung trường `platform_target` (mặc định: `youtube_shorts`, hỗ trợ `tiktok`, `instagram_reels`) và thể loại (`fiction` | `factual`).
2. **Stage 3 (Gate 1)**: Đạo diễn chấm điểm `script.md` đối soát với Gate 1 Rubric mở rộng (bao gồm Viral Readiness checks). Nếu phát hiện lỗi trôi tuột, thiếu leo thang hoặc hook yếu, yêu cầu script agent viết lại theo `viral-storytelling.md`.
3. **Stage 9 (report) & Publishing Package**:
   - Ngoài video path và duration, tự động tạo gói xuất bản:
     * Tiêu đề giật tò mò tối ưu theo nền tảng.
     * Caption và danh sách 3-5 hashtags chuẩn ngách.
     * Kịch bản Pinned Comment dẫn dắt thảo luận.
   - Tuân thủ hướng dẫn trong `references/platform-tuning.md`.

**Step 2: Cập nhật file `.agents/skills/sf-director/SKILL.md`**

**Step 3: Commit**
```bash
git add .agents/skills/sf-director/SKILL.md
git commit -m "feat(sf-director): add platform-tuning stage, viral gate 1 check, and publishing package"
```

---

### Task 7: Kiểm thử đối soát kịch bản mẫu qua Gate 1 Rubric mới

**Files:**
- Test/Verify: `stories/den-ong-sao/story.md` (Fiction test case)
- Create Test Report: `tests/reports/gate1-viral-verification.md`

**Step 1: Rà soát kịch bản `stories/den-ong-sao/story.md`**
Đọc và phân tích kịch bản mẫu hiện tại đối chiếu với Gate 1 Rubric mới:
- Kiểm tra Hook 3 lớp (Verbal, Visual prompt, Text overlay).
- Kiểm tra cấu trúc leo thang (But/Therefore vs And then).
- Đánh giá điểm rơi cao trào và payoff.
- Đề xuất bản chỉnh sửa viral (viral-optimized rewrite) cho kịch bản mẫu để làm tiêu chuẩn đối chứng.

**Step 2: Viết báo cáo nghiệm thu kiểm thử `gate1-viral-verification.md`**
Trình bày bảng điểm chi tiết (14 tiêu chí), chỉ ra các điểm đạt/chưa đạt và kịch bản đã được tối ưu hóa theo chuẩn viral mới.

**Step 3: Commit**
```bash
git add tests/reports/gate1-viral-verification.md
git commit -m "test(sf-script): verify Gate 1 viral rubric against sample story"
```

---

### Task 8: Nghiệm thu toàn diện (`/code-review` & `/verify`)

**Files:**
- Review: Tất cả các file đã tạo và sửa đổi trong `.agents/skills/`

**Step 1: Kiểm tra tính tương thích kỹ thuật**
- Chạy thử các công cụ kiểm tra hiện có của StoryForge (nếu có: validate schema, scripts kiểm tra).
- Đảm bảo các file `taste.md`, `checks.md` và `calibration.json` hoàn toàn nguyên vẹn.

**Step 2: Rà soát chất lượng code review**
- Kiểm tra tính chặt chẽ của Markdown, định dạng metadata frontmatter.
- Đảm bảo tính nhất quán về thuật ngữ, vai trò của từng subagent.

**Step 3: Tổng kết và sẵn sàng vận hành**
- Thông báo cho người dùng hệ thống kịch bản StoryForge đã được trang bị "bộ não" viral hoàn chỉnh.
