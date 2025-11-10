from flask import request, jsonify
from flask_login import login_required
from sqlalchemy import text
from ..extensions import db
from . import dash_bp
from ..auth.decorators import role_required

@dash_bp.get("/ceo/players/cidades")
@login_required
@role_required("CEO")
def ceo_listar_cidades():
    """
    Retorna a lista de cidades disponíveis (para preencher o multiselect do front).
    """
    sql = text("SELECT DISTINCT cidade FROM player WHERE cidade IS NOT NULL AND cidade <> '' ORDER BY cidade;")
    rows = db.session.execute(sql).mappings().all()
    cidades = [r["cidade"] for r in rows]
    return jsonify({"ok": True, "cidades": cidades})

@dash_bp.get("/ceo/players/hist_idade")
@login_required
@role_required("CEO")
def ceo_hist_idade():
    """
    Calcula no BACKEND o histograma de idades, opcionalmente filtrando por cidades.
    Ex.: /api/ceo/players/hist_idade?cidades=São%20Paulo,Santos
    Retorna pares (idade, quantidade).
    """
    cidades_param = (request.args.get("cidades") or "").strip()
    cidades = [c.strip() for c in cidades_param.split(",") if c.strip()]

    if cidades:
        placeholders = ", ".join([f":c{i}" for i in range(len(cidades))])
        sql = text(f"""
            SELECT idade, COUNT(*) AS quantidade
            FROM player
            WHERE idade IS NOT NULL
              AND cidade IN ({placeholders})
            GROUP BY idade
            ORDER BY idade
        """)
        params = {f"c{i}": c for i, c in enumerate(cidades)}
        rows = db.session.execute(sql, params).mappings().all()
    else:
        sql = text("""
            SELECT idade, COUNT(*) AS quantidade
            FROM player
            WHERE idade IS NOT NULL
            GROUP BY idade
            ORDER BY idade
        """)
        rows = db.session.execute(sql).mappings().all()

    hist = [{"idade": r["idade"], "quantidade": r["quantidade"]} for r in rows]
    return jsonify({"ok": True, "histograma": hist})

