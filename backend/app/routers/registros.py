from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_conn
from app.deps import require_roles

router = APIRouter()

class FrequenciaItem(BaseModel):
    id_aluno: int
    id_professor: int
    id_materia: int
    id_periodo: int
    id_data: str           # chave de calendario_dim_1 (DATA)
    presenca: bool
    observacao: Optional[str] = None
    criticidade: Optional[int] = None

class LoteFrequencia(BaseModel):
    registros: List[FrequenciaItem]

@router.post("/frequencia")
def registrar_frequencia(body: LoteFrequencia, user=Depends(require_roles("admin", "professor"))):
    if not body.registros:
        raise HTTPException(status_code=400, detail="Lote vazio")
    with get_conn() as conn, conn.cursor() as cur:
        ids = []
        try:
            for r in body.registros:
                cur.execute("""
                    INSERT INTO registro_fato
                    (id_aluno, id_professor, id_materia, id_periodo, id_data, tipo_registro, presenca, observacao, criticidade)
                    VALUES (%s,%s,%s,%s,%s,'frequencia',%s,%s,%s)
                    RETURNING id_registro
                """, (r.id_aluno, r.id_professor, r.id_materia, r.id_periodo, r.id_data, r.presenca, r.observacao, r.criticidade))
                ids.append(cur.fetchone()["id_registro"])
            return {"ids": ids}
        except Exception as e:
            conn.rollback()
            raise

class NotaItem(BaseModel):
    id_aluno: int
    id_professor: int
    id_materia: int
    id_periodo: int
    id_data: str
    id_registro_avaliativo: int
    nota_decimal: float
    observacao: Optional[str] = None

class LoteNotas(BaseModel):
    registros: List[NotaItem]

@router.post("/notas")
def registrar_notas(body: LoteNotas, user=Depends(require_roles("admin", "professor"))):
    if not body.registros:
        raise HTTPException(status_code=400, detail="Lote vazio")
    with get_conn() as conn, conn.cursor() as cur:
        ids = []
        try:
            for r in body.registros:
                cur.execute("""
                    INSERT INTO registro_fato
                    (id_aluno, id_professor, id_materia, id_periodo, id_data, id_registro_avaliativo, tipo_registro, nota_decimal, observacao)
                    VALUES (%s,%s,%s,%s,%s,%s,'avaliacao',%s,%s)
                    RETURNING id_registro
                """, (r.id_aluno, r.id_professor, r.id_materia, r.id_periodo, r.id_data, r.id_registro_avaliativo, r.nota_decimal, r.observacao))
                ids.append(cur.fetchone()["id_registro"])
            return {"ids": ids}
        except Exception:
            conn.rollback()
            raise

class ObsItem(BaseModel):
    id_aluno: int
    id_professor: int
    id_materia: int
    id_periodo: int
    id_data: str
    observacao: str
    criticidade: Optional[int] = None

class LoteObs(BaseModel):
    registros: List[ObsItem]

@router.post("/observacoes")
def registrar_observacoes(body: LoteObs, user=Depends(require_roles("admin", "professor"))):
    if not body.registros:
        raise HTTPException(status_code=400, detail="Lote vazio")
    with get_conn() as conn, conn.cursor() as cur:
        ids = []
        try:
            for r in body.registros:
                cur.execute("""
                    INSERT INTO registro_fato
                    (id_aluno, id_professor, id_materia, id_periodo, id_data, tipo_registro, observacao, criticidade)
                    VALUES (%s,%s,%s,%s,%s,'observacao',%s,%s)
                    RETURNING id_registro
                """, (r.id_aluno, r.id_professor, r.id_materia, r.id_periodo, r.id_data, r.observacao, r.criticidade))
                ids.append(cur.fetchone()["id_registro"])
            return {"ids": ids}
        except Exception:
            conn.rollback()
            raise
