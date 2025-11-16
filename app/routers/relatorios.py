from fastapi import APIRouter, Depends, HTTPException
from app.db import get_conn
from app.deps import require_roles

router = APIRouter()

@router.get("/frequencia")
def relatorio_frequencia(periodo: int, id_materia: int, user=Depends(require_roles("admin", "professor"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT a.nome AS aluno,
                   SUM(CASE WHEN rf.presenca = TRUE THEN 1 ELSE 0 END) AS presencas,
                   COUNT(*) AS total_aulas,
                   ROUND(100.0 * SUM(CASE WHEN rf.presenca = TRUE THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS percentual
            FROM registro_fato rf
            JOIN aluno_dim a ON a.id_aluno = rf.id_aluno
            WHERE rf.tipo_registro = 'frequencia'
              AND rf.id_periodo = %s
              AND rf.id_materia = %s
            GROUP BY a.nome
            ORDER BY a.nome
        """, (periodo, id_materia))
        return cur.fetchall()

@router.get("/boletim/{id_aluno}")
def relatorio_boletim(id_aluno: int, periodo: int, user=Depends(require_roles("admin", "professor", "responsavel"))):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT m.nome AS materia,
                   rav.tipo_registro AS avaliacao,
                   rf.nota_decimal,
                   rf.observacao
            FROM registro_fato rf
            JOIN materia_dim m ON m.id_materia = rf.id_materia
            JOIN registro_avaliativo_dim rav ON rav.id_registro_avaliativo = rf.id_registro_avaliativo
            WHERE rf.tipo_registro = 'avaliacao'
              AND rf.id_aluno = %s
              AND rf.id_periodo = %s
            ORDER BY m.nome, rav.tipo_registro
        """, (id_aluno, periodo))
        data = cur.fetchall()
        if data is None:
            raise HTTPException(status_code=404, detail="Sem registros")
        return data
