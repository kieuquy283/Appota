# Kế hoạch xây dựng giao diện chatbot hỏi đáp có citation

## 1. Hiện trạng

Ứng dụng hiện đã có backend trả về các trường:

- `answer`: nội dung câu trả lời.
- `status`: một trong ba trạng thái `ANSWER`, `ABSTAIN`, `CONFLICT`.
- `citations`: danh sách tài liệu được dùng làm nguồn.
- `reason`: lý do từ chối trả lời hoặc phát hiện xung đột.
- `trace`: thông tin kiểm tra quyền, phạm vi áp dụng, phiên bản và nguồn được truy xuất.

Giao diện hiện tại chỉ hỗ trợ một lượt tra cứu. Mục tiêu tiếp theo là chuyển sang giao diện hội thoại nhiều lượt, trong đó mỗi câu trả lời giữ citation và audit trace riêng.

## 2. Mục tiêu

- Cho phép người dùng hỏi nhiều câu trong cùng một phiên.
- Hiển thị câu hỏi và câu trả lời dưới dạng bong bóng chat.
- Gắn nguồn trích dẫn với từng câu trả lời.
- Thể hiện rõ ba trạng thái `ANSWER`, `ABSTAIN`, `CONFLICT`.
- Không làm lẫn kết quả hoặc citation giữa các người dùng.
- Giữ khả năng kiểm tra pipeline phân quyền và truy xuất.
- Bảo đảm mọi citation đều thuộc nguồn backend đã cấp phép cho câu hỏi tương ứng.

## 3. Thiết kế giao diện

### 3.1. Bố cục

Sidebar tiếp tục chứa:

- Bộ chọn người dùng giả lập.
- Công ty, phòng ban, nhóm, vai trò và cấp độ.
- Các câu hỏi mẫu.
- Nút tạo cuộc trò chuyện mới.

Khu vực chính gồm:

- Tiêu đề và mô tả ngắn về Knowledge Guard.
- Lịch sử hội thoại.
- Bong bóng câu hỏi của người dùng.
- Bong bóng câu trả lời của trợ lý.
- Citation bên dưới từng câu trả lời.
- Audit trace trong vùng có thể mở rộng.
- Ô nhập câu hỏi cố định ở cuối bằng `st.chat_input`.

### 3.2. Cấu trúc một câu trả lời

Mỗi câu trả lời hiển thị:

1. Nội dung trả lời.
2. Trạng thái xử lý.
3. Citation đánh số `[1]`, `[2]`, ...
4. Khối **Nguồn tham khảo**.
5. Khối **Vì sao có câu trả lời này?** chứa audit trace.

Ví dụ:

```text
Bạn có 15 ngày nghỉ phép mỗi năm. [1]

Nguồn tham khảo
[1] Chính sách nghỉ phép AlphaPay
    ALPHA-LEAVE · v3 · Annual Leave
```

## 4. Quản lý trạng thái hội thoại

Dùng `st.session_state` để lưu lịch sử tin nhắn. Cấu trúc đề xuất:

```python
{
    "role": "assistant",
    "content": "...",
    "status": "ANSWER",
    "citations": [...],
    "reason": None,
    "trace": {...},
    "request_id": "...",
}
```

Quy tắc quản lý state:

- Mỗi câu hỏi và câu trả lời được thêm vào `chat_messages` theo đúng thứ tự.
- Mỗi câu trả lời lưu citation và trace riêng.
- Khi đổi người dùng, tạo phiên chat mới hoặc xóa lịch sử của người dùng trước.
- Nút **Cuộc trò chuyện mới** xóa lịch sử hiện tại.
- Câu hỏi mẫu được đưa vào cùng luồng xử lý với câu hỏi nhập thủ công.
- Một lỗi xử lý không được làm mất các tin nhắn trước đó.
- Có thể giới hạn số tin nhắn được giữ trong một phiên nếu lịch sử quá dài.

## 5. Tách cấu trúc UI

Tái cấu trúc `app.py` thành các hàm nhỏ:

```python
render_sidebar()
render_chat_history()
render_user_message()
render_assistant_message()
render_status()
render_citations()
render_audit_trace()
submit_question()
reset_conversation()
```

Mục đích:

- Dùng chung cách hiển thị citation cho mọi câu trả lời.
- Giảm logic lồng nhau trong `main()`.
- Kiểm soát thống nhất ba trạng thái kết quả.
- Dễ kiểm thử từng phần của giao diện.

## 6. Citation

### 6.1. Citation dạng thẻ nguồn

Backend hiện đã cung cấp đủ dữ liệu cho mỗi citation:

- `title`.
- `document_id`.
- `version`.
- `section`.

Mỗi nguồn được hiển thị dưới dạng một thẻ có số thứ tự:

```text
[1] Chính sách nghỉ phép AlphaPay
    Document: ALPHA-LEAVE
    Version: v3
    Section: Annual Leave
```

Citation phải được render trong chính bong bóng trả lời tương ứng, không dùng một danh sách nguồn chung cho toàn bộ phiên chat.

### 6.2. Citation trực tiếp trong nội dung

Nếu cần citation theo từng câu hoặc từng claim, mở rộng structured output của backend:

```python
answer = "Bạn có 15 ngày nghỉ phép mỗi năm. [S1]"
citation_ids = ["S1"]
```

Backend cần kiểm tra:

- Mọi mã `[Sx]` đều thuộc nguồn đã đưa vào LLM context.
- Không có citation không tồn tại.
- Kết quả `ANSWER` phải có ít nhất một citation.
- `ABSTAIN` không tạo citation giả.
- `CONFLICT` có thể liệt kê tất cả nguồn đang mâu thuẫn.
- Citation trả về phải khớp `document_id` và `version` của nguồn được chọn.

Phần mở rộng này liên quan đến:

- `src/llm.py`.
- `src/service.py`.
- `src/models.py` nếu cần bổ sung mã nguồn hoặc vị trí claim.

## 7. Hiển thị trạng thái

### 7.1. `ANSWER`

- Hiển thị câu trả lời trong bong bóng trợ lý.
- Hiển thị citation ngay bên dưới.
- Cho phép mở audit trace.

### 7.2. `ABSTAIN`

- Hiển thị cảnh báo màu vàng.
- Giải thích rằng tài liệu hiện có chưa đủ căn cứ.
- Hiển thị `reason` bằng ngôn ngữ dễ hiểu.
- Không tạo nguồn giả để làm câu trả lời có vẻ đầy đủ.

### 7.3. `CONFLICT`

- Hiển thị cảnh báo màu đỏ.
- Nêu rõ hệ thống phát hiện các chính sách cùng thẩm quyền đang mâu thuẫn.
- Liệt kê các citation tham gia xung đột.
- Hướng dẫn người dùng liên hệ chủ sở hữu chính sách khi phù hợp.

## 8. Audit trace

Audit trace tiếp tục nằm trong expander để giao diện chat gọn hơn. Nội dung cần giữ:

- User context.
- Tổng số tài liệu.
- Số tài liệu có quyền đọc.
- Số tài liệu áp dụng cho người dùng.
- Số phiên bản hiện hành.
- Tài liệu được truy xuất.
- Quyết định của authority resolver.
- Nguồn thực sự đi vào LLM context.
- Thời gian xử lý.
- Request ID.

Mỗi câu trả lời phải giữ trace riêng để người dùng có thể kiểm tra lại một lượt hỏi cũ.

## 9. Trạng thái tải và xử lý lỗi

Khi gửi câu hỏi:

- Hiển thị trạng thái “Đang kiểm tra quyền và tìm tài liệu…”.
- Ngăn gửi cùng một câu hỏi nhiều lần trong lúc đang xử lý.
- Giữ nguyên lịch sử hội thoại trong thời gian chờ.
- Khi backend lỗi, hiển thị một bong bóng lỗi có thể thử lại.
- Không ghi exception hoặc dữ liệu nội bộ nhạy cảm trực tiếp ra giao diện production.
- Ghi nhận `request_id` để phục vụ việc đối chiếu lỗi.

## 10. Bảo mật giao diện

- Escape nội dung câu hỏi, câu trả lời, tiêu đề và section trước khi render HTML.
- Không hiển thị nội dung tài liệu bị từ chối truy cập.
- Không đưa tên tài liệu mật bị chặn vào lịch sử chat.
- Citation chỉ lấy từ `AnswerResult.citations` đã được backend kiểm tra.
- Khi đổi người dùng, không tái sử dụng câu trả lời hoặc trace thuộc người dùng trước.
- Không dùng UI để tự suy luận quyền truy cập; backend tiếp tục là nơi quyết định quyền.

## 11. Kiểm thử

### 11.1. Kiểm thử chức năng

- Gửi nhiều câu hỏi liên tiếp và giữ đúng thứ tự.
- Mỗi câu trả lời giữ citation riêng.
- Nút tạo cuộc trò chuyện mới xóa đúng lịch sử.
- Câu hỏi mẫu đi qua cùng pipeline với câu hỏi nhập tay.
- Lỗi ở một câu hỏi không xóa lịch sử trước đó.

### 11.2. Kiểm thử citation

- Citation hiển thị đúng `document_id`, version và section.
- Citation luôn thuộc `llm_context_document_ids` và `llm_context_version_ids`.
- Kết quả `ANSWER` có citation hợp lệ.
- Citation của hai câu trả lời không bị trộn lẫn.
- Citation trực tiếp `[Sx]` được ánh xạ đúng sang thẻ nguồn.
- Citation không hợp lệ bị backend từ chối.

### 11.3. Kiểm thử ngữ cảnh người dùng

- Cùng một câu hỏi của Alice và Carol tạo nguồn khác nhau đúng theo công ty.
- Đổi người dùng không làm lộ lịch sử hoặc nguồn của người trước.
- Tài liệu HR và tài liệu quản lý không xuất hiện với người không có quyền.

### 11.4. Kiểm thử trạng thái

- `ANSWER` hiển thị nội dung và nguồn.
- `ABSTAIN` hiển thị lý do thiếu bằng chứng.
- `CONFLICT` hiển thị các nguồn mâu thuẫn.
- Màu sắc, nhãn và nội dung giải thích thống nhất.

### 11.5. Kiểm thử an toàn khi render

- Câu hỏi chứa HTML hoặc script không được thực thi.
- Nội dung tài liệu được escape đúng cách.
- Dữ liệu trace không phá vỡ bố cục.

## 12. Thứ tự triển khai

### Giai đoạn 1: Chat cơ bản

1. Thay `st.text_input` bằng `st.chat_input`.
2. Dùng `st.chat_message` để hiển thị hội thoại.
3. Thêm `chat_messages` vào `st.session_state`.
4. Thêm nút tạo cuộc trò chuyện mới.

### Giai đoạn 2: Citation và trạng thái

1. Tạo `render_citations()`.
2. Gắn citation vào từng tin nhắn trợ lý.
3. Tạo cách hiển thị riêng cho `ANSWER`, `ABSTAIN`, `CONFLICT`.
4. Đưa audit trace vào từng câu trả lời.

### Giai đoạn 3: An toàn ngữ cảnh

1. Xử lý đổi người dùng.
2. Kiểm tra citation với LLM context.
3. Escape mọi dữ liệu render bằng HTML.
4. Kiểm tra không rò rỉ tài liệu bị từ chối.

### Giai đoạn 4: Citation theo claim

1. Bổ sung mã nguồn `[S1]`, `[S2]` vào structured output.
2. Kiểm tra mã nguồn trong backend.
3. Chuyển mã nguồn thành số `[1]`, `[2]` trên UI.
4. Ánh xạ số citation sang thẻ nguồn.

### Giai đoạn 5: Kiểm thử và hoàn thiện

1. Chạy unit test hiện có.
2. Thêm kiểm thử cho lịch sử và citation.
3. Kiểm tra trực quan trên Streamlit.
4. Kiểm tra bố cục ở chiều rộng màn hình nhỏ.
5. Cập nhật README với ảnh và hướng dẫn sử dụng.

## 13. Tiêu chí hoàn thành

- Người dùng có thể hỏi nhiều câu trong cùng một phiên.
- Mỗi câu trả lời có nguồn riêng và không bị lẫn với câu khác.
- Citation luôn khớp với nguồn backend đã cấp phép.
- Đổi hồ sơ người dùng không làm rò rỉ lịch sử hoặc citation.
- Ba trạng thái `ANSWER`, `ABSTAIN`, `CONFLICT` dễ phân biệt.
- Audit trace kiểm chứng được quy trình phân quyền và retrieval.
- Giao diện hoạt động tốt trên desktop và màn hình chiều rộng nhỏ.
- Các kiểm thử backend hiện có tiếp tục đạt.
- Không có nội dung bị từ chối truy cập đi vào LLM context hoặc giao diện citation.

## 14. Ước lượng

- Giao diện chat và citation dạng thẻ: khoảng một ngày.
- Citation trực tiếp theo từng claim và kiểm tra structured output: khoảng nửa ngày.
- Kiểm thử, sửa lỗi và hoàn thiện responsive: khoảng nửa ngày.

Tổng thời gian dự kiến: khoảng hai ngày cho phiên bản hoàn chỉnh có kiểm thử.
