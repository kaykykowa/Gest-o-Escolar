from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.db import get_conn
from app.deps import require_roles

router = APIRouter()

class AlunoIn(BaseModel):
    nome: str
    data_nascimento: Optional[str] = None  # YYYY-MM-DD
    sexo: Optional[str] = None            # 'M' | 'F'
    nome_pai: Optional[str] = None
    nome_mae: Optional[str] = None

@router.post("/alunos")
def criar_aluno(body: AlunoIn, user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO aluno_dim (nome, data_nascimento, sexo, nome_pai, nome_mae)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id_aluno, nome
        """, (body.nome, body.data_nascimento, body.sexo, body.nome_pai, body.nome_mae))
        return cur.fetchone()

@router.get("/alunos")
def listar_alunos(user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id_aluno, nome, data_nascimento, sexo, nome_pai, nome_mae FROM aluno_dim ORDER BY id_aluno")
        return cur.fetchall()

class ProfessorIn(BaseModel):
    nome: str
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    formacao: Optional[str] = None

@router.post("/professores")
def criar_professor(body: ProfessorIn, user=Depends(require_roles("admin"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO professor_dim (nome, data_nascimento, sexo, formacao)
            VALUES (%s,%s,%s,%s)
            RETURNING id_professor, nome
        """, (body.nome, body.data_nascimento, body.sexo, body.formacao))
        return cur.fetchone()

class MateriaIn(BaseModel):
    nome: str

@router.post("/materias")
def criar_materia(body: MateriaIn, user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO materia_dim (nome) VALUES (%s) RETURNING id_materia, nome", (body.nome,))
        return cur.fetchone()

class PeriodoIn(BaseModel):
    ano: str
    ciclo: str
    semestre: Optional[str] = None

@router.post("/periodos")
def criar_periodo(body: PeriodoIn, user=Depends(require_roles("admin"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO periodo_letivo_dim (ano, ciclo, semestre)
            VALUES (%s,%s,%s)
            RETURNING id_periodo, ano, ciclo, semestre
        """, (body.ano, body.ciclo, body.semestre))
        return cur.fetchone()

class TipoAvaliativoIn(BaseModel):
    tipo_registro: str

@router.post("/tipos-avaliativos")
def criar_tipo_avaliativo(body: TipoAvaliativoIn, user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO registro_avaliativo_dim (tipo_registro)
            VALUES (%s)
            RETURNING id_registro_avaliativo, tipo_registro
        """, (body.tipo_registro,))
        return cur.fetchone()

class DataCalendarioIn(BaseModel):
    data: str
    dia: int
    mes: int
    ano: int
    bimestre: Optional[int] = None
    semestre: Optional[int] = None

@router.post("/datas")
def criar_data(body: DataCalendarioIn, user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO calendario_dim_1 (data, dia, mes, ano, bimestre, semestre)
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING data
        """, (body.data, body.dia, body.mes, body.ano, body.bimestre, body.semestre))
        return cur.fetchone()
