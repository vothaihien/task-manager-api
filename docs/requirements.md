### 1. Yêu cầu dự án

#### 1.1 Yêu cầu chức năng chính

- Người dùng có thể đăng ký tài khoản bằng email và mật khẩu.
- Người dùng có thể đăng nhập và nhận access token có thời hạn.
- Hệ thống có đúng ba vai trò trong phạm vi dự án: **Owner** (người tạo dự án), **Manager** và **Member**. Mỗi người dùng là Owner của dự án mình tạo; vai trò Manager hoặc Member có hiệu lực riêng trong từng dự án.
- Owner và Manager có thể tạo task; Member chỉ có thể xem task và sửa một số trường của task được giao cho mình. Quyền cụ thể được quy định trong ma trận dưới đây.
- Task có tên, mô tả, trạng thái, mức ưu tiên, ngày bắt đầu, ngày kết thúc dự kiến và người được giao.
- Người được giao task phải đang là thành viên (Manager hoặc Member) của chính dự án chứa task đó.
- Ngày kết thúc dự kiến không được trước ngày bắt đầu.
- API trả mã HTTP và thông báo lỗi phù hợp với loại lỗi; không dùng thao tác xác nhận trên giao diện làm điều kiện của API.

#### 1.2 Ma trận quyền theo dự án

`Y` = được phép; `N` = không được phép; `Được giao` = chỉ áp dụng với task được giao cho Member đó. Người ngoài dự án không có các quyền trong ma trận.

| Hành động | Owner | Manager | Member |
|---|---:|---:|---:|
| Sửa/xoá dự án | Y | N | N |
| Thêm/xoá thành viên | Y | Y | N |
| Tạo task | Y | Y | N |
| Sửa task | Y | Y | Được giao |
| Xoá task | Y | Y | N |
| Xem task | Y | Y | Y |

Quy tắc bổ sung: Owner có thể gán hoặc thay đổi vai trò. Manager có thể thêm Member và xoá Member, nhưng không thể thay đổi vai trò hoặc xoá Owner/Manager. Member chỉ được sửa mô tả và trạng thái của task được giao; Owner/Manager mới được sửa người được giao, mức ưu tiên và ngày dự kiến.

#### 1.3 Yêu cầu phi chức năng chính

- Mật khẩu phải được hash trước khi lưu vào cơ sở dữ liệu.
- API phải yêu cầu token hợp lệ cho các thao tác cần xác thực.
- Danh sách dữ liệu phải hỗ trợ phân trang để giảm tải.
- API cần phản hồi trong thời gian bình thường dưới 300ms cho các truy vấn cơ bản.
- Hệ thống cần có log để theo dõi hoạt động và lỗi.
- Hệ thống phải có test cho các luồng chính như đăng ký, đăng nhập, quản lý dự án và công việc.
- Dự án phải chạy được bằng Docker để dễ triển khai và kiểm thử môi trường.

### 2. User story và tiêu chí chấp nhận

Các mã HTTP dưới đây là kết quả của API. `400` dùng cho request sai định dạng/thiếu trường bắt buộc; `401` cho thiếu hoặc token không hợp lệ/hết hạn; `403` cho thành viên đã xác thực nhưng thiếu quyền; `404` cho tài nguyên không tồn tại hoặc người gọi không phải thành viên của dự án; `409` cho xung đột như email đã dùng; `422` cho dữ liệu đúng định dạng nhưng vi phạm quy tắc nghiệp vụ.

#### US-01: Đăng ký tài khoản

Với tư cách là khách, tôi muốn đăng ký tài khoản bằng email và mật khẩu, để sử dụng hệ thống quản lý công việc.

Tiêu chí chấp nhận:

- Request hợp lệ với email chưa tồn tại và mật khẩu từ 8 ký tự trả `201`; response chứa thông tin tài khoản nhưng không chứa mật khẩu hoặc hash.
- Email đã tồn tại trả `409` với mã lỗi `EMAIL_ALREADY_EXISTS`.
- Thiếu email/mật khẩu hoặc JSON sai định dạng trả `400`; mật khẩu dưới 8 ký tự trả `422`.
- Mật khẩu được lưu dưới dạng hash; đăng nhập bằng thông tin vừa đăng ký trả `200`.

#### US-02: Đăng nhập

Với tư cách là người dùng đã đăng ký, tôi muốn đăng nhập bằng email và mật khẩu, để truy cập dữ liệu của mình.

Tiêu chí chấp nhận:

- Email và mật khẩu hợp lệ trả `200` cùng access token có thời hạn 60 phút.
- Email hoặc mật khẩu sai trả `401`; response không phân biệt email không tồn tại với mật khẩu sai.
- API cần xác thực khi không có token, token sai hoặc token hết hạn trả `401`.

#### US-03: Tạo dự án

Với tư cách là người dùng đã đăng nhập, tôi muốn tạo dự án, để tổ chức công việc.

Tiêu chí chấp nhận:

- Request có tên dự án hợp lệ trả `201`; người tạo được ghi nhận là Owner.
- Thiếu tên hoặc request sai định dạng trả `400`; tên rỗng sau khi loại khoảng trắng trả `422`.
- Không có token hợp lệ trả `401`.

#### US-04: Xem danh sách và chi tiết dự án

Với tư cách là thành viên dự án, tôi muốn xem danh sách và chi tiết các dự án mình tham gia.

Tiêu chí chấp nhận:

- `GET` danh sách dự án trả `200` chỉ với dự án người dùng là thành viên; response có metadata phân trang.
- `GET` chi tiết dự án mà người dùng không tham gia hoặc không tồn tại trả `404`.
- Request không có token hợp lệ trả `401`.

#### US-05: Cập nhật dự án

Với tư cách là Owner, tôi muốn cập nhật thông tin dự án, để thông tin dự án luôn chính xác.

Tiêu chí chấp nhận:

- Owner gửi dữ liệu cập nhật hợp lệ nhận `200`; `GET` dự án sau đó trả về đúng các giá trị vừa cập nhật.
- Manager hoặc Member gọi cập nhật dự án nhận `403`.
- Dự án không tồn tại hoặc người gọi không thuộc dự án nhận `404`; request sai định dạng nhận `400`; không có token hợp lệ nhận `401`.

#### US-06: Xoá dự án

Với tư cách là Owner, tôi muốn xoá dự án không còn sử dụng, để dự án không xuất hiện trong danh sách đang hoạt động.

Tiêu chí chấp nhận:

- Owner xoá dự án thành công nhận `204`; dự án được đánh dấu đã xoá và không còn xuất hiện trong danh sách dự án đang hoạt động (`200`).
- Manager hoặc Member gọi xoá dự án nhận `403`; người ngoài dự án hoặc dự án không tồn tại nhận `404`; không có token hợp lệ nhận `401`.

#### US-07: Quản lý thành viên và vai trò

Với tư cách là Owner hoặc Manager, tôi muốn thêm và xoá thành viên, để quản lý quyền truy cập dự án.

Tiêu chí chấp nhận:

- Thêm một người dùng đang tồn tại thành viên mới trả `201`; người dùng đã là thành viên trả `409`.
- Owner có thể gán vai trò Manager hoặc Member. Manager chỉ có thể thêm/xoá Member; yêu cầu Manager gán vai trò, hoặc xoá Owner/Manager, trả `403`.
- Xoá thành viên thành công trả `204`; sau đó người bị xoá gọi API dự án/task nhận `404`.
- Dự án không tồn tại hoặc người gọi không phải thành viên trả `404`; không có token hợp lệ trả `401`.

#### US-08: Tạo task

Với tư cách là Owner hoặc Manager, tôi muốn tạo task trong dự án, để giao và theo dõi công việc.

Tiêu chí chấp nhận:

- Tạo task với dữ liệu hợp lệ trả `201`; sau đó `GET` task trả `200` và đúng dữ liệu đã tạo.
- Chỉ Owner/Manager mới tạo được task; Member gọi tạo task nhận `403`.
- Gán task cho người không phải thành viên đang hoạt động của dự án trả `422`.
- Ngày kết thúc trước ngày bắt đầu trả `422`; thiếu trường bắt buộc/sai định dạng trả `400`.
- Dự án không tồn tại hoặc người gọi không thuộc dự án trả `404`; không có token hợp lệ trả `401`.

#### US-09: Xem, lọc và phân trang task

Với tư cách là thành viên dự án, tôi muốn xem task và lọc theo trạng thái hoặc mức ưu tiên, để tìm công việc cần xử lý.

Tiêu chí chấp nhận:

- Thành viên gọi danh sách task nhận `200` với các task của dự án và metadata gồm trang hiện tại, kích thước trang, tổng số bản ghi và tổng số trang.
- Tham số trạng thái hoặc mức ưu tiên hợp lệ chỉ trả task khớp bộ lọc; giá trị lọc không hợp lệ trả `422`.
- Task không tồn tại hoặc người gọi không phải thành viên dự án nhận `404`; không có token hợp lệ nhận `401`.

#### US-10: Cập nhật task và trạng thái

Với tư cách là Owner, Manager hoặc Member được giao task, tôi muốn cập nhật task phù hợp với quyền của mình, để duy trì thông tin và tiến độ chính xác.

Tiêu chí chấp nhận:

- Owner/Manager cập nhật trường được phép thành công trả `200`; `GET` task sau đó trả đúng giá trị vừa cập nhật.
- Member chỉ cập nhật mô tả hoặc trạng thái task được giao cho mình; sửa task không được giao hoặc sửa trường bị hạn chế trả `403`.
- Chuyển trạng thái ngoài luồng đã quy định trả `422`; ngày kết thúc trước ngày bắt đầu hoặc người được giao không phải thành viên dự án trả `422`.
- Task không tồn tại hoặc người gọi không phải thành viên dự án nhận `404`; không có token hợp lệ nhận `401`.

#### US-11: Xoá task

Với tư cách là Owner hoặc Manager, tôi muốn xoá task không còn cần thiết, để danh sách công việc đang hoạt động chính xác.

Tiêu chí chấp nhận:

- Owner/Manager xoá task thành công nhận `204`; lần `GET` tiếp theo nhận `404`.
- Member gọi xoá task nhận `403`.
- Task không tồn tại hoặc người gọi không phải thành viên dự án nhận `404`; không có token hợp lệ nhận `401`.

#### US-12: Xem hồ sơ cá nhân

Với tư cách là người dùng đã đăng nhập, tôi muốn xem hồ sơ của mình, để kiểm tra thông tin tài khoản.

Tiêu chí chấp nhận:

- `GET` hồ sơ cá nhân với token hợp lệ trả `200` cùng email và thông tin hồ sơ; không trả mật khẩu hoặc hash mật khẩu.
- Không có token, token không hợp lệ hoặc hết hạn trả `401`.

### 3. MVP và phạm vi

**MVP (Minimum Viable Product)** là phiên bản nhỏ nhất vẫn dùng được. Ta cần xác định rõ cái gì không làm để tránh kéo dài phạm vi.

#### 3.1 Phạm vi MVP của Task Manager

**Có:**

- Đăng ký tài khoản.
- Đăng nhập và xác thực bằng token.
- Quản lý dự án.
- Quản lý công việc.
- Phân quyền theo ba vai trò Owner, Manager và Member.
- API RESTful cơ bản với xử lý lỗi rõ ràng.
- Hỗ trợ phân trang cho danh sách dữ liệu.
- Chạy ở môi trường Docker.

**Chưa có (để sau):**

- Thông báo email.
- Upload file đính kèm.
- Giao diện web người dùng.
- Báo cáo trực quan, dashboard phức tạp.
- Tích hợp webhook hoặc hệ thống thông báo realtime.
- Tự động hóa workflow nâng cao.

### 4. Yêu cầu phi chức năng cho dự án này

#### 4.1 Bảo mật

- Mật khẩu được hash trước khi lưu vào cơ sở dữ liệu.
- API yêu cầu access token hợp lệ cho các endpoint cần bảo vệ; access token hết hạn sau 60 phút.
- Người dùng chỉ thấy dữ liệu của mình hoặc dữ liệu thuộc về dự án mà họ được phân quyền.
- Không lộ thông tin nhạy cảm trong lỗi trả về cho client.

#### 4.2 Hiệu năng

- Danh sách dự án và công việc có hỗ trợ phân trang.
- Phản hồi API thông thường dưới 300ms cho các truy vấn cơ bản trong điều kiện tải nhẹ.
- Hệ thống cần tránh truy vấn không cần thiết và tối ưu các API đọc dữ liệu.

#### 4.3 Chất lượng

- Cần có test bao phủ các luồng chính: đăng ký, đăng nhập, tạo dự án, quản lý công việc, kiểm tra quyền truy cập.
- Test phải kiểm tra các trường hợp lỗi và dữ liệu không hợp lệ.
- Mã nguồn cần tuân thủ các chuẩn lập trình và dễ mở rộng trong tương lai.

#### 4.4 Vận hành

- Ứng dụng phải chạy được bằng Docker.
- Hệ thống cần có log để ghi lại lỗi, truy cập và hoạt động quan trọng.
- Cấu hình môi trường phải tách biệt rõ ràng giữa development, testing và production.
- Dễ triển khai và dễ khởi động lại khi cần.

### 5. Tóm tắt yêu cầu dự án

Dự án Task Manager API tập trung vào việc cung cấp nền tảng quản lý dự án và công việc cho người dùng cá nhân và nhóm nhỏ. Hệ thống phải đảm bảo an toàn, dễ sử dụng và hỗ trợ các chức năng cơ bản từ đăng ký, đăng nhập, quản lý dự án, quản lý công việc, đến phân quyền theo quyền truy cập. MVP chỉ tập trung vào các tính năng cốt lõi, không đi quá xa vào các tính năng ngoài phạm vi để giữ cho sản phẩm vừa dùng được và dễ triển khai.

### 6. Các quyết định đã chốt

- **Vai trò:** Mỗi dự án có ba vai trò Owner, Manager và Member. Owner tạo dự án, có toàn quyền quản lý dự án; Manager quản lý thành viên Member và task nhưng không sửa/xoá dự án; Member chỉ xem task và sửa mô tả/trạng thái task được giao. Tách ba vai trò để quyền quản lý nhóm không đồng nghĩa quyền sở hữu dự án; ma trận quyền tại mục 1.2 là nguồn chuẩn khi có nội dung khác mâu thuẫn.
- **Xoá dự án:** Dùng soft delete, không xoá dây chuyền task. Dự án đã xoá và task bên trong không còn truy cập qua API thông thường; dữ liệu task được giữ lại để bảo toàn lịch sử và không xoá nhầm dữ liệu liên quan.
- **Xoá task và thành viên:** Xoá task là xoá mềm khỏi API đang hoạt động để giữ lịch sử; xoá thành viên thu hồi quyền truy cập ngay để quyền cũ không còn hiệu lực. Chỉ Owner được thay đổi vai trò; Manager chỉ được thêm/xoá Member.
- **Mã lỗi quyền truy cập:** Người ngoài dự án nhận `404` cho tài nguyên dự án/task để không tiết lộ sự tồn tại của tài nguyên. Thành viên đã xác thực nhưng thiếu quyền nhận `403`.
- **Token:** Access token có hiệu lực 60 phút; token hết hạn trả `401`. Refresh token không thuộc phạm vi MVP để giữ xác thực đơn giản.
- **Luồng trạng thái task:** Cho phép `pending -> in_progress|cancelled`, `in_progress -> pending|completed|cancelled`, `completed -> in_progress` (mở lại), và `cancelled -> pending` (khôi phục). Cho phép mở lại/khôi phục để phản ánh công việc thay đổi ngoài thực tế; các chuyển trạng thái khác trả `422`. Gửi lại trạng thái hiện tại là thao tác idempotent.
- **Ngày và người được giao:** Ngày kết thúc dự kiến phải bằng hoặc sau ngày bắt đầu; người được giao phải là thành viên hiện tại của cùng dự án. Các ràng buộc này ngăn task có lịch bất khả thi hoặc giao cho người không có quyền truy cập; vi phạm trả `422`.
