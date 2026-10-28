import sys

from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jwt
from app.config import settings

if len(sys.argv) < 2:
    print("Run: py .\\scripts\\make_expired_token.py <user_id>")
    sys.exit(1)
user_id = sys.argv[1]
payload = {"sub": user_id, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
print(jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm))
