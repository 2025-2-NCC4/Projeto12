# app/dashboards/cfo.py
from flask import jsonify, request
from flask_login import login_required
from sqlalchemy import text, bindparam
from ..extensions import db
from . import dash_bp
from ..auth.decorators import role_required


# ---- util: normalizar nome de bairro (espelha o front) ----
import re
from unidecode import unidecode
def limpar_nome_bairro(nome: str) -> str:
    if not isinstance(nome, str):
        return ""
    s = unidecode(str(nome).upper())
    if s == "HIGIENOPOLIS":
        s = "CONSOLACAO"
    s = re.sub(r'[^A-Z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

@dash_bp.get("/cfo/filters")
@login_required
@role_required("CFO")
def cfo_filters():
    row = db.session.execute(text("""
        SELECT MIN(DATE(t.data_hora_transacao)) AS min_dt,
               MAX(DATE(t.data_hora_transacao)) AS max_dt
        FROM transacao t
    """)).mappings().first() or {}
    min_dt, max_dt = row.get("min_dt"), row.get("max_dt")

    categorias = [r["categoria"] for r in db.session.execute(text("""
        SELECT DISTINCT p.categoria_parceiro AS categoria
        FROM parceiro p
        WHERE p.categoria_parceiro IS NOT NULL AND p.categoria_parceiro <> ''
        ORDER BY categoria
    """)).mappings().all()]

    bairros = [r["bairro"] for r in db.session.execute(text("""
        SELECT DISTINCT r.bairro AS bairro
        FROM regiao r
        WHERE r.bairro IS NOT NULL AND r.bairro <> ''
        ORDER BY bairro
    """)).mappings().all()]

    return jsonify({"ok": True,
                    "min_date": str(min_dt) if min_dt else None,
                    "max_date": str(max_dt) if max_dt else None,
                    "categorias": categorias,
                    "bairros": bairros})

@dash_bp.post("/cfo/data")
@login_required
@role_required("CFO")
def cfo_data():
    p = request.get_json(silent=True) or {}
    dt_from, dt_to = p.get("from"), p.get("to")
    categorias = p.get("categorias") or []
    bairros    = p.get("bairros") or []
    if not dt_from or not dt_to:
        return jsonify({"ok": False, "error": "periodo_obrigatorio"}), 400

    wheres = [
        "t.data_hora_transacao >= :dt_from",
        "t.data_hora_transacao <  DATE_ADD(:dt_to, INTERVAL 1 DAY)"
    ]
    params = {"dt_from": dt_from, "dt_to": dt_to}
    if categorias:
        wheres.append("p.categoria_parceiro IN :cats")
        params["cats"] = categorias
    if bairros:
        wheres.append("r.bairro IN :brrs")
        params["brrs"] = bairros
    where_sql = " WHERE " + " AND ".join(wheres)

    def expand(stmt):
        if "cats" in params:
            stmt = stmt.bindparams(bindparam("cats", expanding=True))
        if "brrs" in params:
            stmt = stmt.bindparams(bindparam("brrs", expanding=True))
        return stmt

    # Definição do JOIN base
    base_join = f"""
        FROM transacao t
        JOIN cupom     c   ON t.id_cupom_fk     = c.id_cupom
        JOIN parceiro  p   ON t.id_parceiros_fk = p.id_parceiros
        JOIN regiao    r   ON p.id_regiao_fk    = r.id_regiao
        JOIN campanha  camp ON c.id_campanha_fk = camp.id_campanha
        {where_sql}
    """

    # KPIs
    row = db.session.execute(expand(text(f"""
        SELECT COALESCE(SUM(t.valor_repasse), 0)    AS receita_liquida,
               COALESCE(SUM(t.valor_transacao), 0)  AS gmv,
               COUNT(t.id_transacao)                AS num_transacoes
        {base_join}
    """)), params).mappings().first() or {}
    receita_liquida = float(row.get("receita_liquida") or 0)
    gmv             = float(row.get("gmv") or 0)
    num_trans       = int(row.get("num_transacoes") or 0)
    margem_operacional = (receita_liquida / gmv * 100) if gmv > 0 else 0.0
    ticket_medio       = (gmv / num_trans) if num_trans > 0 else 0.0
    valor_medio_repasse= (receita_liquida / num_trans) if num_trans > 0 else 0.0

    # Receita diária
    receita_diaria = [
        {"data": str(r["data"]), "valor_repasse": float(r["valor"] or 0)}
        for r in db.session.execute(expand(text(f"""
            SELECT DATE(t.data_hora_transacao) AS data, SUM(t.valor_repasse) AS valor
            {base_join}
            GROUP BY DATE(t.data_hora_transacao)
            ORDER BY DATE(t.data_hora_transacao)
        """)), params).mappings().all()
    ]

    # Receita por tipo de cupom
    receita_por_cupom = [
        {"tipo_cupom": r["tipo_cupom"], "valor_repasse": float(r["valor_repasse"] or 0)}
        for r in db.session.execute(expand(text(f"""
            SELECT c.tipo_cupom, SUM(t.valor_repasse) AS valor_repasse
            {base_join}
            GROUP BY c.tipo_cupom
            ORDER BY c.tipo_cupom
        """)), params).mappings().all()
    ]

    # Por categoria (com margem e gmv)
    por_categoria = []
    for r in db.session.execute(expand(text(f"""
        SELECT p.categoria_parceiro AS categoria,
               SUM(t.valor_repasse)   AS receita_liquida,
               SUM(t.valor_transacao) AS gmv,
               COUNT(t.id_transacao)  AS num_transacoes
        {base_join}
        GROUP BY p.categoria_parceiro
        ORDER BY receita_liquida DESC
    """)), params).mappings().all():
        receita = float(r["receita_liquida"] or 0)
        gmv_cat = float(r["gmv"] or 0)
        n       = int(r["num_transacoes"] or 0)
        margem  = (receita / gmv_cat * 100) if gmv_cat > 0 else 0.0
        por_categoria.append({
            "categoria_parceiro": r["categoria"],
            "receita_liquida": receita,
            "gmv": gmv_cat,
            "num_transacoes": n,
            "margem": margem
        })

    # Top 5 Parceiros
    top_parceiros = [
        {"nome_parceiro": r["nome_parceiro"], "valor_repasse": float(r["valor_repasse"] or 0)}
        for r in db.session.execute(expand(text(f"""
            SELECT p.nome_parceiro, SUM(t.valor_repasse) AS valor_repasse
            {base_join}
            GROUP BY p.nome_parceiro
            ORDER BY valor_repasse DESC
            LIMIT 5
        """)), params).mappings().all()
    ]

    # Receita por Bairro (e estatísticas para o mapa)
    vals, por_bairro = [], []
    for r in db.session.execute(expand(text(f"""
        SELECT r.bairro, SUM(t.valor_repasse) AS valor_repasse
        {base_join}
        GROUP BY r.bairro
    """)), params).mappings().all():
        bairro = r["bairro"]
        val = float(r["valor_repasse"] or 0)
        vals.append(val)
        # O backend aplica a limpeza do nome do bairro para o 'id_limpo'
        por_bairro.append({"id_limpo": limpar_nome_bairro(bairro),
                           "bairro": bairro, "valor_repasse": val})
    stats_bairro = {"min": min(vals) if vals else 0.0,
                    "mean": (sum(vals)/len(vals)) if vals else 0.0,
                    "max": max(vals) if vals else 0.0}

    return jsonify({"ok": True,
                    "kpis": {
                        "receita_liquida": receita_liquida,
                        "gmv": gmv,
                        "num_transacoes": num_trans,
                        "margem_operacional": margem_operacional,
                        "ticket_medio": ticket_medio,
                        "valor_medio_repasse": valor_medio_repasse
                    },
                    "receita_diaria": receita_diaria,
                    "receita_por_cupom": receita_por_cupom,
                    "por_categoria": por_categoria,
                    "top_parceiros": top_parceiros,
                    "por_bairro": por_bairro,
                    "stats_bairro": stats_bairro})