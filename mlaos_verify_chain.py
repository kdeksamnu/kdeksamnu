import sqlite3

conn = sqlite3.connect("ash_archive.db")
cur = conn.cursor()

# Detect table layout
cur.execute("PRAGMA table_info(ash_archive);")
cols = [c[1] for c in cur.fetchall()]
order_col = "id" if "id" in cols else ("stratum_id" if "stratum_id" in cols else "rowid")
hash_col = "lineage_hash" if "lineage_hash" in cols else "hash"
parent_col = "parent_hash" if "parent_hash" in cols else "prev_hash"

query = f"""
    SELECT {order_col}, timestamp, layer_id, logic_state, {parent_col}, {hash_col}
    FROM ash_archive
    ORDER BY {order_col} DESC
    LIMIT 3;
"""

print(f"{'INDEX':<8} | {'LAYER':<6} | {'STATE':<6} | {'PARENT HASH (PREFIX)':<22} | {'LINEAGE HASH (PREFIX)':<22}")
print("-" * 75)
for row in cur.execute(query):
    idx, ts, layer, state, parent, lineage = row
    p_pref = (parent[:18] + "...") if parent else "NONE"
    l_pref = (lineage[:18] + "...") if lineage else "NONE"
    print(f"{str(idx):<8} | {str(layer):<6} | {str(state):<6} | {p_pref:<22} | {l_pref:<22}")

