from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.database import get_conn
from app.security import hash_password, verify_password, create_token

router = APIRouter()

class RegisterIn(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    papel: str  # "ADMIN", "PROFESSOR", "ALUNO", etc.

class LoginIn(BaseModel):
    email: EmailStr
    senha: str

@router.post("/register")
def register(body: RegisterIn):
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (body.email,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="E-mail já cadastrado")

                cur.execute(
                    """
                    INSERT INTO users (nome, email, senha_hash, papel)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, nome, email, papel
                    """,
                    (
                        body.nome,
                        body.email,
                        hash_password(body.senha),  # aqui vai salvar "1234" direto
                        body.papel,
                    ),
                )
                user = cur.fetchone()

        return {"message": "Usuário criado com sucesso", "user": user}
    finally:
        conn.close()


@router.post("/login")
def login(body: LoginIn):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash, papel FROM users WHERE email = %s",
                (body.email,),
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        if not verify_password(body.senha, row["senha_hash"]):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = create_token(
            {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "papel": row["papel"],
            }
        )

        return {"access_token": token, "token_type": "bearer"}
    finally:
        conn.close()
