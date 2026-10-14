# Giới hạn đã quan sát và chưa kiểm chứng

- **Đã quan sát:** T08 thất bại. Câu “Số ngày nghỉ hằng năm của tôi là bao nhiêu?” có nguồn phù hợp nhưng bộ nhận diện intent offline trả `ABSTAIN`. Xem `evaluation/results.md`.
- Retrieval offline dùng vector từ vựng; semantic embedding chỉ chạy khi cấu hình endpoint và chưa được kiểm thử trong môi trường này.
- LLM provider chưa được cấu hình/kiểm thử; chế độ mặc định tạo câu trả lời trích xuất theo `value` của seed.
- Phát hiện conflict dựa trên `topic` và `value` có cấu trúc, chưa phát hiện mâu thuẫn trong văn bản tự do.
- Dữ liệu và danh tính đều giả lập; chưa có SSO, IAM, workflow duyệt chính sách, PostgreSQL/pgvector hoặc kiểm thử quy mô lớn.
- Frontend Streamlit, deploy công khai và video chưa được thực hiện.
