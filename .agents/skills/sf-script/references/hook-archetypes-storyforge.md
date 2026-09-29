# 10 Hook Archetypes for StoryForge AI Video Pipeline

Tài liệu này định nghĩa 10 dạng Hook kinh điển từ các nhà sáng tạo video ngắn hàng đầu thế giới (Kallaway, Hormozi, MrBeast, Brunson, Koe, Welsh...), được chuyển hóa riêng cho **AI Video Pipeline của StoryForge**.

---

## Cấu Trúc 3 Lớp Bắt Buộc (3-Layer AI Hook)

Trong StoryForge, hook không chỉ là một câu nói. Hook là **sự va chạm đồng thời của 3 giác quan trong 1.5 giây đầu tiên**:

1. **Verbal Hook (Thính giác):** Câu thoại mở đầu đọc bởi Kokoro TTS. Tối đa 8–15 từ (khoảng 1.2s – 1.8s theo tốc độ 12.92 ký tự/giây). Cắt bỏ mọi từ đệm, đi thẳng vào xung đột.
2. **Visual Hook (Thị giác):** Prompt ảnh slide 1 sinh bởi ComfyUI. Phải thể hiện **hành động dở dang (frozen action)**, ánh mắt đối kháng, góc máy kịch tính (macro close-up hoặc Dutch angle), ánh sáng có độ tương phản cao (chiaroscuro). TUYỆT ĐỐI không dùng ảnh chân dung tạo dáng bình thường.
3. **Text Hook (Nhận thức bổ trợ):** Đoạn chữ xuất hiện trên màn hình (caption nổi bật). **Không được sao chép y hệt câu nói**, mà phải cung cấp bối cảnh bổ sung, con số hoặc câu hỏi kích thích mắt đọc trước khi tai nghe kịp.

---

## Danh Mục 10 Hook Archetypes

### 1. The Curiosity Gap (Khoảng Trống Tò Mò)
*Nguyên lý:* Tiết lộ kết quả phi lý nhưng giấu kín nguyên nhân, khiến người xem cảm thấy khó chịu nếu không xem tiếp để giải đáp.
- **Ví dụ Fiction:**
  - *Verbal:* "Cả làng tưởng cậu bé chết đuối, cho đến khi thấy bóng nó cầm đèn đi dưới đáy sông."
  - *Visual:* `A cinematic wide shot of a misty river at night, a glowing red star lantern shining from deep beneath the dark water surface, ripples glowing eerily, atmospheric oil painting style, mysterious mood.`
  - *Text Hook:* "Bí mật 10 năm trước ở bến sông Đăm"
- **Ví dụ Factual:**
  - *Verbal:* "Có một căn phòng ở Thụy Sĩ mà bất kỳ ai bước vào quá 45 phút đều bắt đầu phát điên."
  - *Visual:* `Extreme wide shot inside an anechoic chamber, fiberglass acoustic wedges covering walls, floor, and ceiling, a single solitary wooden chair in the dead center under cold dim light, photorealistic, eerie silence.`
  - *Text Hook:* "Căn phòng yên tĩnh nhất hành tinh (-9.4 dBA)"

---

### 2. Direct Challenge / Contrarian (Phản Trực Giác / Thách Thức Niềm Tin)
*Nguyên lý:* Tấn công trực diện vào một niềm tin mà người xem coi là chân lý hiển nhiên.
- **Ví dụ Fiction:**
  - *Verbal:* "Đừng bao giờ tin lời người tốt nhất trong gia đình bạn."
  - *Visual:* `Over-the-shoulder shot looking at an elderly kind grandmother smiling warmly at the camera, while her hand under the wooden dining table quietly slips a packet of white powder into a tea tin, dramatic shadows.`
  - *Text Hook:* "Bữa cơm tối cuối cùng của dòng họ Vũ"
- **Ví dụ Factual:**
  - *Verbal:* "Uống 2 lít nước mỗi ngày thực ra là lời nói dối tiếp thị trắng trợn nhất thế kỷ 20."
  - *Visual:* `Dynamic macro shot of a clear plastic water bottle violently crushing under immense pressure, water splashing aggressively, harsh studio lighting, high contrast.`
  - *Text Hook:* "Sự thật về con số 2L nước bác sĩ chưa từng nói"

---

### 3. High Stakes / Immediate Danger (Hiểm Họa Cận Kề)
*Nguyên lý:* Đặt nhân vật hoặc người xem vào ranh giới sinh tử, đếm ngược thời gian hoặc mất mát không thể vãn hồi.
- **Ví dụ Fiction:**
  - *Verbal:* "Bình oxy chỉ còn đúng 3 phút, nhưng van xả bên ngoài đã bị ai đó khóa chặt."
  - *Visual:* `Close-up shot of an analog oxygen pressure gauge with the needle trembling in the critical red zone, frost covering the cracked glass face, underwater diving helmet reflection, hyper-realistic, tense atmosphere.`
  - *Text Hook:* "3 phút trước khi buồng lặn cạn khí"
- **Ví dụ Factual:**
  - *Verbal:* "Nếu thấy con vật có đốm xanh này nổi trên mặt nước, bạn chỉ có 60 giây để chạy trốn."
  - *Visual:* `Vibrant macro shot of a tiny blue-ringed octopus resting on shallow beach sand, iridescent glowing neon blue rings pulsating with warning colors, crystal clear water, dangerous and sharp.`
  - *Text Hook:* "Nọc độc gấp 1.000 lần xyanua"

---

### 4. The Unbelievable Fact (Sự Thật Khó Tin Nhưng Có Thật)
*Nguyên lý:* Đưa ra một dữ kiện thật 100% nhưng kỳ lạ đến mức người xem phải xem để xác minh AI có nói bừa hay không.
- **Ví dụ Fiction:**
  - *Verbal:* "Mỗi đêm rằm tháng Tám, bức tượng đồng trong đình làng lại nặng thêm đúng 3 cân."
  - *Visual:* `Atmospheric low-angle shot inside a traditional Vietnamese ancient village temple, incense smoke curling around a centuries-old bronze deity statue glowing in candle light, dark dramatic shadows, cinematic tone.`
  - *Text Hook:* "Bí mật bên trong pho tượng làng gốm"
- **Ví dụ Factual:**
  - *Verbal:* "Cá mập đã tồn tại trên Trái Đất trước cả khi những cái cây đầu tiên mọc lên."
  - *Visual:* `Epic cinematic composition split between primeval prehistoric ocean with a massive ancient shark swimming below, and barren rocky land with zero trees under a prehistoric sky, dramatic lighting.`
  - *Text Hook:* "400 triệu năm: Cá mập già hơn cả cây cối"

---

### 5. In Media Res (Ném Thẳng Vào Giữa Cao Trào)
*Nguyên lý:* Bắt đầu câu chuyện ở khoảnh khắc hỗn loạn, kịch tính nhất rồi mới quay lại giải thích tại sao đến nông nỗi này.
- **Ví dụ Fiction:**
  - *Verbal:* "Tiếng còi cảnh sát hú vang ngay trước cổng, và trên tay Thắng là chiếc đèn ông sao dính đầy máu."
  - *Visual:* `Dynamic Dutch angle shot of a teenager running through a rain-drenched alley at night, blue and red police siren lights reflecting on puddles, clutching a tattered star lantern, terrified expression.`
  - *Text Hook:* "22:15 đêm Trung Thu"
- **Ví dụ Factual:**
  - *Verbal:* "Chuông báo động hạt nhân rú liên hồi, và vị chỉ huy chỉ có 90 giây để quyết định nhấn nút hủy diệt thế giới."
  - *Visual:* `Gritty close-up inside a 1980s Soviet nuclear bunker, flashing red emergency strobe lights illuminating a trembling hand hovering inches above a massive red launch button, sweat glistening, high grain film style.`
  - *Text Hook:* "Ngày Trái Đất suýt biến mất: 26/09/1983"

---

### 6. Secret / Insider Knowledge (Bí Mật Ngành / Thông Tin Cấm)
*Nguyên lý:* Khơi gợi tâm lý muốn biết điều mà đám đông bị che giấu hoặc đặc quyền của giới tinh hoa.
- **Ví dụ Fiction:**
  - *Verbal:* "Thợ làm pháo cổ truyền có một lời thề: Tuyệt đối không bao giờ châm que diêm thứ ba."
  - *Visual:* `Intense close-up of aged wrinkled hands binding black gunpowder into red paper tubes, a lit oil lamp flickering dangerously close, smoke wafting, gritty chiaroscuro lighting.`
  - *Text Hook:* "Lời nguyền của làng pháo Bình Đà"
- **Ví dụ Factual:**
  - *Verbal:* "Lý do các hãng sòng bạc không bao giờ lắp đồng hồ và cửa sổ là để đánh cắp não bộ của bạn."
  - *Visual:* `Endless perspective shot of a sprawling luxury casino floor, rows of dazzling flashing slot machines, ornate carpet, no windows visible anywhere, disorienting neon lights, hyper-detailed.`
  - *Text Hook:* "Cạm bẫy tâm lý học sòng bạc"

---

### 7. Before / After Contrast (Đối Lập Cực Đoan Quá Khứ - Hiện Tại)
*Nguyên lý:* Đặt hai trạng thái tương phản gay gắt cạnh nhau khiến người xem khao khát tìm hiểu con đường chuyển hóa ở giữa.
- **Ví dụ Fiction:**
  - *Verbal:* "Năm 10 tuổi, nó nhặt từng thanh tre thừa để xin vào đoàn múa lân. Mười năm sau, nó sở hữu cả đoàn lân lớn nhất Chợ Lớn."
  - *Visual:* `Cinematic split screen or atmospheric montage: on the left a barefoot ragged boy watching a lion dance in rain; on the right a powerful charismatic troupe leader in golden lion costume commanding a roaring crowd.`
  - *Text Hook:* "Từ đứa trẻ nhặt rác đến ông vua múa lân"
- **Ví dụ Factual:**
  - *Verbal:* "Nơi từng là vùng biển rộng lớn thứ 4 thế giới giờ chỉ còn là một bãi sa mạc đầy xác tàu rỉ sét."
  - *Visual:* `Stunning epic landscape of rusty abandoned cargo ships stranded in the middle of vast cracked dry desert sand, dramatic sunset, moody cinematic post-apocalyptic feeling.`
  - *Text Hook:* "Thảm họa biển Aral: Biến mất sau 40 năm"

---

### 8. Big Numbers / Absurd Scale (Con Số Gây Choáng Ngợp)
*Nguyên lý:* Kích thích trí tò mò bằng quy mô khổng lồ không tưởng hoặc tỷ lệ chọi vô lý.
- **Ví dụ Fiction:**
  - *Verbal:* "Ba nghìn người dân làng Vạn Phúc chỉ đồng lòng giữ kín duy nhất một điều trong suốt 100 năm."
  - *Visual:* `Aerial high-angle shot of hundreds of villagers in traditional attire holding glowing red paper lanterns standing silently around an ancient banyan tree in total darkness, haunting and cinematic.`
  - *Text Hook:* "3.000 người và 1 bí mật trăm năm"
- **Ví dụ Factual:**
  - *Verbal:* "Người đàn ông này đã bán tháp Eiffel không phải một lần, mà tận hai lần để bỏ túi hàng triệu đô la."
  - *Visual:* `Vintage 1920s Paris atmosphere, a stylish con artist in tailored suit and fedora holding blueprint documents, with the iconic Eiffel Tower looming majestically in background, sepia toned film noir.`
  - *Text Hook:* "Victor Lustig: Kẻ lừa đảo vĩ đại nhất lịch sử"

---

### 9. Question with High Stakes (Câu Hỏi Chạm Nỗi Đau / Nghịch Lý)
*Nguyên lý:* Đặt câu hỏi mà câu trả lời có thể thay đổi cách người xem nhìn nhận bản thân hoặc tương lai của họ.
- **Ví dụ Fiction:**
  - *Verbal:* "Nếu phải chọn giữa việc cứu cha mình và cứu bí mật của cả làng, bạn sẽ đốt chiếc đèn nào?"
  - *Visual:* `Medium close-up of a young boy standing in pouring rain, holding a lit torch in one hand looking toward a burning storehouse, tears mixing with rain on his face, agonizing moral dilemma.`
  - *Text Hook:* "Lựa chọn nghiệt ngã đêm trăng rằm"
- **Ví dụ Factual:**
  - *Verbal:* "Bạn có bao giờ tự hỏi tại sao chúng ta nhớ như in một bài hát vô nghĩa từ 10 năm trước, nhưng lại quên sạch bài học hôm qua?"
  - *Visual:* `Surrealistic artistic visual of a glowing translucent human brain with colorful glowing memory threads sparking dynamically, surrounded by floating musical notes and fading books, cinematic lighting.`
  - *Text Hook:* "Hiệu ứng sâu tai (Earworm) của não bộ"

---

### 10. The Micro-Story Hook (Mồi Câu Truyện Vi Mô 3 Giây)
*Nguyên lý:* Kể trọn vẹn một tiểu câu chuyện có mở đầu, xung đột và mất mát chỉ trong 1 câu duy nhất.
- **Ví dụ Fiction:**
  - *Verbal:* "Tôi đã làm chiếc đèn ông sao này ròng rã suốt 3 tháng, chỉ để đặt lên nấm mộ của người bạn thân nhất."
  - *Visual:* `Gentle emotional close-up shot of a beautifully crafted colorful star lantern gently resting against a mossy weathered gravestone on a misty grassy hill, morning dew, soft golden hour sunlight, touching and melancholic.`
  - *Text Hook:* "Món quà Trung Thu muộn 1 năm"
- **Ví dụ Factual:**
  - *Verbal:* "Năm 1903, hai anh em thợ sửa xe đạp đã bay lên bầu trời trong 12 giây, và vĩnh viễn thay đổi lịch sử nhân loại."
  - *Visual:* `Historical recreation of the Wright Brothers Flyer gliding low over sand dunes at Kitty Hawk, wind blowing sand, vintage black and white film aesthetic with crisp details.`
  - *Text Hook:* "12 giây định hình cả thế kỷ 20"
