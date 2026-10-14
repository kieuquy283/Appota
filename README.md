# Appota Knowledge Guard — synthetic Mission 2 MVP

Prototype chứng minh rằng cùng một câu hỏi có thể dùng nguồn chính sách khác nhau theo người hỏi. **Toàn bộ tên người, tổ chức, chính sách và giá trị trong repository là dữ liệu giả lập; không đại diện Appota thật.**

## Trạng thái triển khai

Backend CLI, bộ kiểm thử và giao diện hội thoại đa lượt (Multi-Turn Chat with Citations) trên Streamlit (`app.py`) đã hoàn thành theo kế hoạch [chatbot-ui-citation-plan.md](docs/chatbot-ui-citation-plan.md). Hệ thống hỗ trợ trích dẫn nguồn (citations), hiển thị trạng thái xử lý (`ANSWER`, `ABSTAIN`, `CONFLICT`), audit trace bảo mật và cách ly ngữ cảnh người dùng. Chưa deploy hoặc cấu hình provider LLM/embedding thật.

## Luồng xử lý

`user_id` → trusted synthetic profile → access filter → applicability → approved/current version → retrieval trên tập hợp lệ → authority/conflict → context guard → generation → citation validation.

Phân quyền dùng explicit DENY trước ALLOW và default deny. Applicability chỉ áp dụng cho câu hỏi về chính người dùng. Version phải `APPROVED`, `effective_from <= query_date` và `effective_to` rỗng hoặc lớn hơn `query_date`. `OFFICIAL_POLICY > APPROVED_PROCEDURE > GUIDELINE > FAQ`. Hai nguồn đang hiệu lực cùng thẩm quyền nhưng khác giá trị dẫn tới `CONFLICT`; thiếu bằng chứng dẫn tới `ABSTAIN`.

## Chạy backend từ clone sạch

Yêu cầu Python 3.10+. Backend offline chỉ dùng thư viện chuẩn, không cần `pip install`.

```powershell
python -m unittest discover -s tests -v
python -m scripts.evaluate
python -m scripts.demo U01 "Tôi có bao nhiêu ngày nghỉ phép?"
python -m scripts.demo U03 "Tôi có bao nhiêu ngày nghỉ phép?"
streamlit run app.py
```

Kết quả dự kiến: Alice (`U01`) dùng `ALPHA-LEAVE v3` với 15 ngày/năm; Carol (`U03`) dùng `NOVA-LEAVE v1` với 12 ngày/năm. `scripts.evaluate` ghi lại kết quả thật vào `evaluation/results.md`.

## Backend contract cho Streamlit

```python
from src.service import list_demo_users, answer_question

users = list_demo_users()
result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?")
print(result.status, result.answer, result.citations, result.trace)
```

UI chỉ gửi `user_id` và `question`; backend tự lấy company/department/role từ seed. `AnswerResult` có `status`, `answer`, `citations`, `reason`, `trace`, hỗ trợ `to_dict()`. Mỗi citation hiện tên văn bản, phiên bản, mục và một đoạn trích nguyên văn từ đúng phiên bản được phép truy cập; giao diện không hiển thị JSON kỹ thuật khi xem dẫn chứng.

## Tùy chọn provider

Không có API key, backend chạy chế độ trả lời trích xuất offline và truy xuất bằng vector từ vựng; chế độ này phục vụ kiểm thử quy tắc, **chưa chứng minh chất lượng semantic retrieval hoặc LLM**. Muốn bật hosted semantic embedding và LLM, đặt biến môi trường theo `.env.example`:

- `EMBEDDING_API_KEY`, `EMBEDDING_MODEL`, `EMBEDDING_BASE_URL` cho endpoint embeddings tương thích OpenAI.
- `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL` cho chat completions tương thích OpenAI.

Ứng dụng không tự đọc file `.env`; cấu hình biến môi trường tại shell/hosting. Không commit API key. Kết quả và chi phí provider phụ thuộc cấu hình, hiện chưa được kiểm thử.

## Dữ liệu và ca đánh giá

`data/seed.json` chứa Group → Company → Department → Team, 6 user, tài liệu HR/manager, 3 version phép năm AlphaPay, chính sách WFH chính thức so với FAQ, conflict ngang thẩm quyền và tình huống thiếu bằng chứng. Các ca T01–T08 ở `evaluation/test_cases.json`; kết quả thực tế ở `evaluation/results.md`. T08 hiện fail do cách diễn đạt khác không được query intent classifier nhận ra.

## Giới hạn hiện tại

- Chưa có SSO, IAM thật, quản trị policy, frontend, deployment hoặc GitHub public.
- Chưa dùng PostgreSQL/pgvector; dữ liệu nhỏ được đọc từ JSON. Embedding API là tùy chọn và cache trong bộ nhớ tiến trình.
- Conflict detection dựa trên topic/value có cấu trúc trong metadata; chưa phát hiện mâu thuẫn tự do trong văn bản.
- Câu hỏi tham chiếu công ty khác và nhiều cách diễn đạt ngoài tập intent định sẵn có thể `ABSTAIN` dù có nguồn phù hợp.
- Chưa kiểm tra provider LLM, semantic embedding và khả năng chống prompt injection qua thử nghiệm đối kháng.

## Mission 1 → Mission 2

MVP thu hẹp về ranh giới truy xuất có kiểm soát: synthetic identity, ACL xác định, không autonomous agent. Trọng tâm là ngăn nguồn sai ngữ cảnh hoặc không được phép đi vào LLM, rồi mới xét chất lượng câu trả lời.

1. **Phần quan trọng nhất:** access/applicability/version filtering trước retrieval. Nếu cùng câu hỏi chọn đúng nguồn cho Alice và Carol và chặn được nguồn HR, giả thuyết lõi có bằng chứng ban đầu.
2. **Thay đổi thiết kế:** bỏ autonomous agent và kết nối dữ liệu thật; dùng seed giả lập và orchestration rõ ràng để kiểm thử độc lập.
3. **Rủi ro lớn nhất hiện quan sát:** cách diễn đạt khác có thể bị phân loại sai (T08). Hệ thống trả `ABSTAIN` thay vì bịa đáp án; cần mở rộng query understanding và đánh giá thêm trên câu hỏi thực tế.

## Bảo mật và đánh giá

Không đưa tài liệu bị từ chối, draft hoặc version cũ vào LLM context. Citation phải đối chiếu với nguồn thực được cấp. Debug trace của demo chỉ công bố số lượng tài liệu bị chặn; production cần giới hạn trace theo quyền. Kiểm thử hiện có 9 unit/integration tests và 8 ca formal, trong đó T08 là thất bại quan sát được. Kết quả trên corpus giả lập nhỏ không phải cam kết độ tin cậy production.
