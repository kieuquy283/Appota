# BÁO CÁO TRẢ LỜI 3 CÂU HỎI BẮT BUỘC — MISSION 2
**Dự án: Appota Knowledge Guard (Trợ lý tra cứu chính sách doanh nghiệp có kiểm soát quyền truy cập)**

---

## CÂU HỎI 1:
### Phần quan trọng nhất bạn chọn để hiện thực hóa trong MVP là gì? Vì sao nếu phần này hoạt động, bạn tin rằng hướng giải quyết của mình là khả thi?

#### 1. Phần quan trọng nhất được chọn:
Phần cốt lõi nhất được hiện thực hóa trong MVP là **Tầng lọc quyền truy cập và tính áp dụng tiền truy xuất (Pre-Retrieval Authorization & Governance Filtering)** kết hợp với **Kiểm định trích dẫn nguyên văn (Strict Verbatim Citation Guard)**.

Cụ thể, trước khi câu hỏi được gửi tới mô hình tìm kiếm vector hay LLM, hệ thống kích hoạt chuỗi ranh giới xác định:
1. **Kiểm tra quyền đọc (Can Read)**: Dựa trên vai trò (`role`) và phòng ban (`department`) của người hỏi.
2. **Kiểm tra tính áp dụng (Applicability)**: Chính sách có áp dụng cho đơn vị thành viên (`company`), loại hợp đồng (`employment_type`) và cấp bậc (`level`) của người hỏi hay không.
3. **Lọc phiên bản hiệu lực (Version Temporal Filter)**: Chỉ các tài liệu có ngày hiệu lực phù hợp với ngày truy vấn và trạng thái `APPROVED` mới được lọt vào tập ứng viên (`eligible candidates`). Bản nháp (`DRAFT`) hoặc bản hết hạn (`OBSOLETE`) bị loại bỏ hoàn toàn.
4. **Giải quyết thẩm quyền & mâu thuẫn (Authority & Conflict Resolution)**: Văn bản quy định chính thức ưu tiên hơn tài liệu hỏi đáp (FAQ); nếu hai văn bản cùng cấp thẩm quyền mâu thuẫn, hệ thống gắn cờ `CONFLICT` và dừng sinh câu trả lời bừa bãi.
5. **Kiểm tra trích dẫn sau sinh (Post-Generation Verification)**: Mọi câu trả lời `ANSWER` bắt buộc phải kèm trích đoạn nguyên văn nằm chính xác trong các văn bản đã được cấp phép vào context.

#### 2. Vì sao nếu phần này hoạt động, hướng giải quyết là khả thi?
Trong bài toán AI doanh nghiệp (Enterprise AI), **rủi ro lớn nhất không phải là LLM viết văn không hay, mà là LLM "nói dối trôi chảy" hoặc sử dụng tri thức ngoài thẩm quyền (Grounded but Unauthorized / Outdated Knowledge)**.
- Một mô hình LLM dù tiên tiến đến đâu (GPT-4o, Claude 3.5, Gemini 1.5 Pro) nếu bị nhồi vào ngữ cảnh một bảng lương nhạy cảm hoặc một chính sách nghỉ phép của công ty khác, nó vẫn sẽ tự tin tóm tắt và tiết lộ cho người dùng.
- Khi chứng minh được rằng: **Cùng một câu hỏi** (*"Tôi có bao nhiêu ngày nghỉ phép?"*), người dùng Alice (AlphaPay) và Charlie (NovaGame) nhận về hai tập tài liệu hoàn toàn riêng biệt, số ngày phép khác nhau (15 ngày vs 12 ngày), và Alice hỏi lương thì hệ thống từ chối ngay từ tầng dữ liệu mà không chunk cấm nào lọt vào LLM context (`unauthorized_context_rate = 0%`), chúng ta đã chứng minh được:
  > **Ranh giới an toàn của hệ thống AI doanh nghiệp phải được thiết lập bằng kiến trúc phân quyền dữ liệu tất định (deterministic access control) từ bên ngoài LLM, chứ không trông chờ vào System Prompt.**

Khi ranh giới này đã vững chắc, toàn bộ các phần tiếp theo (tăng quy mô vector database, tích hợp SSO doanh nghiệp, mở rộng thêm phòng ban) chỉ là mở rộng kỹ thuật (engineering scaling), giả thuyết cốt lõi đã hoàn toàn khả thi.

---

## CÂU HỎI 2:
### So với kế hoạch ở Mission 1, bạn đã thay đổi quyết định hoặc thiết kế nào? Điều gì trong quá trình làm khiến bạn thay đổi?

So với bản thiết kế kiến trúc lý thuyết ở Mission 1, tôi đã thực hiện **4 thay đổi thiết kế mang tính bước ngoặt** khi bước vào hiện thực hóa Mission 2:

| Thành phần | Thiết kế ban đầu ở Mission 1 | Quyết định thay đổi ở Mission 2 (MVP) |
| :--- | :--- | :--- |
| **Mô hình điều phối (Orchestration)** | Sử dụng Autonomous AI Agent (ReAct / Tool-calling agent tự lập kế hoạch). | **Fixed Deterministic Pipeline (Quy trình tuần tự xác định)**: Lọc quyền ➜ Truy xuất ➜ Xử lý mâu thuẫn ➜ LLM ➜ Kiểm định trích dẫn. |
| **Cơ chế phân quyền** | ABAC/RBAC động phức tạp kèm engine đánh giá chính sách runtime. | **Deterministic Rule Matrix trên Metadata chuẩn hóa**: Đóng gói quyền đọc, tính áp dụng và phạm vi ngay trong metadata của tài liệu. |
| **Xác thực danh tính (Identity / SSO)** | Tích hợp hệ thống SSO doanh nghiệp (SAML / OAuth2 / Active Directory). | **Synthetic Persona Selector (Bộ chọn hồ sơ giả lập)**: Sử dụng danh sách tài khoản mẫu mang đầy đủ thuộc tính thực tế (công ty, phòng ban, vai trò, loại hợp đồng) để tập trung kiểm chứng ranh giới phân quyền tri thức thay vì sa đà vào dựng hạ tầng IAM. |
| **Xử lý mâu thuẫn dữ liệu** | Giao cho LLM tự đọc và phát hiện ngữ nghĩa mâu thuẫn trong câu hỏi. | **Authority Metadata Precedence**: Phân cấp rõ rệt thẩm quyền văn bản (Chính sách cấp Tập đoàn > Đơn vị > FAQ); phát hiện mâu thuẫn cùng thẩm quyền bằng quy tắc đối soát trước LLM. |

#### Điều gì trong quá trình làm khiến tôi thay đổi?
1. **Bài học về "Ảo tưởng Agentic" trong môi trường nhạy cảm chính sách**:
   Khi thử nghiệm Agent tự do gọi tool để tìm tài liệu, Agent thường xuyên bị lạc hướng khi người dùng hỏi các câu mập mờ, hoặc Agent cố gắng "suy luận giúp người dùng" bằng cách tự ý đọc chéo tài liệu giữa các công ty con. Điều này vi phạm nguyên tắc bảo mật. Tôi nhận ra: **Với bài toán chính sách nhân sự và tuân thủ pháp lý, tính nhất quán (Consistency) và khả năng kiểm toán (Auditability) của một Pipeline xác định quan trọng hơn tính linh hoạt khó đoán của một Autonomous Agent.**
2. **Tập trung vào kiểm chứng giả thuyết cốt lõi thay vì hạ tầng phụ trợ (Core Risk vs IAM Infrastructure)**:
   Ở Mission 1, tôi từng dự kiến tích hợp hệ thống SSO/Active Directory thực tế. Nhưng khi bắt tay vào triển khai MVP, tôi nhận thấy việc dựng hạ tầng SSO tốn nhiều thời gian mà không trực tiếp trả lời được câu hỏi cốt lõi: *"Liệu AI có lấy nhầm chính sách của công ty con khác hay không?"*. Việc chuyển sang mô hình chọn hồ sơ giả lập đa dạng (Persona Switcher) với đầy đủ metadata bối cảnh vừa giúp người đánh giá dễ dàng kiểm thử trực tiếp trên giao diện, vừa tập trung tối đa nguồn lực vào việc hoàn thiện tầng kiểm soát dữ liệu.

---

## CÂU HỎI 3:
### Trường hợp nào hiện khiến hệ thống dễ trả lời sai hoặc sử dụng sai tri thức nhất? Bạn phát hiện và kiểm soát rủi ro đó như thế nào?

#### 1. Trường hợp dễ gây sai lệch nhất:
Có 2 trường hợp hiện dễ khiến hệ thống trả lời sai hoặc sử dụng sai tri thức nhất:

1. **Trường hợp 1: Người dùng sử dụng từ ngữ đồng nghĩa phong phú (Paraphrase & Semantic Gap - Đã bộc lộ ở test case T08)**:
   - *Hiện tượng*: Người dùng không dùng từ khóa chuẩn trong quy chế (*"nghỉ phép"*) mà dùng các cách diễn đạt dân dã, tự nhiên (*"số ngày nghỉ hằng năm"*, *"chế độ nghỉ dưỡng"*).
   - *Nguy cơ*: Do bản MVP đang sử dụng bộ lọc từ khóa cứng (`detect_intent`) để phân loại chủ đề trước khi tìm kiếm, khi trượt từ khóa, hệ thống kết luận không có tài liệu và trả về `ABSTAIN` (từ chối oan khi thực tế có tài liệu hợp lệ).
2. **Trường hợp 2: Sai lệch từ Metadata tài liệu (Metadata Corruption / Outdated Tagging)**:
   - *Hiện tượng*: Một tài liệu thực tế đã bị thay thế nhưng người nhập liệu quên không cập nhật trường `effective_to` hoặc gắn nhầm tag `department`.
   - *Nguy cơ*: Vì hệ thống tin tưởng tuyệt đối vào metadata để lọc quyền, metadata sai sẽ dẫn đến việc cấp phát sai văn bản vào context của LLM.

#### 2. Cách phát hiện rủi ro:
- **Xây dựng bộ kiểm thử đối kháng đa bối cảnh (Adversarial Test Suite)**: Tôi xây dựng 60 test cases giả lập (`data/synthetic/tests/`) và bộ 8 test cases chuyên biệt (`evaluation/test_cases.json`) với đầy đủ các bẫy: câu hỏi bẫy bối cảnh công ty, bẫy quyền hạn, bẫy bản nháp (draft), câu hỏi mập mờ và câu hỏi dùng từ đồng nghĩa.
- **Quan sát kết quả thực nghiệm**: Tình huống `T08` đã được phát hiện ngay trong quá trình chạy `python -m scripts.evaluate`: hệ thống trả về `ABSTAIN` thay vì `ANSWER` khi gặp câu *"Số ngày nghỉ hằng năm của tôi là bao nhiêu?"*.

#### 3. Cách kiểm soát rủi ro trong hệ thống:
Hệ thống áp dụng nguyên tắc **"Thà từ chối trung thực (ABSTAIN) còn hơn trả lời sai (Hallucination)"** thông qua 4 chốt chặn kiểm soát:

1. **Nguyên tắc "Fail-Safe Default" (Mặc định an toàn)**: Khi không chắc chắn về chủ đề hoặc điểm tương đồng ngữ nghĩa dưới ngưỡng an toàn, hệ thống tự động rơi về trạng thái `ABSTAIN` kèm giải thích lịch sự, tuyệt đối không cho LLM "đoán mò".
2. **Chốt chặn Kiểm định Trích dẫn (Strict Citation Assertion)**: Tại [src/service.py](file:///d:/KieuQuy/Documents/Appota/src/service.py#L69-L75), hệ thống dùng mã kiểm tra nghiêm ngặt: Nếu câu trả lời sinh ra không có trích dẫn, hoặc đoạn trích dẫn không khớp 100% từng ký tự với văn bản nguồn được cấp phép, câu trả lời sẽ bị hủy bỏ ngay lập tức.
3. **Cơ chế ghi nhận Trace kiểm toán (Audit Logging)**: Mỗi truy vấn đều sinh ra một bản ghi audit trace ẩn chứa đầy đủ: danh sách tài liệu bị loại vì quyền, danh sách tài liệu bị loại vì hết hạn, quyết định của resolver và độ trễ xử lý. Nhờ đó, đội ngũ kỹ thuật có thể kiểm tra chính xác nguyên nhân vì sao hệ thống từ chối hoặc trả lời.
4. **Lộ trình nâng cấp**: Để giải quyết triệt để case `T08`, lộ trình tiếp theo sẽ thay thế hàm regex `detect_intent` bằng mô hình Dense Embedding đa ngôn ngữ kết hợp kỹ thuật Hybrid Search (BM25 + Vector) để bao quát trọn vẹn mọi biến thể ngôn ngữ tự nhiên của người dùng.
