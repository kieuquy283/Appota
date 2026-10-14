# Kế hoạch Video Trình bày Mission 2 — Appota Knowledge Guard

* **Thời lượng mục tiêu thực tế:** **4 phút 20 giây – 4 phút 30 giây** (tối đa 5 phút).
* **Môi trường ghi hình:** Giao diện Web Next.js 14 Enterprise Dark UI (`http://localhost:3000`), kết hợp slide tối giản.
* **Cấu trúc 5 phần:** `Bài toán ➔ Phần chọn để chứng minh ➔ Demo chính ➔ Tình huống khó ➔ Hạn chế`.

---

## 🎯 Thông điệp cốt lõi (Core Takeaway)

> **"FILTER FIRST — AI SECOND"**  
> *Cùng một câu hỏi, hệ thống phải chọn đúng thông tin theo đúng người dùng, đúng đơn vị, đúng quyền và đúng phiên bản tài liệu — trước khi đưa dữ liệu vào LLM.*

---

# 1. BẢNG PHÂN BỔ THỜI LƯỢNG TỔNG THỂ

| Thời lượng | Phân đoạn | Nội dung trọng tâm | Màn hình hiển thị |
|---|---|---|---|
| **0:00 – 0:30** (30s) | **1. Bài toán** | Cùng câu hỏi nhưng khác bối cảnh; rủi ro lộ tài liệu HR hoặc dùng nhầm chính sách công ty khác | Slide Problem |
| **0:30 – 0:55** (25s) | **2. Chọn chứng minh** | Lọc quyền tất định trước khi vào LLM: *Filter First, AI Second* | Slide Architecture |
| **0:55 – 2:15** (80s) | **3. Demo chính** | Cùng câu hỏi khác kết quả (Alice vs Carol) + Chặn tài liệu HR Confidential | Live Web Next.js |
| **2:15 – 3:15** (60s) | **4. Tình huống khó** | Mâu thuẫn văn bản ngang quyền (`CONFLICT`) + Thiếu chứng cứ (`ABSTAIN`) | Live Web Next.js |
| **3:15 – 4:00** (45s) | **5. Hạn chế (Fail Case)** | Câu hỏi ghép đa chủ đề: Single-intent pipeline chưa có Query Decomposition | Live Web Next.js |
| **4:00 – 4:25** (25s) | **6. Kết luận** | Tổng kết giá trị kiểm chứng: An toàn tri thức là nền tảng của Enterprise AI | Slide Key Takeaway |

---

# 2. KỊCH BẢN CHI TIẾT TỪNG PHÂN ĐOẠN

## PHẦN 1: BÀI TOÁN (0:00 → 0:30) — 30 giây
* **Màn hình:** Slide sơ đồ tổ chức tập đoàn `Appota Demo Group` gồm `AlphaPay` và `NovaGame`.
* **Thông điệp:** `Same Question ≠ Same Answer`.
* **Lời thoại đề xuất:**
  > "Chào anh/chị. Trong một tập đoàn đa đơn vị thành viên, cùng một câu hỏi chưa chắc có cùng một câu trả lời. Nhân viên tại AlphaPay và NovaGame có chính sách ngày nghỉ khác nhau. Đồng thời, tài liệu compensation chỉ dành riêng cho HR không được phép hiển thị cho nhân viên thông thường.  
  > Nếu đưa AI vào doanh nghiệp mà thiếu kiểm soát, rủi ro lớn nhất là mô hình có thể trích xuất nhầm tài liệu của đơn vị khác hoặc đưa thông tin nhạy cảm vào câu trả lời."

---

## PHẦN 2: PHẦN CHỌN ĐỂ CHỨNG MINH (0:30 → 0:55) — 25 giây
* **Màn hình:** Slide Kiến trúc Pipeline xác định:
  ```
  User Profile ➔ Pre-Retrieval Guard (RBAC/ABAC/Version) ➔ Retrieval ➔ Resolver ➔ LLM ➔ Citation Validation
  ```
* **Thông điệp:** `FILTER FIRST — AI SECOND`.
* **Lời thoại đề xuất:**
  > "Để xử lý rủi ro này, nhóm không xây dựng chatbot tự do mà tập trung chứng minh giả thuyết cốt lõi:  
  > **Ranh giới an toàn của AI doanh nghiệp phải được thiết lập bằng tầng kiểm soát phân quyền tất định trước khi tới LLM.**  
  > Trước khi truy xuất hay gọi AI, tầng Pre-Retrieval Guard đã lọc trước quyền đọc, đối tượng áp dụng và phiên bản hiệu lực. Tài liệu ngoài quyền sẽ bị loại bỏ ngay từ đầu, không đưa vào context của LLM."

---

## PHẦN 3: DEMO CHÍNH (0:55 → 2:15) — 80 giây
* **Môi trường:** Chuyển sang màn hình Live Web Application (Next.js 14 tại `localhost:3000`).

### 🎬 Case 1: Cùng câu hỏi — Hai người khác đơn vị nhận kết quả và nguồn khác nhau
1. **Thao tác 1:** Tại thanh chọn nhân sự, chọn **Alice (AlphaPay - Engineering)**.
   * Gõ: *"Tôi có bao nhiêu ngày nghỉ phép?"*
   * **Kết quả:** Trạng thái `ANSWER`. Trả lời: **15 ngày phép**. Trích dẫn: `AlphaPay Annual Leave Policy`.
2. **Thao tác 2:** Chuyển sang **Carol (NovaGame - Engineering)**.
   * Giữ nguyên câu hỏi: *"Tôi có bao nhiêu ngày nghỉ phép?"*
   * **Kết quả:** Trạng thái `ANSWER`. Trả lời: **12 ngày phép**. Trích dẫn: `NovaGame Annual Leave Policy`.
* **Lời thoại:**
  > "Cùng một câu hỏi về ngày phép, Alice nhận 15 ngày từ chính sách AlphaPay, còn Carol nhận 12 ngày từ chính sách NovaGame. Kết quả kiểm thử trong repo cho thấy hệ thống phân lập đúng nguồn theo bối cảnh, không ghi nhận trường hợp rò rỉ tài liệu giữa các công ty thành viên."

### 🎬 Case 2: Kiểm soát dữ liệu mật — Phân quyền trước retrieval
* **Thao tác:** Quay lại **Alice (Nhân viên thông thường)**.
  * Gõ: *"Chính sách lương của tôi là gì?"*
  * **Kết quả:** Trạng thái `ABSTAIN` (Huy hiệu xám: *Chưa đủ thông tin*). Không có trích dẫn nào.
* **Lời thoại:**
  > "Khi Alice hỏi về lương, tài liệu compensation chỉ dành cho HR đã bị Pre-Retrieval Guard loại bỏ trước retrieval và LLM. Do không có tài liệu hợp lệ trong context, hệ thống từ chối trả lời theo nguyên tắc an toàn."

---

## PHẦN 4: TÌNH HUỐNG KHÓ (2:15 → 3:15) — 60 giây

### 🎬 Case 3: Xử lý mâu thuẫn chính sách ngang quyền (Policy Conflict)
* **Thao tác:** Chọn **Carol (NovaGame)**.
  * Gõ: *"Tôi được làm việc tại nhà mấy ngày?"*
  * **Kết quả:** Trạng thái `CONFLICT` (Huy hiệu vàng: *Thông tin chưa thống nhất*).
  * Giao diện: Hiển thị cảnh báo văn bản mâu thuẫn và trích dẫn **cả 2 văn bản ngang hàng**: Policy A (2 ngày) và Policy B (3 ngày).
* **Lời thoại:**
  > "Trong dữ liệu có hai văn bản cùng cấp thẩm quyền quy định mức WFH khác nhau (2 ngày và 3 ngày). Nếu chỉ dựa vào vector similarity hoặc để LLM tự quyết định, mô hình rất dễ chọn ngẫu nhiên một con số. Tại đây, bộ Resolver nhận diện xung đột và chủ động trả trạng thái CONFLICT, hiển thị cả 2 nguồn để nhân sự tự đối soát."

### 🎬 Case 4: Nhận biết ranh giới dữ liệu — Thiếu căn cứ thì không suy diễn
* **Thao tác:** Chọn **Alice (AlphaPay)**.
  * Gõ: *"Tôi có được làm việc tại nhà thứ Sáu không?"*
  * **Kết quả:** Trạng thái `ABSTAIN`.
* **Lời thoại:**
  > "Chính sách chỉ quy định định mức 2 ngày/tuần nhưng không nêu cụ thể thứ Sáu. Thay vì để LLM tự suy đoán, hệ thống kích hoạt cơ chế Missing Evidence Guard và trả về ABSTAIN. Hệ thống chỉ trả lời khi có căn cứ rõ ràng."

---

## PHẦN 5: HẠN CHẾ SẢN PHẨM & FAIL CASE THỰC TẾ (3:15 → 4:00) — 45 giây
* **Màn hình:** Live Demo trên Web với câu hỏi ghép đa chủ đề.

### 🎬 Case 5: Fail case nhóm chủ động kiểm tra để tìm giới hạn thiết kế
* **Thao tác:** Chọn **Alice (AlphaPay)**.
  * Gõ: *"Nếu tôi muốn nghỉ phép kết hợp làm việc tại nhà trong cùng một tuần thì quy trình quản lý phê duyệt như thế nào?"*
  * **Kết quả thực tế:** Hệ thống trả lời vế 15 ngày phép từ `ALPHA-LEAVE`, nhưng bỏ sót nội dung WFH và thủ tục Quản lý phê duyệt.
* **Lời thoại thẳng thắn chỉ ra hạn chế:**
  > "Để hiểu rõ giới hạn của sản phẩm, nhóm chủ động kiểm tra một câu hỏi ghép phức hợp về nghỉ phép, WFH và phê duyệt quản lý. Kết quả là hệ thống chỉ trả lời được vế ngày phép.  
  > **Nguyên nhân:** Pipeline MVP hiện tại đi theo luồng single-intent để đảm bảo kiểm soát quyền chặt chẽ, nên chưa hỗ trợ phân rã câu hỏi đa chủ đề (Query Decomposition). Trong các iteration tiếp theo, nhóm sẽ nâng cấp thêm bộ định tuyến đa nhánh để xử lý trọn vẹn dạng câu hỏi này."

---

## PHẦN 6: KẾT LUẬN & THÔNG ĐIỆP (4:00 → 4:25) — 25 giây
* **Màn hình:** Slide Key Takeaways.
* **Lời thoại:**
  > "Tóm lại, MVP này chứng minh rằng: Trước khi AI sinh câu trả lời, nguồn tri thức hoàn toàn có thể được kiểm soát theo đúng bối cảnh, thẩm quyền và phiên bản. Kèm theo đó, cơ chế citation validation đối soát từng đoạn trích dẫn với văn bản gốc giúp câu trả lời luôn có căn cứ minh bạch.  
  > Cảm ơn anh/chị đã theo dõi."

---

# 3. CHECKLIST TRƯỚC KHI BẤM QUAY VIDEO

- [ ] **Môi trường Backend:** Chạy `python -m uvicorn api.index:app --port 8000`.
- [ ] **Môi trường Frontend:** Chạy `npm run dev` trong thư mục `web/` (`http://localhost:3000`). Trình duyệt để zoom 100% hoặc 110%, giao diện Enterprise Dark UI rõ nét.
- [ ] **Bộ 5 câu hỏi mẫu copy sẵn vào Notepad** để dán nhanh, tiết kiệm thời gian:
  1. `Tôi có bao nhiêu ngày nghỉ phép?`
  2. `Chính sách lương của tôi là gì?`
  3. `Tôi được làm việc tại nhà mấy ngày?`
  4. `Tôi có được làm việc tại nhà thứ Sáu không?`
  5. `Nếu tôi muốn nghỉ phép kết hợp làm việc tại nhà trong cùng một tuần thì quy trình quản lý phê duyệt như thế nào?`
- [ ] **Bấm giờ:** Đặt mốc chuông rung ở phút **4:00** để bước vào phần kết luận, kết thúc an toàn trong khoảng **4:20 – 4:30**.
