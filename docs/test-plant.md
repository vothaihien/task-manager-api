### Đăng ký hợp lệ
    - 201 Created
### Đăng ký lại email vừa đăng ký(viết khác chữ thường/hoa).
    - 409 EMAIL_ALREADY_EXISTS
### Với mật khẩu 7 ký tự.
    - 422
### Với Email sai định dạng.
    - Input: user.test4#gmail.com.
    - 422 msg "value is not a valid email address: An email address must have an @-sign."

### Đăng nhập đúng mật khẩu
Code	Details
200	
Response body
Download
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMzRjZDlkZS03NDA3LTQ0MDQtYWM3Mi1lM2ZiYmY0N2RlOTEiLCJleHAiOjE3OTI5MjU3NjR9.PtWiVNuwquHOBMVEeZ4FrZcgcwNZO9cexYuzrqiwbk0",
  "token_type": "bearer",
  "expires_in": 3600
}
Response headers
 content-length: 224 
 content-type: application/json 
 date: Sun,25 Oct 2026 09:53:54 GMT 
 server: uvicorn s
### Đăng nhập sai mật khẩu
Code	Details
401
Undocumented
Error: Unauthorized

Response body
Download
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid credentials"
  }
}
Response headers
 content-length: 72 
 content-type: application/json 
 date: Sun,25 Oct 2026 09:59:45 GMT 
 server: uvicorn 
### Đăng nhập với email không tồn tại
Code	Details
401
Undocumented
Error: Unauthorized

Response body
Download
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid credentials"
  }
}
Response headers
 content-length: 72 
 content-type: application/json 
 date: Sun,25 Oct 2026 10:00:47 GMT 
 server: uvicorn
### Route user/me với token hợp lệ
Code	Details
200	
Response body
Download
{
  "id": "034cd9de-7407-4404-ac72-e3fbbf47de91",
  "email": "user.test1@example.com",
  "full_name": "Nguyễn Văn A",
  "created_at": "2026-10-20T15:56:57.698712Z"
}
Response headers
 content-length: 151 
 content-type: application/json 
 date: Mon,26 Oct 2026 14:50:08 GMT 
 server: uvicorn
### Route user/me với không vó token
401
Undocumented
Error: Unauthorized

Response body
Download
{
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "Invalid or expired token"
  }
}
Response headers
 content-length: 73 
 content-type: application/json 
 date: Sun,25 Oct 2026 16:17:26 GMT 
 server: uvicorn
### Route user/me với token bị sửa 1 ký tự
Code	Details
401
Undocumented
Error: Unauthorized

Response body
Download
{
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "Invalid or expired token"
  }
}
Response headers
 content-length: 73 
 content-type: application/json 
 date: Mon,26 Oct 2026 14:51:24 GMT 
 server: uvicorn
### Route user/me với token hết hạn

Code	Details
401
Undocumented
Error: Unauthorized

Response body
Download
{
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "Invalid or expired token"
  }
}
Response headers
 content-length: 73 
 content-type: application/json 
 date: Mon,26 Oct 2026 15:15:15 GMT 
 server: uvicorn
### Kiểm tra mật khẩu có được hash không.
"034cd9de-7407-4404-ac72-e3fbbf47de91"	"user.test1@example.com"	"$argon2id$v=19$m=65536,t=3,p=4$l4Qsljh/w+p6Y9q/9nchjQ$vC/I8sAAd+SszIQPhFtxqOVhH9JApPW/4rkB9yfporE"	"2026-10-20 15:56:57.698712+00"	"2026-10-20 15:56:57.698712+00"		"Nguyễn Văn A"
