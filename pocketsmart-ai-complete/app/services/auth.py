import base64, hashlib, hmac, json, os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.db import User

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))

def hash_password(password: str) -> str:
    salt=os.urandom(16); iterations=210_000
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,iterations)
    return f"pbkdf2_sha256${iterations}${_b64(salt)}${_b64(digest)}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme,iters,salt,digest=encoded.split("$",3)
        if scheme!="pbkdf2_sha256": return False
        candidate=hashlib.pbkdf2_hmac("sha256",password.encode(),_unb64(salt),int(iters))
        return hmac.compare_digest(candidate,_unb64(digest))
    except Exception:
        return False

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user=db.query(User).filter(User.email==email.lower().strip()).first()
    return user if user and verify_password(password,user.password_hash) else None

def create_access_token(user_id: int, minutes: int=60*24) -> str:
    header={"alg":"HS256","typ":"JWT"}
    payload={"sub":str(user_id),"exp":int((datetime.now(timezone.utc)+timedelta(minutes=minutes)).timestamp())}
    h=_b64(json.dumps(header,separators=(",",":")).encode()); p=_b64(json.dumps(payload,separators=(",",":")).encode())
    sig=_b64(hmac.new(get_settings().secret_key.encode(),f"{h}.{p}".encode(),hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"

def decode_access_token(token: str) -> int | None:
    try:
        h,p,s=token.split(".")
        expected=_b64(hmac.new(get_settings().secret_key.encode(),f"{h}.{p}".encode(),hashlib.sha256).digest())
        if not hmac.compare_digest(expected,s): return None
        payload=json.loads(_unb64(p))
        if int(payload.get("exp",0)) < int(datetime.now(timezone.utc).timestamp()): return None
        return int(payload["sub"])
    except Exception:
        return None
