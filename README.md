# Appota Knowledge Guard — Enterprise Policy AI Assistant (Mission 2 MVP)

> **Hệ thống Trợ lý Tra cứu Chính sách Doanh nghiệp có Kiểm soát Quyền truy cập (RBAC/ABAC), Quản trị Phiên bản và Trích dẫn Bằng chứng Nguyên văn.**  
> *(Toàn bộ tên tổ chức, cá nhân, quy chế trong repository là dữ liệu giả lập phục vụ kiểm chứng kỹ thuật; không đại diện cho pháp nhân Appota ngoài đời thực).*

---

## TỔNG QUAN
Ứng dụng được xây dựng với mục đích kiểm thử và minh chứng phương pháp luận kỹ thuật: **Chọn đúng thứ cần làm ➔ Biến nó thành sản phẩm ➔ Kiểm thử nghiêm ngặt ➔ Biết rõ sản phẩm đang tốt và chưa tốt ở đâu.**

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

## CORE LOOP

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

### Tình huống bắt buộc: Cùng câu hỏi — Hai bối cảnh — Hai kết quả khác nhau
Cùng đặt câu hỏi: *"Tôi có bao nhiêu ngày nghỉ phép?"*:
* **Alice (`U01`)** — Kỹ sư tại **AlphaPay**: Hệ thống đối soát bối cảnh AlphaPay ➔ Cấp quyền đọc `ALPHA-LEAVE` ➔ Trả lời: **15 ngày nghỉ phép năm** (kèm trích dẫn chính sách hiện hành AlphaPay).
* **Carol (`U03`)** — Chuyên viên tại **NovaGame**: Hệ thống đối soát bối cảnh NovaGame ➔ Cấp quyền đọc `NOVA-LEAVE` ➔ Trả lời: **12 ngày nghỉ phép năm** (kèm trích dẫn chính sách NovaGame).
* 🛡️ **Kết quả**: **0% rò rỉ chéo dữ liệu (Zero Cross-Company Leakage)**. Tài liệu của AlphaPay không bao giờ lọt vào ngữ cảnh xử lý của nhân sự NovaGame và ngược lại.

### 6 Tiêu chuẩn MVP đã chứng minh:
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

## MÔ PHỎNG CƠ CẤU TỔ CHỨC VÀ NHÂN VIÊN

Để kiểm chứng tính cô lập dữ liệu và khả năng phân quyền đa cấp trong tập đoàn, hệ thống xây dựng mô hình dữ liệu giả lập chuẩn hóa (Synthetic Schema) tại [data/seed.json](data/seed.json):

### 1. Cây phân cấp tổ chức (Organizational Hierarchy)
Hệ thống mô phỏng cấu trúc tập đoàn 4 tầng (`GROUP ➔ COMPANY ➔ DEPARTMENT ➔ TEAM`):

```
Appota Demo Group (GROUP)
├── AlphaPay (ALPHA) — Công ty Fintech thành viên
│   ├── Engineering (ALPHA-ENG)
│   │   ├── Backend Team (ALPHA-BACKEND)
│   │   └── Platform Team (ALPHA-PLATFORM)
│   └── HR (ALPHA-HR)
│       └── HR Ops Team (ALPHA-HR-OPS)
└── NovaGame (NOVA) — Công ty Game & Publishing thành viên
    ├── Engineering (NOVA-ENG)
    │   └── Core Team (NOVA-CORE)
    └── Marketing (NOVA-MARKETING)
        └── Growth Team (NOVA-GROWTH)
```

### 2. Danh sách Nhân viên giả lập (Synthetic Personas)
Hệ thống định nghĩa 6 tài khoản mẫu mang đầy đủ tổ hợp thuộc tính thực tế (kết hợp RBAC + ABAC) để phục vụ kiểm thử phân quyền:

| Mã NV | Họ tên | Công ty | Phòng ban | Nhóm | Vai trò (Role) | Cấp bậc | Loại HĐ | Ý nghĩa kiểm thử trong hệ thống |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **U01** | Alice | AlphaPay | Engineering | Backend | `EMPLOYEE` | Level 3 | Full-time | Nhân viên AlphaPay tiêu chuẩn; kiểm chứng truy xuất chính sách AlphaPay, bị chặn hỏi lương HR. |
| **U02** | Bob | AlphaPay | Engineering | Backend | `PEOPLE_MANAGER` | Level 5 | Full-time | Quản lý trực tiếp; được quyền truy cập tài liệu quy trình phê duyệt nghỉ phép của Manager. |
| **U03** | Carol | NovaGame | Engineering | Core | `EMPLOYEE` | Level 3 | Full-time | Cùng cấp bậc & vai trò với Alice nhưng thuộc NovaGame; kiểm chứng cách ly dữ liệu giữa 2 công ty con. |
| **U04** | David | NovaGame | Marketing | Growth | `EMPLOYEE` | Level 2 | Full-time | Nhân viên Marketing cấp cơ sở tại NovaGame. |
| **U05** | Helen | AlphaPay | HR | HR Ops | `HR` | Level 4 | Full-time | Chuyên viên Nhân sự; người duy nhất được cấp quyền truy cập cẩm nang lương thưởng nhạy cảm. |
| **U06** | Frank | AlphaPay | Engineering | Platform | `EMPLOYEE` | Level 1 | Full-time | Nhân viên mới/Junior thuộc Platform Team AlphaPay. |

### 3. Nguyên tắc Áp dụng & Phân quyền (Access & Applicability Rules)
Mỗi tài liệu trong kho tri thức đều được gắn thẻ metadata chuẩn hóa:
- **Quyền đọc (`access`)**: Xác định đối tượng được phép đọc (ví dụ: `role: HR` mới đọc được tài liệu lương thưởng; nhân viên thông thường bị chặn ngay từ tầng truy xuất).
- **Phạm vi áp dụng (`applicability`)**: Quy định chính sách chỉ có hiệu lực cho đúng đơn vị (ví dụ: `company: AlphaPay` chỉ áp dụng cho nhân sự AlphaPay, không thể áp dụng cho NovaGame).
- **Phân cấp thẩm quyền (`authority`)**: `OFFICIAL_POLICY` (Chính sách chính thức) > `APPROVED_PROCEDURE` (Quy trình) > `GUIDELINE` (Hướng dẫn) > `FAQ` (Hỏi đáp).

---

## BỘ KIỂM THỬ MISSION 2

📄 *Chi tiết toàn văn 07 tình huống nghiệm thu xem tại: [docs/mission_2_test_evaluation.md](docs/mission_2_test_evaluation.md)*

---

## 3 CÂU HỎI BẮT BUỘC

📄 *Chi tiết toàn văn bản luận giải xem tại: [docs/mission_2_mandatory_questions.md](docs/mission_2_mandatory_questions.md)*

---

## KIẾN TRÚC & HƯỚNG DẪN KHỞI CHẠY

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