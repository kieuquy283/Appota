# Appota Knowledge Guard — Enterprise Policy AI Assistant (Mission 2 MVP)

> **Hệ thống Trợ lý Tra cứu Chính sách Doanh nghiệp có Kiểm soát Quyền truy cập (RBAC/ABAC), Quản trị Phiên bản và Trích dẫn Bằng chứng Nguyên văn.**  
> *(Toàn bộ tên tổ chức, cá nhân, quy chế trong repository là dữ liệu giả lập phục vụ kiểm chứng kỹ thuật; không đại diện cho pháp nhân Appota ngoài đời thực).*

---

## 🎯 CẦN CHỨNG MINH
Dự án được xây dựng nhằm chứng minh phương pháp luận kỹ thuật: **Chọn đúng thứ cần làm ➔ Biến nó thành sản phẩm ➔ Kiểm thử nghiêm ngặt ➔ Biết rõ sản phẩm đang tốt và chưa tốt ở đâu.**

```
[Chọn đúng thứ cần làm] ──► [Biến thành sản phẩm] ──► [Kiểm thử đa chiều] ──► [Nhận diện ranh giới]
• Không sa đà vào IAM        • Pipeline xác định        • 36 Unit Tests            • Làm tốt: Phân quyền,
• Không Agent tự do          • Next.js + FastAPI UI     • 8 Evaluation Cases         Bảo mật, Trích dẫn
• Tập trung Pre-retrieval    • Live trên Vercel         • 60 Synthetic Tests       • Chưa tốt: Đa chủ đề
  Authorization Guard                                   • 7 Test Scenarios           liên tài liệu
```

1. **Chọn đúng thứ cần làm**: Trong môi trường doanh nghiệp đa công ty thành viên, rủi ro lớn nhất của AI không phải là "văn phong chưa mượt", mà là **tiết lộ bí mật nội bộ** hoặc **áp dụng nhầm chính sách của công ty khác**. Do đó, MVP tập trung hiện thực hóa ranh giới cốt lõi: **Tầng phân quyền dữ liệu tất định (Deterministic Governance Filtering)** trước khi tri thức được đưa vào context của LLM.
2. **Biến nó thành sản phẩm**: Hệ thống không dừng lại ở script dòng lệnh mà đã được hoàn thiện thành ứng dụng Web hoàn chỉnh:
   - **Frontend**: Next.js 14 (App Router, TypeScript, Giao diện Doanh nghiệp cao cấp phong cách Bloomberg/Enterprise Dark UI).
   - **Backend API**: FastAPI (Python 3.10+), hỗ trợ phân quyền theo bối cảnh người dùng, xử lý mâu thuẫn thẩm quyền, bóc tách thực thể thời gian và trả về trích dẫn nguyên văn.
3. **Kiểm thử thực nghiệm**: Hệ thống vượt qua bộ kiểm thử tự động toàn diện:
   - `36/36` Unit Tests kiểm chứng bảo mật, cô lập người dùng, che giấu trace kỹ thuật.
   - `8/8` Ca đánh giá chất lượng phản hồi và hành vi RAG (`scripts.evaluate` đạt 100% PASS).
   - Bộ kiểm thử nghiệm thu 07 tình huống chi tiết theo chuẩn báo cáo.
4. **Biết sản phẩm đang tốt và chưa tốt ở đâu**:
   - **Làm rất tốt**: Kiểm soát quyền đa cấp, cô lập dữ liệu tuyệt đối giữa các công ty con, nhận diện từ đồng nghĩa, xử lý truy vấn mốc thời gian lịch sử, phát hiện mâu thuẫn văn bản ngang quyền và chặn 100% rò rỉ dữ liệu nhạy cảm.
   - **Chưa xử lý tốt**: Các câu hỏi phức hợp đa chủ đề liên tài liệu (do thiết kế MVP là pipeline tuần tự đơn chủ đề, chưa có Query Decomposition).

---

## 🔄 CORE LOOP MISSION 2

> **Câu hỏi + Bối cảnh người dùng ➔ Tìm đúng tri thức ➔ Sử dụng đúng phạm vi ➔ Trả lời có nguồn kiểm chứng.**

```
┌────────────────────────┐      ┌────────────────────────┐
│  Câu hỏi người dùng   │  +   │   Bối cảnh nhân sự     │ (Công ty, Phòng ban,
└───────────┬────────────┘      └───────────┬────────────┘  Vai trò, Cấp bậc...)
            │                               │
            └───────────────┬───────────────┘
                            ▼
          ┌───────────────────────────────────┐
          │  1. Pre-retrieval Governance Guard │
          │  • Can Read (RBAC/ABAC)           │
          │  • Applicability (Đối tượng áp dụng│
          │  • Version Temporal Filter (Ngày) │
          └─────────────────┬─────────────────┘
                            ▼
          ┌───────────────────────────────────┐
          │  2. Semantic & Lexical Retrieval  │ (Chỉ chạy trên tập văn bản
          └─────────────────┬─────────────────┘  đã được cấp phép)
                            ▼
          ┌───────────────────────────────────┐
          │  3. Authority & Conflict Resolver │ (Policy > Procedure > FAQ;
          └─────────────────┬─────────────────┘  Bắt mâu thuẫn ngang hàng)
                            ▼
          ┌───────────────────────────────────┐
          │  4. Generation & Citation Guard   │ (Kiểm định đối soát 100%
          │  • Trả lời trung thực             │  trích đoạn nguyên văn)
          │  • Từ chối an toàn khi thiếu căn cứ│
          └─────────────────┬─────────────────┘
                            ▼
                 [ Kết quả minh bạch ]
```

### 👥 Tình huống bắt buộc: Cùng câu hỏi — Hai bối cảnh — Hai kết quả khác nhau
Cùng đặt câu hỏi: *"Tôi có bao nhiêu ngày nghỉ phép?"*:
* **Alice (`U01`)** — Kỹ sư tại **AlphaPay**: Hệ thống đối soát bối cảnh AlphaPay ➔ Cấp quyền đọc `ALPHA-LEAVE` ➔ Trả lời: **15 ngày nghỉ phép năm** (kèm trích dẫn chính sách hiện hành AlphaPay).
* **Carol (`U03`)** — Chuyên viên tại **NovaGame**: Hệ thống đối soát bối cảnh NovaGame ➔ Cấp quyền đọc `NOVA-LEAVE` ➔ Trả lời: **12 ngày nghỉ phép năm** (kèm trích dẫn chính sách NovaGame).
* 🛡️ **Kết quả**: **0% rò rỉ chéo dữ liệu (Zero Cross-Company Leakage)**. Tài liệu của AlphaPay không bao giờ lọt vào ngữ cảnh xử lý của nhân sự NovaGame và ngược lại.

### 📋 6 Tiêu chuẩn MVP đã chứng minh:
1. **Dữ liệu giả lập ở nhiều cấp tổ chức**: Phân cấp từ Tập đoàn (`GROUP`) ➔ Công ty thành viên (`ALPHA`, `NOVA`) ➔ Phòng ban (`ENG`, `HR`, `MARKETING`) ➔ Nhóm (`BACKEND`, `PLATFORM`, `CORE`, `GROWTH`).
2. **Hiểu được bối cảnh người hỏi**: Tự động giải quyết quyền lợi dựa trên hồ sơ: `company`, `department`, `role`, `level`, `employment_type`.
3. **Không sử dụng / làm lộ thông tin ngoài quyền**: Khi nhân viên thông thường hỏi bảng lương (`ALPHA-HR-COMPENSATION`), tài liệu bị loại bỏ ngay từ tầng lưu trữ (`unauthorized_context_rate = 0%`).
4. **Câu trả lời có nguồn / căn cứ**: Mọi câu trả lời `ANSWER` đều kèm thẻ trích dẫn chứa tên văn bản, điều khoản và trích đoạn nguyên văn 100% khớp văn bản nguồn.
5. **Biết từ chối khi thiếu dữ liệu**: Khi người dùng hỏi nội dung văn bản không quy định (ví dụ: *"Được WFH vào thứ Sáu không?"*), hệ thống trả về `ABSTAIN` thay vì để LLM suy diễn.
6. **Xử lý phiên bản và thông tin mâu thuẫn**:
   - Tự động bỏ qua bản nháp (`DRAFT`).
   - Xử lý truy vấn thời gian lịch sử: Tự động trích xuất năm (ví dụ: năm 2025) để tra cứu đúng phiên bản lịch sử `v2` (13 ngày) thay vì bản hiện tại `v3` (15 ngày).
   - Khi có 2 văn bản cùng cấp thẩm quyền quy định khác nhau, hệ thống phát hiện và gắn cờ `CONFLICT`.

---

## 🧪 BỘ KIỂM THỬ MISSION 2

📄 *Chi tiết toàn văn 07 tình huống nghiệm thu xem tại: [docs/mission_2_test_evaluation.md](docs/mission_2_test_evaluation.md)*

Bộ kiểm thử được xây dựng theo chuẩn quy cách: `Kỳ vọng ➔ Kết quả thực tế ➔ Đạt/Chưa đạt ➔ Điều học được`.

| Mã Test | Phân loại | Tình huống kiểm thử | Kỳ vọng | Kết quả thực tế | Đánh giá | Điều học được |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **TC-M2-01** | Làm tốt | `U01` (AlphaPay) hỏi số ngày nghỉ phép | `ANSWER` (15 ngày) | `ANSWER` (15 ngày) | **Đạt** | RBAC/ABAC phân quyền đúng tài liệu của AlphaPay. |
| **TC-M2-02** | Làm tốt | `U03` (NovaGame) hỏi cùng câu hỏi nghỉ phép | `ANSWER` (12 ngày) | `ANSWER` (12 ngày) | **Đạt** | Cô lập dữ liệu giữa các công ty; ra đúng nguồn NovaGame. |
| **TC-M2-03** | Khó / Quyền hạn | `U01` hỏi khung lương HR Confidential | `ABSTAIN` (Từ chối) | `ABSTAIN` (Từ chối) | **Đạt** | Chặn nguồn nhạy cảm trước khi vào prompt LLM. |
| **TC-M2-04** | Khó / Mâu thuẫn | `U03` hỏi số ngày WFH (Chính sách A vs B) | `CONFLICT` (2 nguồn) | `CONFLICT` (2 nguồn) | **Đạt** | Phát hiện mâu thuẫn chính sách ngang quyền, hiển thị cả 2 nguồn. |
| **TC-M2-05** | Dữ liệu không rõ | `U01` hỏi WFH vào ngày thứ Sáu | `ABSTAIN` (Từ chối) | `ABSTAIN` (Từ chối) | **Đạt** | Từ chối trả lời khi văn bản không nêu ngày cụ thể. |
| **TC-M2-06** | Làm tốt (Paraphrase) | `U01` hỏi *"Số ngày nghỉ hằng năm"* | `ANSWER` (15 ngày) | `ANSWER` (15 ngày) | **Đạt** | Mở rộng intent nhận diện từ đồng nghĩa tự nhiên (`T08` PASS). |
| **TC-M2-07** | Giới hạn thiết kế | `U01` hỏi nghỉ phép + WFH + Quản lý duyệt | Tổng hợp 3 nguồn | Chỉ ra 1 nguồn phép | **Chưa đạt** | Pipeline MVP đơn luồng, chưa có Query Decomposition & Multi-Topic Routing. |

* **Tổng số ca kiểm thử**: 07 tình huống (6 Đạt, 1 Chưa đạt).
* **Tỷ lệ Đạt**: **85.7%**.
* **Tỷ lệ rò rỉ dữ liệu ngoài quyền**: **0.0%**.

---

## ❓ 3 CÂU HỎI BẮT BUỘC

📄 *Chi tiết toàn văn bản luận giải xem tại: [docs/mission_2_mandatory_questions.md](docs/mission_2_mandatory_questions.md)*

### Câu hỏi 1: Phần quan trọng nhất bạn chọn để hiện thực hóa trong MVP là gì? Vì sao nếu phần này hoạt động, bạn tin rằng hướng giải quyết của mình là khả thi?
* **Phần cốt lõi**: **Tầng lọc quyền truy cập và tính áp dụng tiền truy xuất (Pre-Retrieval Authorization Guard)** kết hợp với **Kiểm định trích dẫn nguyên văn (Strict Verbatim Citation Guard)**.
* **Cơ sở tính khả thi**: Trong bài toán Enterprise AI, LLM "nói dối trôi chảy" hoặc tiết lộ thông tin ngoài thẩm quyền là rủi ro chí mạng. Bằng việc chứng minh: Alice và Carol nhận hai nguồn tri thức độc lập, Alice bị chặn truy cập bảng lương ngay từ tầng lưu trữ (`unauthorized_context_rate = 0%`), ta khẳng định được nguyên lý: *Ranh giới an toàn của AI doanh nghiệp phải được thiết lập bằng kiến trúc phân quyền tất định từ bên ngoài LLM, chứ không trông chờ vào System Prompt.* Khi ranh giới này vững chắc, việc mở rộng quy mô dữ liệu hay tích hợp thêm phòng ban chỉ là bài toán mở rộng kỹ thuật thuần túy.

### Câu hỏi 2: So với kế hoạch ở Mission 1, bạn đã thay đổi quyết định hoặc thiết kế nào? Điều gì trong quá trình làm khiến bạn thay đổi?
* **Thay đổi 1: Bỏ Autonomous ReAct Agent ➔ Chuyển sang Fixed Deterministic Pipeline**: Agent tự do lập kế hoạch thường bị lạc hướng, suy diễn lung tung hoặc cố tình đọc chéo tài liệu. Với chính sách nhân sự và tuân thủ pháp lý, tính nhất quán (Consistency) và khả năng kiểm toán (Auditability) của Pipeline xác định quan trọng hơn tính linh hoạt khó đoán.
* **Thay đổi 2: Tách biệt kiến trúc Frontend Next.js + Backend API FastAPI**: Thay vì dùng giao diện Streamlit nguyên khối, MVP đã tách biệt hoàn toàn Frontend (Next.js 14 App Router) và Backend API bảo mật qua Server-to-Server secret key, sẵn sàng triển khai Serverless trên Vercel.
* **Thay đổi 3: Thay thế SSO thật bằng Synthetic Persona Selector**: Để tập trung tối đa nguồn lực chứng minh giả thuyết cốt lõi về phân quyền tri thức thay vì sa đà vào dựng hạ tầng IAM/AD phức tạp.

### Câu hỏi 3: Trường hợp nào hiện khiến hệ thống dễ trả lời sai hoặc sử dụng sai tri thức nhất? Bạn phát hiện và kiểm soát rủi ro đó như thế nào?
* **Trường hợp dễ sai lệch nhất**: **Truy vấn phức hợp đa chủ đề liên tài liệu (Composite Multi-Topic Query — Case TC-M2-07)**. Khi người dùng hỏi câu hỏi ghép (ví dụ vừa hỏi số ngày phép, vừa hỏi định mức WFH, vừa hỏi quy trình phê duyệt), pipeline đơn luồng gán nhãn câu hỏi vào một topic duy nhất (`leave_days`) và lọc bỏ các tài liệu còn lại, dẫn đến câu trả lời bị phiến diện.
* **Cách phát hiện**: Sử dụng bộ kiểm thử đối kháng (Adversarial Test Suite) với các câu hỏi phức hợp đa chủ đề và đối soát ma trận tài liệu được cấp vào context.
* **Kiểm soát rủi ro**: Áp dụng nguyên tắc *"Thà từ chối trung thực (ABSTAIN) còn hơn trả lời sai"*, ghi nhận audit trace đầy đủ và đặt ra lộ trình nâng cấp với **Query Decomposition Planner** trong Mission 3.

---

## 💻 KIẾN TRÚC & HƯỚNG DẪN KHỞI CHẠY

### 1. Cấu trúc dự án
```
Appota/
├── api/
│   └── index.py            # FastAPI Backend API (deployable on Vercel)
├── web/                    # Next.js 14 Frontend (App Router, TypeScript)
│   ├── app/                # Layout, Pages, Route Handlers
│   └── components/         # UserSelector, ChatConversation, AnswerCard, CitationCard
├── src/
│   ├── governance.py       # Bộ lọc phân quyền (RBAC/ABAC) & Quản trị phiên bản
│   ├── retrieval.py        # Semantic & Lexical Search, Intent Classifier
│   ├── resolver.py         # Bộ giải quyết mâu thuẫn thẩm quyền văn bản
│   ├── service.py          # Orchestration pipeline chính & Temporal Entity Parser
│   └── llm.py              # LLM Generation & Trích xuất bằng chứng
├── data/
│   └── seed.json           # Dữ liệu tổ chức & tài liệu chính sách giả lập
├── docs/
│   ├── mission_2_test_evaluation.md     # Báo cáo bộ kiểm thử 07 tình huống
│   └── mission_2_mandatory_questions.md   # Báo cáo 3 câu hỏi bắt buộc
└── tests/                  # Bộ kiểm thử tự động (36 unit tests)
```

### 2. Chạy kiểm thử tự động
Yêu cầu Python 3.10+.
```powershell
# Chạy toàn bộ 36 unit tests
python -m unittest discover tests -v

# Chạy kịch bản đánh giá 8 ca thực nghiệm RAG (100% PASS)
python -m scripts.evaluate

# Thử nghiệm CLI nhanh theo từng bối cảnh người dùng
python -m scripts.demo U01 "Tôi có bao nhiêu ngày nghỉ phép?"
python -m scripts.demo U03 "Tôi có bao nhiêu ngày nghỉ phép?"
python -m scripts.demo U01 "Năm 2025 chính sách nghỉ phép của AlphaPay quy định bao nhiêu ngày?"
```

### 3. Chạy giao diện Web (Next.js + FastAPI)
```powershell
# 1. Khởi động Backend API (Terminal 1)
python -m uvicorn api.index:app --host 127.0.0.1 --port 8000 --reload

# 2. Khởi động Frontend Next.js (Terminal 2)
cd web
npm install
npm run dev
# Truy cập giao diện tại: http://localhost:3000
```

*(Hoặc chạy giao diện Streamlit cổ điển: `streamlit run streamlit_app.py`)*

---

## 🔒 AN TOÀN & BẢO MẬT DỮ LIỆU
* **Zero Client-Side Leakage**: Giao diện người dùng tuyệt đối không hiển thị document ID nội bộ, mã phiên bản thô (`v1`, `v2`), trace debug hay thông báo lỗi hệ thống.
* **Strict Source Alignment**: Mọi trích đoạn chính sách hiển thị trên UI bắt buộc phải khớp nguyên văn từng ký tự với tài liệu đã được cấp phép.
* **Tamper-Proof Authorization**: Phân quyền được thực thi ở tầng dịch vụ backend bằng quy tắc tất định, ngăn chặn hoàn toàn các nỗ lực Prompt Injection hoặc vượt quyền qua giao diện.
