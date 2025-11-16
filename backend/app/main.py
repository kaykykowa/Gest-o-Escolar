import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Gestão Escolar - Full Stack")

# 🔓 CORS liberado para qualquer origem (apenas DEV)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # aceita file://, http://127.0.0.1, etc.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⬇️ Rotas da API
from app.routers import auth, dimensoes, registros, relatorios
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(dimensoes.router, prefix="/dim", tags=["dimensoes"])
app.include_router(registros.router, prefix="/registros", tags=["registros"])
app.include_router(relatorios.router, prefix="/relatorios", tags=["relatorios"])

@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8000")),
        reload=True
    )
