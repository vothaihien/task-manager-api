# Thiết kế REST API

Tài liệu này mô tả API MVP cho Task Manager. Các mã user story tham chiếu
`docs/requirements.md`; ma trận quyền và quy tắc nghiệp vụ trong tài liệu đó là
nguồn chuẩn khi có nội dung khác mâu thuẫn.

## 1. Nguyên tắc thiết kế

- URL biểu diễn tài nguyên bằng danh từ số nhiều; HTTP method biểu diễn hành
  động. Ví dụ: `POST /projects`, không dùng `/createProject`.
- Tài nguyên con dùng đường dẫn lồng nhau, ví dụ
  `/projects/{project_id}/tasks`.
- Tất cả endpoint có tiền tố phiên bản `/api/v1`.
- Dùng `PATCH` để cập nhật một phần. Endpoint cập nhật chỉ chấp nhận các trường
  mà vai trò hiện tại được phép sửa.
- JSON dùng tên trường `snake_case`; ngày dùng định dạng ISO 8601.
- Các endpoint cần đăng nhập nhận access token qua header Authorization với
  scheme Bearer. Token có hiệu lực 60 phút.

### HTTP method

| Method   | Ý nghĩa                         | Idempotent |
| -------- | ------------------------------- | ---------- |
| `GET`    | Đọc tài nguyên                  | Có         |
| `POST`   | Tạo tài nguyên                  | Không      |
| `PATCH`  | Cập nhật một phần               | Thường có  |
| `PUT`    | Thay thế toàn bộ tài nguyên     | Có         |
| `DELETE` | Xoá hoặc vô hiệu hoá tài nguyên | Có         |

API chọn `PATCH` cho cập nhật vì quyền cập nhật có thể giới hạn theo từng
trường. Không dùng `PUT` trong các luồng MVP.

## 2. Danh sách endpoint

`{project_id}`, `{task_id}` và `{user_id}` là định danh của tài nguyên. Các
endpoint trừ health check, đăng ký và đăng nhập yêu cầu access token hợp lệ.

### Health check

| Method | Đường dẫn        | Thành công |
| ------ | ---------------- | ---------: |
| `GET`  | `/api/v1/health` |   `200 OK` |

Health check không yêu cầu đăng nhập và trả trạng thái hoạt động của ứng dụng:

```json
{
  "status": "ok"
}
```

### Xác thực và hồ sơ

| Method | Đường dẫn               | Story |    Thành công |
| ------ | ----------------------- | ----- | ------------: |
| `POST` | `/api/v1/auth/register` | US-01 | `201 Created` |
| `POST` | `/api/v1/auth/login`    | US-02 |      `200 OK` |
| `GET`  | `/api/v1/users/me`      | US-12 |      `200 OK` |

### Dự án

| Method   | Đường dẫn                       | Story |       Thành công |
| -------- | ------------------------------- | ----- | ---------------: |
| `POST`   | `/api/v1/projects`              | US-03 |    `201 Created` |
| `GET`    | `/api/v1/projects`              | US-04 |         `200 OK` |
| `GET`    | `/api/v1/projects/{project_id}` | US-04 |         `200 OK` |
| `PATCH`  | `/api/v1/projects/{project_id}` | US-05 |         `200 OK` |
| `DELETE` | `/api/v1/projects/{project_id}` | US-06 | `204 No Content` |

Danh sách dự án chỉ gồm dự án đang hoạt động mà người dùng hiện tại là thành
viên.

### Thành viên dự án

| Method   | Đường dẫn                                         | Story |       Thành công |
| -------- | ------------------------------------------------- | ----- | ---------------: |
| `GET`    | `/api/v1/projects/{project_id}/members`           | US-07 |         `200 OK` |
| `POST`   | `/api/v1/projects/{project_id}/members`           | US-07 |    `201 Created` |
| `PATCH`  | `/api/v1/projects/{project_id}/members/{user_id}` | US-07 |         `200 OK` |
| `DELETE` | `/api/v1/projects/{project_id}/members/{user_id}` | US-07 | `204 No Content` |

`POST` thêm thành viên bằng `email` của tài khoản đã đăng ký; không nhận
`user_id` trong body. Thiếu `email` hoặc request sai định dạng trả
`400 Bad Request`. MVP chấp nhận rủi ro dò email đã đăng ký qua kết quả thêm
thành viên; cần xem xét giảm thiểu rủi ro này trước khi mở API rộng rãi.
Owner có thể gán vai trò `manager` hoặc `member`; Manager chỉ có thể thêm
Member. `PATCH` vai trò chỉ dành cho Owner và không được phép gán `owner` trong
MVP; người tạo dự án giữ vai trò `owner` trong `project_members` trong suốt
vòng đời dự án. Xoá thành viên thu hồi quyền truy cập ngay.

`created_by_id` trong `projects` là người tạo ban đầu và bất biến; vai trò hiện
tại của người đó được lấy từ dòng `project_members` đang hoạt động. Điều này
cho phép lưu lịch sử người tạo mà vẫn hỗ trợ quyền và ràng buộc `owner` hiện
hành.

### Công việc (task)

| Method   | Đường dẫn                                       | Story |       Thành công |
| -------- | ----------------------------------------------- | ----- | ---------------: |
| `POST`   | `/api/v1/projects/{project_id}/tasks`           | US-08 |    `201 Created` |
| `GET`    | `/api/v1/projects/{project_id}/tasks`           | US-09 |         `200 OK` |
| `GET`    | `/api/v1/projects/{project_id}/tasks/{task_id}` | US-09 |         `200 OK` |
| `PATCH`  | `/api/v1/projects/{project_id}/tasks/{task_id}` | US-10 |         `200 OK` |
| `DELETE` | `/api/v1/projects/{project_id}/tasks/{task_id}` | US-11 | `204 No Content` |

Task chỉ được truy cập qua dự án chứa task đó. Nếu `task_id` không thuộc
`project_id` trên URL, API trả `404 Not Found`.

## 3. Quy ước request và response

### Tạo tài khoản và đăng nhập

Request đăng ký:

```json
{
  "email": "member@example.com",
  "password": "minimum-8-chars"
}
```

Response đăng ký `201 Created`:

```json
{
  "id": "8e03978e-40d5-43e8-bc93-6894a57f9324",
  "email": "member@example.com",
  "created_at": "2026-10-07T08:30:00Z"
}
```

Response đăng ký `201 Created` trả thông tin tài khoản, không bao giờ trả mật
khẩu hoặc password hash. Đăng nhập nhận cùng hai trường và trả access token có
thời hạn 60 phút. Email hoặc mật khẩu không đúng trả cùng một lỗi `401` để
không tiết lộ email có tồn tại hay không.

### Tạo và cập nhật tài nguyên

- `POST` nhận các trường cần thiết để tạo tài nguyên và trả tài nguyên vừa tạo.
- `PATCH` chỉ nhận các trường cần cập nhật và trả tài nguyên sau cập nhật.
- Không được gửi trường ngoài quyền của vai trò hiện tại; trường không được
  phép sửa bị từ chối, không bị âm thầm bỏ qua.
- Với task, Owner/Manager có thể cập nhật thông tin được phép, bao gồm người
  được giao, mức ưu tiên và ngày dự kiến. Member chỉ có thể cập nhật `description`
  và `status` của task được giao cho mình.
- Khi thành viên rời dự án, task không tự động bị bỏ giao. Dữ liệu lịch sử giữ
  `assigned_to_user_id` để không mất trace; API trả task có thể để `assigned_to_user`
  bằng `null` hoặc không cấp dữ liệu do người này không còn là thành viên của dự án.
- `DELETE` thành công trả `204 No Content`, không kèm JSON response. Xoá dự án
  và task là soft delete; thành viên bị xoá mất quyền truy cập ngay.
- `projects` có trường `name` bắt buộc và `description` tùy chọn để đáp ứng US-03.
  `POST /projects` chấp nhận `description` và `PATCH /projects/{project_id}` cho phép
  cập nhật `name` và `description` trong phạm vi quyền.

Các trường cụ thể của tài nguyên tuân theo yêu cầu nghiệp vụ: project có tên và
mô tả tùy chọn; task có tên, mô tả, trạng thái, mức ưu tiên, ngày bắt đầu, ngày
kết thúc dự kiến và người được giao. Tên trường và enum phải nhất quán giữa
request, response và tài liệu schema của ứng dụng.

Ví dụ tạo task bằng `POST /api/v1/projects/{project_id}/tasks`:

```json
{
  "name": "Chuẩn bị bản phát hành",
  "description": "Hoàn tất kiểm thử hồi quy",
  "status": "pending",
  "priority": "high",
  "start_date": "2026-10-08",
  "due_date": "2026-10-15",
  "assigned_to_user_id": "2b3a1c4d-5e6f-4789-8abc-1234567890ab"
}
```

Response `201 Created`:

```json
{
  "id": "6d3a71bc-9472-4a30-a340-dbc54ac8b38a",
  "project_id": "6f5f0d86-44f9-42eb-a2f5-7e0f06eb5678",
  "name": "Chuẩn bị bản phát hành",
  "description": "Hoàn tất kiểm thử hồi quy",
  "status": "pending",
  "priority": "high",
  "start_date": "2026-10-08",
  "due_date": "2026-10-15",
  "assigned_to_user_id": "2b3a1c4d-5e6f-4789-8abc-1234567890ab",
  "created_at": "2026-10-07T08:30:00Z",
  "updated_at": "2026-10-07T08:30:00Z"
}
```

`status` nhận một trong `pending`, `in_progress`, `completed`, `cancelled`;
`priority` nhận một trong `low`, `medium`, `high`. Khi không gửi các trường
này, lần lượt dùng mặc định `pending` và `medium`. `assigned_to_user_id` có
thể là `null` nếu task chưa được giao; người được giao phải là thành viên đang
hoạt động của dự án.

### Phân trang và lọc

Mọi endpoint danh sách hỗ trợ query `page` và `page_size`, mặc định lần lượt là
`1` và `20`. `page` bắt đầu từ `1`; giá trị không hợp lệ trả `422`.
Mọi danh sách mặc định sắp xếp `created_at` giảm dần, sau đó `id` giảm dần để
thứ tự ổn định giữa các trang.

Danh sách dự án, thành viên và task trả cùng cấu trúc:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0,
  "total_pages": 0
}
```

`total` là số bản ghi khớp bộ lọc trước khi phân trang. `total_pages` bằng
`ceil(total / page_size)`; bằng `0` khi không có bản ghi. Danh sách task hỗ trợ
lọc bằng `status` và `priority`; giá trị lọc không hợp lệ trả `422`. Bộ lọc và
phân trang có thể dùng đồng thời, ví dụ:
`GET /api/v1/projects/42/tasks?page=1&page_size=20&status=in_progress`.

## 4. Quy ước lỗi

Tất cả lỗi API dùng cùng cấu trúc JSON:

```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "Email đã được sử dụng"
  }
}
```

`code` là mã ổn định để client xử lý; `message` là mô tả dễ đọc. Không trả
stack trace, password hash hoặc thông tin nhạy cảm khác cho client.

|                HTTP status | Khi sử dụng                                                          | Ví dụ mã lỗi                                     |
| -------------------------: | -------------------------------------------------------------------- | ------------------------------------------------ |
|          `400 Bad Request` | JSON sai định dạng hoặc thiếu trường bắt buộc                        | `INVALID_REQUEST`                                |
|         `401 Unauthorized` | Thiếu token, token không hợp lệ/hết hạn hoặc thông tin đăng nhập sai | `UNAUTHENTICATED`, `INVALID_CREDENTIALS`         |
|            `403 Forbidden` | Đã xác thực và là thành viên nhưng vai trò không đủ quyền            | `FORBIDDEN`                                      |
|            `404 Not Found` | Tài nguyên không tồn tại hoặc người gọi không thuộc dự án            | `NOT_FOUND`                                      |
|             `409 Conflict` | Xung đột với tài nguyên hiện có                                      | `EMAIL_ALREADY_EXISTS`, `ALREADY_PROJECT_MEMBER` |
| `422 Unprocessable Entity` | Request đúng định dạng nhưng vi phạm quy tắc nghiệp vụ               | `VALIDATION_ERROR`                               |

Người không thuộc dự án nhận `404` cho tài nguyên dự án/task để không tiết lộ
sự tồn tại của tài nguyên. Thành viên đã xác thực nhưng thiếu quyền nhận `403`.

## 5. Quy tắc nghiệp vụ áp dụng cho API

- Người tạo dự án trở thành Owner của dự án.
- Chỉ thành viên của dự án được xem dự án, thành viên và task thuộc dự án đó.
- Chỉ Owner/Manager được tạo hoặc xoá task. Member chỉ được xem task và cập
  nhật mô tả/trạng thái của task giao cho mình.
- Người được giao task phải là thành viên hiện tại của chính dự án đó.
- Ngày kết thúc dự kiến phải bằng hoặc sau ngày bắt đầu.
- Chuyển trạng thái task chỉ hợp lệ theo luồng:
  `pending -> in_progress|cancelled`,
  `in_progress -> pending|completed|cancelled`,
  `completed -> in_progress`,
  `cancelled -> pending`. Gửi lại trạng thái hiện tại được xem là idempotent.
- Giá trị hợp lệ nhưng vi phạm các quy tắc nghiệp vụ trên trả `422`; thiếu
  quyền trả `403`; người ngoài dự án trả `404`.
