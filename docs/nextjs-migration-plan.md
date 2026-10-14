# Kế hoạch chuyển giao diện sang Next.js

## Mục tiêu và phạm vi

Thay giao diện Streamlit trong `app.py` bằng giao diện Next.js để triển khai trên Vercel. Giữ logic hỏi đáp và kiểm soát quyền trong `src/`: chọn hồ sơ giả lập, lọc tài liệu theo quyền, chọn phiên bản có hiệu lực, xử lý mâu thuẫn, tạo câu trả lời và kiểm tra trích dẫn. Dữ liệu tiếp tục là dữ liệu giả lập.

Kết quả cần giữ được hành vi hiện tại: nhiều lượt hỏi trong một cuộc trò chuyện; cùng câu hỏi cho hai người có bối cảnh khác nhau cho kết quả khác nhau; đổi người hỏi thì xóa cuộc trò chuyện; câu trả lời có tên tài liệu và đoạn trích nguyên văn; thông báo dễ hiểu khi thiếu dữ liệu, tài liệu mâu thuẫn hoặc dịch vụ gặp lỗi. Giao diện không hiển thị mã tài liệu, trace, tên model hay thông số xử lý.

## Kiến trúc chọn cho MVP

```text
Trình duyệt → Next.js (Vercel, project giao diện)
            → API Python/FastAPI (Vercel, project API)
            → src/service.py → dữ liệu giả lập + OpenRouter
```

- Next.js dùng App Router và TypeScript. Một trang chủ hiển thị giao diện chat; các thành phần tương tác là Client Components. Các khóa bí mật chỉ có ở phía máy chủ.
- FastAPI chỉ làm lớp HTTP mỏng gọi `list_demo_users()` và `answer_question()`. Quyền truy cập và lựa chọn tài liệu vẫn được quyết định ở Python; trình duyệt chỉ gửi `user_id` và câu hỏi trong phạm vi demo.
- Triển khai hai Vercel project từ cùng repository để tránh phụ thuộc Vercel Services đang ở Private Beta. Dùng Next.js Route Handler làm cổng gọi tới API Python, nhờ đó trình duyệt gọi cùng origin. URL backend và khóa kết nối giữa hai dịch vụ chỉ nằm trong biến môi trường phía máy chủ; FastAPI kiểm tra khóa kết nối này để hạn chế gọi trực tiếp vào API công khai. Nếu sau này được cấp Vercel Services, có thể gộp về một project.
- Không lưu khóa OpenRouter trong Next.js hoặc gửi khóa xuống trình duyệt. Python API nhận `LLM_API_KEY`, `EMBEDDING_API_KEY` và cấu hình model từ biến môi trường Vercel.

## Cấu trúc dự kiến

```text
web/
  app/page.tsx                 # Trang chat
  app/api/users/route.ts       # Chuyển tiếp danh sách người dùng demo
  app/api/answer/route.ts      # Chuyển tiếp câu hỏi tới Python API
  components/UserSelector.tsx
  components/ChatConversation.tsx
  components/AnswerCard.tsx
  components/CitationCard.tsx
  components/QuestionComposer.tsx
  lib/types.ts
  app/globals.css
api/
  index.py                     # FastAPI: /users, /answer
src/                           # Logic Python hiện có
data/                          # Tài liệu giả lập hiện có
```

`web/` là root của project Next.js. Project API dùng root repository, đặt Framework Preset là Other và dùng `api/index.py` làm Python entrypoint để có thể import `src/` và đọc `data/`. Cần xác nhận routing và đường dẫn Python trong bản preview trước khi dùng production domain; root hiện có `app.py` của Streamlit nên phải kiểm tra Vercel chọn đúng entrypoint API.

## Hợp đồng dữ liệu

- `GET /users`: trả danh sách người dùng giả lập gồm `user_id`, tên, công ty, phòng ban, nhóm và loại hợp đồng để chọn trong bản demo. Không trả thông tin cá nhân không cần thiết.
- `POST /answer`: nhận `{ "user_id": "U01", "question": "..." }`; kiểm tra khóa kết nối từ Next.js, chuỗi rỗng và độ dài hợp lý, rồi gọi `answer_question()`.
- Kết quả trả về trình duyệt chỉ gồm `status`, `answer`, `reason` nếu cần, và `citations` với `title`, `section`, `excerpt`. Không gửi `trace`, mã tài liệu, phiên bản nội bộ hoặc lỗi thô của provider xuống trình duyệt.
- `ANSWER`: hiển thị câu trả lời cùng các đoạn trích. `ABSTAIN`: thông báo chưa đủ thông tin. `CONFLICT`: thông báo các tài liệu chưa thống nhất và cho xem từng đoạn trích. Lỗi dịch vụ: thông báo thử lại sau và giữ các tin nhắn trước đó.

## Các bước thực hiện

1. **Chốt hành vi hiện có.** Ghi lại ảnh màn hình desktop/mobile và các tình huống demo đang chạy. Chốt nội dung giao diện dễ hiểu, đặc biệt thẻ dẫn chứng và trạng thái thiếu thông tin.
2. **Tạo API Python.** Thêm FastAPI adapter, schema yêu cầu/phản hồi, giới hạn dữ liệu trả ra và xử lý lỗi. Viết test cho API để chứng minh cùng câu hỏi hai người cho hai nguồn khác nhau, nguồn ngoài quyền không được trả ra, và đoạn trích khớp văn bản.
3. **Dựng giao diện Next.js.** Tạo trang chat, danh sách người hỏi, hồ sơ ngắn, câu hỏi gợi ý, ô nhập, trạng thái chờ, câu trả lời và thẻ dẫn chứng. Dùng CSS hiện có làm tham chiếu màu sắc/bố cục nhưng dựng lại bằng React; hỗ trợ màn hình hẹp và bàn phím.
4. **Nối giao diện với API.** Next.js Route Handlers gọi Python API bằng khóa kết nối chỉ có ở máy chủ. Lịch sử hội thoại giữ trong bộ nhớ tab; đổi người hỏi hoặc chọn “Cuộc trò chuyện mới” sẽ xóa lịch sử. Mỗi kết quả giữ dẫn chứng riêng, kể cả khi nhiều câu hỏi được gửi liên tiếp.
5. **Kiểm thử hoàn chỉnh.** Chạy test Python, kiểm tra build/typecheck Next.js và kiểm thử trình duyệt cho các ca: hai bối cảnh khác nhau; thiếu dữ liệu; mâu thuẫn; giới hạn quyền; đổi người hỏi; lỗi API/model; trích dẫn đúng văn bản; giao diện mobile; không lộ biến môi trường hoặc trường kỹ thuật.
6. **Triển khai preview rồi production.** Deploy API trước và xác nhận dữ liệu được đóng gói; đặt biến môi trường OpenRouter và khóa kết nối ở project API. Deploy Next.js với URL API và cùng khóa kết nối ở biến môi trường chỉ dùng phía máy chủ. Kiểm tra các ca trên preview, sau đó mới trỏ production domain.

## Điều kiện hoàn thành

- U01 và U03 hỏi cùng câu về phép năm nhận kết quả và dẫn chứng thuộc đúng công ty của từng người.
- Không có đoạn trích ngoài quyền, tài liệu hết hiệu lực hoặc mã kỹ thuật trong phản hồi hiển thị.
- Trích dẫn thể hiện rõ đoạn nào thuộc tài liệu nào; bấm/xem nguồn không mở JSON kỹ thuật.
- Đổi người hỏi xóa lịch sử trước đó; lỗi mạng hoặc model không làm mất hội thoại.
- Test Python, kiểm tra kiểu, build Next.js và các ca trình duyệt đều đạt trên preview Vercel.

## Điểm cần giữ trong thiết kế

Hồ sơ trong MVP là hồ sơ giả lập do người dùng tự chọn; đây chưa phải đăng nhập nhân sự thật. Nếu triển khai cho dữ liệu thật, cần đưa xác thực và ánh xạ người dùng từ hệ thống danh tính đáng tin cậy vào API trước khi mở quyền truy cập. Khóa OpenRouter hiện chỉ được cấu hình ở máy chủ; tạo khóa mới khi đưa bản demo lên môi trường công khai.

Tham khảo: [Next.js trên Vercel](https://vercel.com/docs/frameworks/full-stack/nextjs), [Server và Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components), [FastAPI trên Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Vercel Services](https://vercel.com/docs/services).
