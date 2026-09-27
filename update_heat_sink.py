import sqlite3

conn = sqlite3.connect("sovereign_odyssey.db")
cur = conn.cursor()
cur.execute("""
    INSERT INTO ash_strata (timestamp, layer_id, logic_state, event_payload, parent_hash, lineage_hash)
    VALUES (strftime('%s','now'), 5, 'B', 'THERMODYNAMICS: DialetheicHeatSink active at 1.5 Hz harmonic dissipation threshold.', (SELECT lineage_hash FROM ash_strata ORDER BY id DESC LIMIT 1), 'hks_sync_01');
""")
conn.commit()
print("[✓] DialetheicHeatSink synchronization node committed under Lex I.")
conn.close()
