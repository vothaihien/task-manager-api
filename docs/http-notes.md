## 1. Ở phần 1, request -v đầu tiên gửi header nào? Response trả Content-Type gì?

    - Header là: Host: jsonplaceholder.typicode.com
    - Content-Type là: application/json; charset=utf-8

## 2. POST ở Phần 1 trả mã nào? Server giả lập này có thực sự lưu bài viết mới không, và bạn kiểm tra bằng cách nào?

    - Mã trả ra là 201
    - Không, tôi kiểm tra bằng cách tôi GET đến server với mã id mà phần body trả ra khi POST

## 3. Chọn mã HTTP đúng theo thiết kế của bạn cho từng tình huống:

    a. Member gọi xoá một task trong dự án mình tham gia (403)
    b. Người lạ (không thuộc dự án) gọi xem task của dự án đó (404)
    c. Gọi API với token đã hết hạn (401)
    d. Đăng ký với email đã tồn tại (409)
    e. Tạo task có due_date trước start_date (422)
    f. Gửi body JSON thiếu dấu ngoặc đóng (400)
    g. Server gặp lỗi bất ngờ trong code (chia cho 0) (500)

## 4. Vì sao HTTP là stateless, và hệ quả của điều đó với cách ta xác thực?

Vì server sẽ không nhớ những gì giữa 2 request. Vì vậy không thể đăng nhập 1 lần rồi thôi, mà mỗi lần request sẽ cần kèm theo token. Token này sẽ cho server biết bạn là ai và đã giao tiếp gì với server trước đó. Cho phép là có thể request cho các server chạy song song.
