import httpx

# Initialize the root URL of the emulator API
BASE_URL = "https://jsonplaceholder.typicode.com"

# 1. GET /posts with query userId = 1 using the params parameter
print("Task 1: GET /posts with params ---")
query_params = {"userId": 1}
response_get = httpx.get(f"{BASE_URL}/posts", params=query_params)

if response_get.status_code == 200:
    posts = response_get.json()
    print(f"Number of posts: {len(posts)}")
    print(f"Status code: {response_get.status_code}")
    print(f"Content-Type: {response_get.headers['content-type']}")
else:
    print(f"Wrong: {response_get.status_code}")

# 2. POST /posts with body JSON using the parameter json
print("\n Task 2: POST /posts with json ---")
payload = {
    "title": "Học lập trình",
    "body": "Sử dụng httpx để gửi HTTP rất tiện lợi",
    "userId": 1,
}

response_post = httpx.post(f"{BASE_URL}/posts", json=payload)
print(f"Status code: {response_post.status_code}")
print("The content of the received response")
print(response_post.json())

# 3. GET /posts/9999 and handle the 404 error using code
print("\n Task 3: GET /posts/9999 and handle 404 error ---")
response_404 = httpx.get(f"{BASE_URL}/posts/9999")

if response_404.status_code == 404:
    print("Handle: Post not found(404 error handle successfully).")
elif response_404.status_code == 200:
    print(f"Post: {response_404.json()}")
else:
    print(f"Different error {response_404.status_code}")
