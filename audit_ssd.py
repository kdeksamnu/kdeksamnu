import sqlite3

conn = sqlite3.connect("sovereign_odyssey.db")
cur = conn.cursor()
print("Journal Mode:", cur.execute("PRAGMA journal_mode;").fetchone()[0])
print("Synchronous Setting:", cur.execute("PRAGMA synchronous;").fetchone()[0])
print("Page Size:", cur.execute("PRAGMA page_size;").fetchone()[0])
print("Lex I Trigger Status:", cur.execute("SELECT name FROM sqlite_master WHERE type='trigger';").fetchall())
conn.close()
