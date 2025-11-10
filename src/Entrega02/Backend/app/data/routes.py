from . import data_bp
from flask import request, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db


ALLOWED_TABLES = {"transacao", "player", "parceiro", "cupom", "campanha", "regiao"}
ALLOWED_PREFIXES = ("SELECT", "WITH")  
MAX_LIMIT = 10000000 

def _is_safe_sql(sql: str) -> bool:
    s = " ".join(sql.strip().split()).upper()
    if not s.startswith(ALLOWED_PREFIXES):
        return False
    
    forbidden = ["UPDATE ", "DELETE ", "INSERT ", "DROP ", "ALTER ", "CREATE ", "TRUNCATE ", ";--", "-- ", "/*", "*/"]
    if any(tok in s for tok in forbidden):
        return False
    
    lowered = sql.lower()
    for word in [" from ", " join "]:
        parts = lowered.split(word)
        if len(parts) > 1:
            for seg in parts[1:]:
                table = seg.strip().split()[0].replace("`", "").replace('"', "")
                table = table.split(".")[-1]
                table = table.replace("(", "")
                if table and table not in ALLOWED_TABLES:
                    return False
    return True

@data_bp.post("/query")
def run_query():
    payload = request.get_json(silent=True) or {}
    sql = (payload.get("sql") or "").strip()
    if not sql:
        return jsonify({"ok": False, "error": "sql_vazio"}), 400
    if not _is_safe_sql(sql):
        return jsonify({"ok": False, "error": "sql_nao_permitido"}), 400

    # Impõe LIMIT padrão se não houver
    low = sql.lower()
    if " limit " not in low and " count(" not in low:
        sql = f"{sql}\nLIMIT {MAX_LIMIT}"

    try:
        result = db.session.execute(text(sql))
        rows = [dict(r._mapping) for r in result]
        return jsonify({"ok": True, "rows": rows})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": "sqlalchemy_error", "detail": str(e)}), 400
