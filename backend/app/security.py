import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

# ====================================================
#   SENHA EM TEXTO PURO (APENAS PARA AMBIENTE DE TESTE)
#   NÃO USAR EM PRODUÇÃO
# ====================================================

def hash_password(plain: str) -> str:
   
    return plain

def verify_password(plain: str, stored: str) -> bool:
    # Compara diretamente a senha digitada com o valor salvo no banco
    return plain == stored

# ================= JWT ======================

JWT_SECRET = os.getenv("JWT_SECRET", "dev")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "120"))
ALGORITHM = "HS256"

security = HTTPBearer()

def create_token(payload: dict) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(tz=timezone.utc) + timedelta(minutes=JWT_EXPIRES_MIN)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def get_current_user(creds: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    token = creds.credentials
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return data
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

def require_roles(*roles):
    def wrapper(user=Depends(get_current_user)):
        papel: Optional[str] = user.get("papel")
        if roles and papel not in roles:
            raise HTTPException(status_code=403, detail="Permissão negada")
        return user
    return wrapper
