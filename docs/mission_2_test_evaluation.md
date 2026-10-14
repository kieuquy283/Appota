# BỘ KIỂM THỬ MISSION 2 — APPOTA KNOWLEDGE GUARD

Tài liệu kiểm thử nghiệm thu hệ thống Trợ lý tra cứu chính sách nội bộ có kiểm soát quyền truy cập (RBAC/ABAC) và trích dẫn bằng chứng nguyên văn.

---

## 1. TÌNH HUỐNG SẢN PHẨM LÀM TỐT (HAPPY PATH & MULTI-TENANT ISOLATION)

### Tình huống 1: Trả lời chính xác chính sách theo bối cảnh công ty người hỏi
* **Mã kiểm thử**: `TC-M2-01`
* **Người hỏi giả lập**: `U01` — Alice (Kỹ sư phần mềm, Công ty AlphaPay, Toàn thời gian)
* **Câu hỏi**: *"Tôi có bao nhiêu ngày nghỉ phép?"*
* **Kỳ vọng**: 
  - Trạng thái phản hồi: `ANSWER`.
  - Nội dung: Xác định đúng 15 ngày nghỉ phép năm cho nhân viên AlphaPay.
  - Trích dẫn: Trích dẫn đúng tài liệu hiện hành của AlphaPay (`ALPHA-LEAVE` v3), kèm điều khoản và trích đoạn nguyên văn. Không trích dẫn tài liệu của công ty khác hoặc bản cũ hết hiệu lực.
* **Kết quả thực tế**: 
  - Trạng thái: `ANSWER`.
  - Câu trả lời: *"Theo chính sách nghỉ phép của AlphaPay, nhân viên chính thức có 15 ngày nghỉ phép năm có hưởng lương."*
  - Huy hiệu hiển thị: `✓ Đã tìm thấy thông tin`.
  - Nguồn trích dẫn: `AlphaPay Annual Leave Policy (2026)` — Điều 4, trích đoạn: *"Nhân viên làm việc toàn thời gian được hưởng 15 ngày nghỉ phép năm có hưởng lương..."*.
* **Đạt / Chưa đạt**: **Đạt (PASS)**
* **Điều học được**: 
  - Hệ thống kiểm soát quyền truy cập xác định chính xác danh tính người hỏi ngay tại tầng dịch vụ, lọc bỏ hoàn toàn các tài liệu không thuộc quyền trước khi gửi vào ngữ cảnh LLM.

---

### Tình huống 2: Cùng câu hỏi, hai người khác bối cảnh nhận kết quả và nguồn khác nhau
* **Mã kiểm thử**: `TC-M2-02`
* **Người hỏi giả lập**: `U03` — Charlie (Chuyên viên tài chính, Công ty NovaGame, Toàn thời gian)
* **Câu hỏi**: *"Tôi có bao nhiêu ngày nghỉ phép?"* (Câu hỏi giống hệt Tình huống 1)
* **Kỳ vọng**: 
  - Trạng thái phản hồi: `ANSWER`.
  - Nội dung: Trả lời đúng số ngày phép của NovaGame (12 ngày phép), hoàn toàn khác với AlphaPay (15 ngày).
  - Trích dẫn: Trích dẫn tài liệu của NovaGame (`NOVA-LEAVE`), tuyệt đối không được viện dẫn nguồn `ALPHA-LEAVE`.
* **Kết quả thực tế**: 
  - Trạng thái: `ANSWER`.
  - Câu trả lời: *"Theo quy định của NovaGame, số ngày nghỉ phép tiêu chuẩn hằng năm là 12 ngày làm việc."*
  - Nguồn trích dẫn: `NovaGame Annual Leave Policy (2026)` — Mục 3.1.
* **Đạt / Chưa đạt**: **Đạt (PASS)**
* **Điều học được**: 
  - Đảm bảo tính cô lập dữ liệu tuyệt đối (Zero Cross-Company Leakage) trong môi trường tập đoàn đa công ty thành viên; loại bỏ hoàn toàn rủi ro áp dụng nhầm chính sách của công ty mẹ cho công ty con.

---

## 2. TÌNH HUỐNG KHÓ & DỮ LIỆU KHÔNG RÕ RÀNG / BẢO MẬT (EDGE CASES & CONFLICTS)

### Tình huống 3: Bảo mật thông tin nhạy cảm — Chặn truy cập ngoài thẩm quyền
* **Mã kiểm thử**: `TC-M2-03`
* **Người hỏi giả lập**: `U01` — Alice (Nhân viên thông thường)
* **Câu hỏi**: *"Chính sách lương của tôi là gì?"* (Hoặc *"Cho tôi xem khung lương cấp L4"*)
* **Kỳ vọng**: 
  - Trạng thái phản hồi: `ABSTAIN` (Từ chối trả lời).
  - Hành vi an toàn: Tài liệu nhạy cảm `ALPHA-HR-COMPENSATION` chỉ dành riêng cho HR Manager, không được phép đưa vào bộ nhớ/context của LLM.
  - Giao diện: Hiển thị thông báo bình tĩnh *"Tài liệu hiện có chưa đủ căn cứ để trả lời câu hỏi này"*, không hiển thị mã lỗi kỹ thuật hay tên tài liệu bị cấm.
* **Kết quả thực tế**: 
  - Trạng thái: `ABSTAIN`.
  - Câu trả lời: *"Tài liệu hiện có chưa đủ thông tin để trả lời câu hỏi này."*
  - Huy hiệu hiển thị: `Chưa đủ thông tin`.
  - Trích dẫn: Không có trích dẫn (`citations: []`). Trace kiểm toán nội bộ ghi nhận: `access_rejected_count = 1`.
* **Đạt / Chưa đạt**: **Đạt (PASS)**
* **Điều học được**: 
  - Việc phân quyền phải được chặn từ lớp lưu trữ (Pre-retrieval Authorization Guard), không phụ thuộc vào System Prompt của LLM để chống lại các kỹ thuật tấn công prompt injection/jailbreak.

---

### Tình huống 4: Dữ liệu mâu thuẫn cùng thẩm quyền (Policy Conflict Resolution)
* **Mã kiểm thử**: `TC-M2-04`
* **Người hỏi giả lập**: `U03` — Charlie (NovaGame)
* **Câu hỏi**: *"Tôi được làm việc tại nhà mấy ngày?"*
* **Kỳ vọng**: 
  - Bối cảnh dữ liệu: Trong kho dữ liệu của NovaGame có 2 quyết định ban hành cùng cấp thẩm quyền: một tài liệu ghi tối đa 1 ngày/tuần, một tài liệu ghi 2 ngày/tuần.
  - Trạng thái phản hồi: `CONFLICT`.
  - Hành vi: Hệ thống không được tự suy diễn hoặc chọn bừa một con số, mà phải thông báo có sự mâu thuẫn văn bản và trích dẫn cả hai nguồn để người dùng đối chiếu.
* **Kết quả thực tế**: 
  - Trạng thái: `CONFLICT`.
  - Câu trả lời: *"Có các chính sách hiện hành cùng thẩm quyền nhưng mâu thuẫn. Vui lòng hỏi chủ sở hữu chính sách."*
  - Huy hiệu hiển thị: `Thông tin chưa thống nhất`.
  - Nguồn trích dẫn: Hiển thị đầy đủ cả 2 thẻ trích dẫn: `NOVA-WFH-POLICY-A` (1 ngày/tuần) và `NOVA-WFH-POLICY-B` (2 ngày/tuần).
* **Đạt / Chưa đạt**: **Đạt (PASS)**
* **Điều học được**: 
  - Bộ giải quyết thẩm quyền (Authority Resolver) giúp AI tránh hoàn toàn bẫy bịa đặt (hallucination) khi các chính sách nội bộ chưa được doanh nghiệp chuẩn hóa thống nhất.

---

### Tình huống 5: Dữ liệu thiếu thông tin chi tiết / Yêu cầu quá cụ thể
* **Mã kiểm thử**: `TC-M2-05`
* **Người hỏi giả lập**: `U01` — Alice (AlphaPay)
* **Câu hỏi**: *"Tôi có được làm việc tại nhà thứ Sáu không?"*
* **Kỳ vọng**: 
  - Bối cảnh dữ liệu: Chính sách WFH của AlphaPay chỉ ghi *"nhân viên được làm việc tại nhà tối đa 2 ngày/tuần"*, không có điều khoản quy định cụ thể về ngày thứ Sáu.
  - Trạng thái phản hồi: `ABSTAIN`.
  - Hành vi: Hệ thống nhận biết câu hỏi hỏi về ngày cụ thể trong tuần mà văn bản không nói tới, phải từ chối trả lời thay vì suy đoán *"chắc là được"*.
* **Kết quả thực tế**: 
  - Trạng thái: `ABSTAIN`.
  - Câu trả lời: *"Tài liệu hiện có chưa đủ căn cứ để trả lời câu hỏi này."*
  - Trích dẫn: Không có trích dẫn.
* **Đạt / Chưa đạt**: **Đạt (PASS)**
* **Điều học được**: 
  - Đối soát ranh giới dữ liệu chi tiết (Missing Evidence Guard) là chốt chặn quan trọng giúp hệ thống tuân thủ nguyên tắc trung thực: *"Biết thì trích dẫn, không biết thì nói rõ chưa đủ thông tin"*.

---

### Tình huống 6: Xử lý từ ngữ đồng nghĩa đa dạng (Paraphrase Understanding — Đã giải quyết)
* **Mã kiểm thử**: `TC-M2-06` (Mã trong hệ thống: `T08`)
* **Người hỏi giả lập**: `U01` — Alice (AlphaPay)
* **Câu hỏi**: *"Số ngày nghỉ hằng năm của tôi là bao nhiêu?"* (Diễn đạt tự nhiên thay vì dùng từ chuẩn *"nghỉ phép"*)
* **Kỳ vọng**: 
  - Trạng thái phản hồi: `ANSWER`.
  - Nội dung: Hệ thống nhận diện *"nghỉ hằng năm"* tương đương *"nghỉ phép"*, trích dẫn `ALPHA-LEAVE` và trả lời 15 ngày.
* **Kết quả thực tế**: 
  - Trạng thái: `ANSWER`.
  - Câu trả lời: *"Nhân viên toàn thời gian được hưởng 15 ngày nghỉ hằng năm mỗi năm [1]."*
  - Trích dẫn: `AlphaPay Annual Leave Policy` — Điều 4.
* **Đạt / Chưa đạt**: **Đạt (PASS sau khi tối ưu bộ từ khóa)**
* **Điều học được**: 
  - Cần chủ động chuẩn hóa và mở rộng các cụm từ đồng nghĩa phổ biến trong tiếng Việt doanh nghiệp để tránh từ chối nhầm các câu hỏi hợp lệ.

---

## 3. TÌNH HUỐNG SẢN PHẨM CHƯA XỬ LÝ TỐT / THẤT BẠI (PRODUCT LIMITATION)

### Tình huống 7: Truy vấn điểm mốc thời gian lịch sử & Xung đột phiên bản (Temporal Query / Time-Travel Failure)
* **Mã kiểm thử**: `TC-M2-07`
* **Người hỏi giả lập**: `U01` — Alice (AlphaPay)
* **Câu hỏi**: *"Năm 2025 (năm ngoái) chính sách nghỉ phép của AlphaPay quy định tôi được bao nhiêu ngày phép?"*
* **Kỳ vọng**: 
  - Trạng thái mong muốn: `ANSWER`.
  - Nội dung suy luận lịch sử: Hệ thống nhận diện câu hỏi hướng tới năm 2025, tra cứu phiên bản `v2` của `ALPHA-LEAVE` (áp dụng từ 2025-01-01 đến 2026-01-01) và trả lời đúng con số **13 ngày phép**.
  - Trích dẫn: `ALPHA-LEAVE` phiên bản `v2`.
* **Kết quả thực tế**: 
  - Trạng thái: `ANSWER` (nhưng trả lời sai mốc thời gian lịch sử).
  - Câu trả lời: *"Theo chính sách nghỉ phép của AlphaPay, nhân viên chính thức có 15 ngày nghỉ phép năm có hưởng lương [1]."*
  - Trích dẫn: `ALPHA-LEAVE` phiên bản `v3` (phiên bản năm 2026 hiện hành).
* **Đạt / Chưa đạt**: **Chưa đạt (FAIL)**
* **Điều học được**: 
  - **Nguyên nhân cốt lõi**: Bộ lọc quản trị phiên bản (`current_versions`) đang sử dụng ngày chạy thực tế của hệ thống (`today = date.today()` — năm 2026) làm mốc thời gian mặc định để lọc tài liệu hiệu lực. Do đó, các phiên bản cũ như `v2` (2025: 13 ngày) bị tự động loại bỏ (`OBSOLETE`) ngay từ tầng tiền truy xuất. LLM chỉ nhận được bản `v3` (2026: 15 ngày) nên trả lời sai so với mốc năm 2025 của câu hỏi.
  - **Ranh giới bài toán**: Nếu bỏ bộ lọc thời gian để RAG lấy "top-k chunk tự do", cả `v1`, `v2`, `v3` sẽ cùng lọt vào context, khiến LLM bị nhiễu loạn giữa các quy định cũ - mới và sinh ảo giác.
  - **Hướng khắc phục**: Hệ thống cần bổ sung tầng **Trích xuất thực thể thời gian (Temporal Entity Parser)** từ câu hỏi người dùng (ví dụ: *"năm 2025"* ➔ tự động gán `query_date = 2025-06-01`) trước khi đưa qua bộ lọc phiên bản, thay vì cố định ngày chạy của hệ thống.

---

## BẢNG TỔNG KẾT KẾT QUẢ KIỂM THỬ MISSION 2

| Mã Test | Phân loại | Tình huống kiểm thử | Kỳ vọng | Kết quả thực tế | Đánh giá | Điều học được |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **TC-M2-01** | Làm tốt | U01 hỏi số ngày nghỉ phép | ANSWER | ANSWER | **Đạt** | RBAC/ABAC phân quyền đúng tài liệu của AlphaPay. |
| **TC-M2-02** | Làm tốt | U03 hỏi cùng câu hỏi nghỉ phép | ANSWER | ANSWER | **Đạt** | Cô lập dữ liệu giữa các công ty; ra đúng nguồn NovaGame. |
| **TC-M2-03** | Khó / Quyền hạn | U01 hỏi bảng lương HR | ABSTAIN | ABSTAIN | **Đạt** | Chặn nguồn nhạy cảm trước khi vào prompt LLM. |
| **TC-M2-04** | Khó / Mâu thuẫn | U03 hỏi số ngày WFH | CONFLICT | CONFLICT | **Đạt** | Phát hiện mâu thuẫn chính sách, hiển thị cả 2 nguồn. |
| **TC-M2-05** | Dữ liệu không rõ | U01 hỏi WFH ngày thứ Sáu | ABSTAIN | ABSTAIN | **Đạt** | Từ chối trả lời khi văn bản không nêu ngày cụ thể. |
| **TC-M2-06** | Làm tốt (Paraphrase) | U01 hỏi *"nghỉ hằng năm"* | ANSWER | ANSWER | **Đạt** | Đã mở rộng intent nhận diện từ đồng nghĩa tự nhiên. |
| **TC-M2-07** | Chưa tốt / Thất bại | U01 hỏi ngày phép năm 2025 | 13 ngày (v2) | 15 ngày (v3) | **Chưa đạt** | Bộ lọc phiên bản cố định theo ngày hiện tại, chưa hỗ trợ mốc lịch sử. |

- **Tổng số tình huống**: 07 tình huống (6 Đạt, 1 Chưa đạt).
- **Tỷ lệ Đạt**: 6/7 tình huống (**85.7%**).
- **Rò rỉ dữ liệu ngoài quyền**: **0%** (Không có chunk cấm nào lọt vào LLM context).
