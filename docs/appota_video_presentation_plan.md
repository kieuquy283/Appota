# Kế hoạch Video Trình bày Mission 2 — Appota Knowledge Guard

* **Thời lượng tối đa:** 5 phút (Mục tiêu quay thực tế: **4 phút 35 giây – 4 phút 45 giây**, không để sát giờ).
* **Môi trường ghi hình:** Giao diện Web Next.js 14 Enterprise Dark UI (`http://localhost:3000`), kết hợp slide tối giản.
* **Cấu trúc 5 phần bắt buộc:**  
  `Bài toán ➔ Phần chọn để chứng minh ➔ Demo chính ➔ Tình huống khó ➔ Hạn chế`.

---

## 🎯 Thông điệp cốt lõi (Core Takeaway)

> **"FILTER FIRST — AI SECOND"**  
> *Cùng một câu hỏi, hệ thống phải chọn đúng thông tin theo đúng người dùng, đúng đơn vị, đúng quyền và đúng phiên bản tài liệu — trước khi đưa dữ liệu vào LLM.*

---

# 1. BẢNG PHÂN BỔ THỜI LƯỢNG TỔNG THỂ

| Thời lượng | Phân đoạn | Nội dung trọng tâm | Màn hình hiển thị |
|---|---|---|---|
| **0:00 – 0:35** (35s) | **1. Bài toán** | Nguy cơ AI trả lời sai ngữ cảnh, lộ bảng lương, dùng nhầm chính sách công ty khác | Slide Problem |
| **0:35 – 1:05** (30s) | **2. Chọn chứng minh** | Lọc quyền tất định trước khi vào LLM: *Filter First, AI Second* | Slide Architecture |
| **1:05 – 2:30** (85s) | **3. Demo chính** | Cùng câu hỏi khác kết quả (Alice vs Carol) + Chặn dữ liệu mật (Hỏi lương) | Live Web Next.js |
| **2:30 – 3:30** (60s) | **4. Tình huống khó** | Mâu thuẫn văn bản ngang quyền (`CONFLICT`) + Thiếu chứng cứ (`ABSTAIN`) | Live Web Next.js |
| **3:30 – 4:20** (50s) | **5. Hạn chế (Fail Case)** | Câu hỏi ghép đa chủ đề (`TC-M2-07`): Chưa có Query Decomposition & Multi-Topic Routing | Live Web / Slide |
| **4:20 – 4:45** (25s) | **6. Kết luận** | Tổng kết giá trị kiểm chứng: An toàn tri thức là nền tảng của Enterprise AI | Slide Key Takeaway |

---

# 2. KỊCH BẢN CHI TIẾT TỪNG PHÂN ĐOẠN

## PHẦN 1: BÀI TOÁN (0:00 → 0:35) — 35 giây
* **Màn hình:** Slide sơ đồ tổ chức tập đoàn `Appota Demo Group` gồm `AlphaPay` và `NovaGame`.
* **Thông điệp:** `Same Question ≠ Same Answer`.
* **Lời thoại đề xuất:**
  > "Chào anh/chị. Trong một tập đoàn đa công ty thành viên, cùng một câu hỏi chưa bao giờ có cùng một câu trả lời. Một nhân viên tại AlphaPay và một nhân viên tại NovaGame có chính sách nghỉ phép hoàn toàn khác nhau. Thậm chí, bảng lương cấp quản lý tuyệt đối không được phép xuất hiện trước mắt nhân viên thông thường.  
  > Nếu đưa một chatbot AI thông thường vào doanh nghiệp, nguy cơ lớn nhất không phải là câu trả lời chưa hay, mà là **AI tiết lộ bí mật nội bộ** hoặc **áp dụng nhầm chính sách của công ty này cho công ty khác**."

---

## PHẦN 2: PHẦN CHỌN ĐỂ CHỨNG MINH (0:35 → 1:05) — 30 giây
* **Màn hình:** Slide Kiến trúc Pipeline xác định:
  ```
  User Profile ➔ Pre-Retrieval Guard (RBAC/ABAC/Version) ➔ Retrieval ➔ Resolver ➔ LLM ➔ Citation Assertion
  ```
* **Thông điệp:** `FILTER FIRST — AI SECOND`.
* **Lời thoại đề xuất:**
  > "Để giải quyết bài toán này, trong Mission 2 nhóm không cố dựng một chatbot đa năng hay để Autonomous Agent tự do suy diễn. Nhóm tập trung hiện thực hóa và kiểm chứng giả thuyết quan trọng nhất:  
  > **Ranh giới an toàn của AI doanh nghiệp phải được thiết lập bằng tầng kiểm soát phân quyền tất định từ bên ngoài LLM.**  
  > Trước khi câu hỏi được gửi tới AI, hệ thống đã lọc sạch tài liệu theo quyền đọc, đối tượng áp dụng và phiên bản hiệu lực. Tài liệu ngoài quyền sẽ bị chặn 100%, không bao giờ được lọt vào ngữ cảnh của LLM."

---

## PHẦN 3: DEMO CHÍNH (1:05 → 2:30) — 85 giây
* **Môi trường:** Chuyển sang màn hình Live Web Application (Next.js 14 tại `localhost:3000`).

### 🎬 Case 1: Cùng câu hỏi — Hai người khác công ty nhận kết quả và nguồn khác nhau
1. **Thao tác 1:** Tại thanh chọn nhân sự, chọn **Alice (AlphaPay - Engineering)**.
   * Gõ câu hỏi: *"Tôi có bao nhiêu ngày nghỉ phép?"*
   * **Kết quả:** Trạng thái `ANSWER` (Huy hiệu xanh). Trả lời: **15 ngày phép**. Trích dẫn nguyên văn: `AlphaPay Annual Leave Policy` (Điều 4).
2. **Thao tác 2:** Chuyển sang **Carol (NovaGame - Engineering)**.
   * Giữ nguyên câu hỏi: *"Tôi có bao nhiêu ngày nghỉ phép?"*
   * **Kết quả:** Trạng thái `ANSWER`. Trả lời: **12 ngày phép**. Trích dẫn nguyên văn: `NovaGame Annual Leave Policy`.
* **Lời thoại:**
  > "Như anh/chị thấy trên màn hình: Cùng một câu hỏi, cùng vị trí kỹ sư, nhưng Alice nhận 15 ngày từ chính sách AlphaPay, còn Carol nhận 12 ngày từ chính sách NovaGame. Hệ thống đạt độ cô lập dữ liệu tuyệt đối: Zero Cross-Company Leakage."

### 🎬 Case 2: Kiểm soát dữ liệu mật — Chặn truy cập ngoài thẩm quyền
* **Thao tác:** Quay lại **Alice (Nhân viên thông thường)**.
  * Gõ câu hỏi: *"Chính sách lương của tôi là gì?"* (hoặc hỏi về bảng lương HR).
  * **Kết quả:** Trạng thái `ABSTAIN` (Huy hiệu xám: *Chưa đủ thông tin*). Không có bất kỳ trích dẫn nào.
* **Lời thoại:**
  > "Khi Alice hỏi về lương, tài liệu mật của phòng HR đã bị bộ lọc quyền chặn ngay từ tầng lưu trữ. LLM hoàn toàn không nhìn thấy tài liệu này trong context, và hệ thống lịch sự từ chối trả lời. Tuyệt đối không có nguy cơ lộ lọt thông tin mật."

---

## PHẦN 4: TÌNH HUỐNG KHÓ (2:30 → 3:30) — 60 giây

### 🎬 Case 3: Xử lý mâu thuẫn chính sách ngang quyền (Policy Conflict)
* **Thao tác:** Chọn **Carol (NovaGame)**.
  * Gõ câu hỏi: *"Tôi được làm việc tại nhà mấy ngày?"*
  * **Kết quả:** Trạng thái `CONFLICT` (Huy hiệu vàng: *Thông tin chưa thống nhất*).
  * Giao diện: Hiển thị thông báo văn bản mâu thuẫn và trích dẫn **cả 2 văn bản ngang hàng**: Policy A (2 ngày) và Policy B (3 ngày).
* **Lời thoại:**
  > "Đây là một tình huống rất khó trong thực tế: NovaGame có 2 văn bản chính sách cùng cấp hiệu lực nhưng quy định số ngày WFH khác nhau. AI thông thường sẽ đoán mò hoặc chọn ngẫu nhiên một con số. Nhưng tại đây, bộ Authority Resolver nhận diện xung đột và gắn cờ CONFLICT, trích dẫn cả 2 nguồn để người dùng đối soát thay vì bịa đặt."

### 🎬 Case 4: Nhận biết ranh giới dữ liệu — Thiếu căn cứ thì không suy đoán
* **Thao tác:** Chọn **Alice (AlphaPay)**.
  * Gõ câu hỏi: *"Tôi có được làm việc tại nhà thứ Sáu không?"*
  * **Kết quả:** Trạng thái `ABSTAIN`.
* **Lời thoại:**
  > "Văn bản AlphaPay cho phép WFH 2 ngày/tuần nhưng không nói rõ thứ Sáu được hay không. Hệ thống kiên quyết từ chối thay vì suy đoán 'chắc là được'. Nguyên tắc ở đây là: **Biết thì trích dẫn nguyên văn, không đủ căn cứ thì dứt khoát từ chối.**"

---

## PHẦN 5: HẠN CHẾ SẢN PHẨM & FAIL CASE THỰC TẾ (3:30 → 4:20) — 50 giây
* **Màn hình:** Live Demo câu hỏi ghép trên Web hoặc Slide phân tích Fail Case `TC-M2-07`.

### 🎬 Case 5 (Fail Case): Truy vấn ghép đa chủ đề liên tài liệu (TC-M2-07)
* **Thao tác:** Chọn **Alice (AlphaPay)**.
  * Gõ câu hỏi ghép: *"Nếu tôi muốn nghỉ phép kết hợp làm việc tại nhà trong cùng một tuần thì quy trình quản lý phê duyệt như thế nào?"*
  * **Kết quả thực tế:** Hệ thống trả về `ANSWER` nhưng **chỉ nói về 15 ngày phép và trích dẫn duy nhất `ALPHA-LEAVE`**. Toàn bộ quy định WFH và thủ tục Quản lý phê duyệt bị bỏ sót.
* **Lời thoại thẳng thắn chỉ ra hạn chế:**
  > "Một hệ thống tốt là hệ thống biết rõ mình đang chưa tốt ở đâu. Đây là một ca kiểm thử thất bại thực tế của MVP (Mã TC-M2-07).  
  > **Nguyên nhân:** Để đảm bảo an toàn tối đa cho MVP, kiến trúc hiện tại là Pipeline tuần tự đơn chủ đề. Khi gặp câu hỏi ghép gồm 3 khía cạnh (Nghỉ phép + WFH + Phê duyệt), hệ thống chỉ bắt được intent đầu tiên và lọc tài liệu theo chủ đề đó, dẫn đến việc bỏ sót 2 văn bản còn lại.  
  > **Hướng khắc phục:** Trong Mission 3, hệ thống sẽ được nâng cấp thêm tầng **Query Decomposition** để tự động phân rã câu hỏi phức thành các truy vấn đơn trước khi tổng hợp câu trả lời."

---

## PHẦN 6: KẾT LUẬN & THÔNG ĐIỆP (4:20 → 4:45) — 25 giây
* **Màn hình:** Slide Key Takeaways & Liên kết tài liệu nghiệm thu.
* **Lời thoại:**
  > "Tóm lại, giá trị lớn nhất mà MVP Mission 2 chứng minh không phải là AI nói hay đến đâu, mà là **AI được kiểm soát chặt chẽ như thế nào**.  
  > Với cơ chế phân quyền tất định, kiểm tra phiên bản và kiểm định trích dẫn nguyên văn 100%, chúng tôi tin rằng đây là nền móng khả thi để đưa AI chính sách vào vận hành doanh nghiệp thực tế.  
  > Xin cảm ơn anh/chị đã lắng nghe!"

---

# 3. CHECKLIST TRƯỚC KHI BẤM QUAY VIDEO

- [ ] **Môi trường Backend:** Chạy lệnh `python -m uvicorn api.index:app --port 8000` (đảm bảo phản hồi nhanh < 300ms).
- [ ] **Môi trường Frontend:** Chạy `npm run dev` trong thư mục `web/` (`http://localhost:3000`). Trình duyệt để zoom 100% hoặc 110%, giao diện Dark Mode rõ nét.
- [ ] **Bộ câu hỏi mẫu copy sẵn vào Notepad** để paste nhanh, tránh gõ phím mất thời gian:
  1. `Tôi có bao nhiêu ngày nghỉ phép?`
  2. `Chính sách lương của tôi là gì?`
  3. `Tôi được làm việc tại nhà mấy ngày?`
  4. `Tôi có được làm việc tại nhà thứ Sáu không?`
  5. `Nếu tôi muốn nghỉ phép kết hợp làm việc tại nhà trong cùng một tuần thì quy trình quản lý phê duyệt như thế nào?`
- [ ] **Đồng hồ bấm giờ kế bên:** Đặt mốc chuông rung nhẹ ở phút **4:15** để chuẩn bị kết luận, tuyệt đối dừng lại trước **4:50**.
