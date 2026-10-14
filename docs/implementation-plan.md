# Kế hoạch triển khai Appota Knowledge Guard MVP

## 1. Mục tiêu và phạm vi

Chứng minh một câu hỏi giống hệt nhau có thể cho kết quả đúng khác nhau theo ngữ cảnh người dùng, trong khi tài liệu không được phép truy cập không bao giờ đi vào ngữ cảnh LLM. Dùng hoàn toàn dữ liệu giả lập. Trạng thái trả lời gồm `ANSWER`, `ABSTAIN`, `CONFLICT`, kèm citation và trace.

Luồng bắt buộc: **trusted user context → authorization → applicability → approved/current version → retrieval → authority/conflict resolution → context guard → LLM → citation validation**. Các quyết định về quyền, phạm vi, phiên bản và xung đột thuộc backend xác định, không giao cho LLM hoặc UI.

Giữ Python + Streamlit theo `plan.md` và `AGENT.md`. Backend là các module Python; UI Streamlit chỉ gọi service. FastAPI chỉ bổ sung nếu xuất hiện nhu cầu tích hợp thực tế, không phải điều kiện ban đầu. PostgreSQL + pgvector là hướng ưu tiên; nếu hạ tầng làm chậm MVP, dùng lưu trữ nhẹ hơn nhưng giữ nguyên thứ tự lọc và kiểm thử bất biến.

## 2. Phân công theo công cụ

| Phần | Công cụ thực hiện | Sở hữu | Đầu ra |
|---|---|---|---|
| Backend, dữ liệu, kiểm thử, đánh giá | Codex CLI trong terminal project này | `src/`, `data/`, `scripts/`, `tests/`, `evaluation/`, cấu hình chạy | Service ổn định, dữ liệu seed, test và kết quả thật |
| Frontend demo | Antigravity IDE, Gemini 3.8 Flash | `app.py` và thành phần giao diện riêng nếu cần | Streamlit UI nối service, trạng thái/citation/trace |
| Tích hợp và tài liệu cuối | Codex CLI sau khi nhận UI | `README.md`, hướng dẫn chạy, demo, kiểm thử tích hợp | Bản chạy được từ clone sạch |

Hai công cụ làm trên cùng repository. Không sửa đồng thời cùng file. Codex chốt contract backend và fixture trước khi Antigravity nối UI; Antigravity không tự thay đổi `src/` hoặc quy tắc bảo mật. Nếu UI cần dữ liệu khác, cập nhật contract trước rồi mới đổi cả hai phía.

### Contract giữa backend và frontend

```python
list_demo_users() -> list[UserSummary]
answer_question(user_id: str, question: str) -> AnswerResult
```

`UserSummary` có `user_id`, tên, company, department, team, canonical role, job level. `AnswerResult` có `status`, `answer`, `citations` (`document_id`, `title`, `version`, `section`), `reason`, và `trace`. Trace chỉ hiển thị dữ liệu an toàn cho demo; phần tên tài liệu bị từ chối cần được đánh dấu là thông tin debug giả lập, không là mẫu UI production. Service nhận `user_id`, tự tải ngữ cảnh tin cậy; UI không gửi role/company để quyết định quyền.

## 3. Các giai đoạn triển khai

### Giai đoạn 0 — Chốt nền tảng

- Codex tạo cấu trúc tối thiểu, dependency, `.env.example`, `.gitignore`, README khởi đầu; chọn storage/embedding/LLM theo điều kiện chạy thực tế.
- Chốt schema, enum, contract service và 8 ca đánh giá T01–T08. Seed có Group → Company → Department → Team, 6 user giả lập, tài liệu manager-only, HR-only, v1/v2/v3, FAQ kém thẩm quyền, conflict ngang thẩm quyền, ca thiếu bằng chứng.
- **Cổng hoàn thành:** chạy seed lặp lại được, không có secret, contract đủ để frontend làm việc.

### Giai đoạn 1 — Backend xác định (Codex CLI)

- Implement `can_read()` với explicit DENY > explicit ALLOW > inherited ALLOW > default DENY; tách applicability cho câu hỏi self-context.
- Lọc `APPROVED` và khoảng hiệu lực trước retrieval. Chỉ truy xuất trong tập document/version đã hợp lệ.
- Test Alice/Carol cùng câu hỏi phép năm cho nguồn khác nhau; Alice không đọc được HR/manager; Bob/Helen đúng quyền; v1/v2 không vào context.
- **Cổng hoàn thành:** các ca này qua test *không cần LLM*; zero unauthorized chunks trong LLM context thử nghiệm.

### Giai đoạn 2 — Trả lời và xử lý bằng chứng (Codex CLI)

- Chunk/embed/ingest một lần; truy xuất top-k trên tập hợp lệ. Resolver xử lý thứ bậc `OFFICIAL_POLICY > APPROVED_PROCEDURE > GUIDELINE > FAQ`, phát hiện conflict có kiểm soát theo seed, và từ chối khi bằng chứng thiếu.
- LLM chỉ diễn đạt bằng tiếng Việt từ các chunk đã qua guard. Validate schema và citation đối chiếu nguồn thực được cấp. Lỗi provider trả trạng thái lỗi hệ thống riêng, không giả làm `ABSTAIN`.
- Service trả `ANSWER`/`ABSTAIN`/`CONFLICT` cùng trace có request ID, số lượng sau từng bước, nguồn, version, quyết định và latency.
- **Cổng hoàn thành:** T01–T07 qua test tự động; query WFH thứ Sáu `ABSTAIN`; hai policy chính thức mâu thuẫn `CONFLICT`.

### Giai đoạn 3 — Frontend demo (Antigravity IDE, Gemini 3.8 Flash)

- Dùng contract đã chốt để làm `app.py`: sidebar chọn user giả lập và hiển thị profile; ô câu hỏi + nút hỏi; badge trạng thái; câu trả lời; citation; expander “Vì sao có câu trả lời này?” cho trace.
- Không cho UI chỉnh role/company để vượt trusted context. Hiển thị loading, lỗi service/provider rõ ràng, và chú thích dữ liệu hoàn toàn giả lập.
- **Cổng hoàn thành:** bằng UI, chuyển Alice ↔ Carol với cùng nguyên văn câu hỏi thấy nguồn/đáp án tương ứng; kiểm tra `ABSTAIN`, `CONFLICT`, citation và trace.

### Giai đoạn 4 — Tích hợp, đánh giá, bàn giao

- Codex chạy unit/e2e và kiểm tra UI smoke; ghi `evaluation/results.md` theo kỳ vọng → thực tế → đạt/chưa đạt → điều học được. T08 phải là giới hạn hoặc lỗi quan sát được thật, không dựng kết quả.
- Hoàn thiện README: setup từ clone sạch, seed/ingest/run/test, kiến trúc, dữ liệu giả lập, Mission 1 → Mission 2, ba câu hỏi bắt buộc, hạn chế, lưu ý secret.
- Deploy demo sau khi test lõi qua; kiểm tra link hoặc ghi lý do chỉ chạy local. Chuẩn bị script/video tối đa 5 phút và rà repository công khai, secret, citation, toàn bộ checklist Definition of Done.

## 4. Thứ tự và điểm giao việc

1. Codex hoàn thành Giai đoạn 0, xuất schema/fixture và service contract.
2. Codex hoàn thành Giai đoạn 1; đây là điều kiện để đầu tư UI.
3. Antigravity bắt đầu giao diện trên contract cố định trong khi Codex làm Giai đoạn 2, nhưng chỉ tích hợp đáp án thật sau khi service ổn định.
4. Codex và Antigravity kiểm tra chung Giai đoạn 3; Codex hoàn tất Giai đoạn 4.

Ước lượng phù hợp kế hoạch gốc ba ngày: **Ngày 1:** nền tảng và bộ lọc xác định; **Ngày 2:** retrieval, LLM, UI và lần deploy đầu; **Ngày 3:** kiểm thử, phát hiện giới hạn thật, README, deploy và video. Nếu thiếu thời gian, ưu tiên quyền truy cập → applicability → version → retrieval → citation → abstain/conflict → test; giảm polish UI trước.

## 5. Prompt giao việc cho Antigravity

> Đọc `docs/AGENT.md`, `docs/plan.md`, `docs/architecture.md` và `docs/implementation-plan.md`. Chỉ triển khai frontend Streamlit trong `app.py` (và file UI riêng nếu thật cần). Dùng `list_demo_users()` và `answer_question(user_id, question)` từ backend; không tự viết authorization, applicability, version filtering hoặc gọi LLM trực tiếp từ UI. Sidebar chọn synthetic user và hiển thị context; main có input, Ask, trạng thái ANSWER/ABSTAIN/CONFLICT, answer, citation, và expander trace. Xử lý loading/lỗi rõ ràng. Kiểm tra thủ công Alice/Carol cùng câu hỏi và các trạng thái ABSTAIN/CONFLICT. Báo file sửa, cách chạy, kết quả kiểm tra và vấn đề còn lại. Không sửa `src/`, `data/`, `tests/` nếu chưa thống nhất contract.

## 6. Tiêu chí hoàn tất bắt buộc

- Cùng câu hỏi phép năm: Alice lấy AlphaPay current policy, Carol lấy NovaGame current policy.
- Tỷ lệ chunk không được phép vào LLM context = **0** trên bộ test; default deny hoạt động.
- Version cũ/draft không được truy xuất; nguồn ưu tiên đúng authority.
- Câu trả lời có citation hợp lệ; thiếu bằng chứng → `ABSTAIN`; xung đột ngang thẩm quyền → `CONFLICT`.
- Có ít nhất 5 ca formal (mục tiêu T01–T08), một lỗi/giới hạn thật, README chạy từ clone sạch, không commit secret, và demo/video theo yêu cầu tài liệu gốc.
