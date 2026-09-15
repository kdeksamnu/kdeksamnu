import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "leaky.db"

def hash_password(plaintext_password: str) -> str:
    return generate_password_hash(plaintext_password)

def verify_password(stored_hash: str, candidate_password: str) -> bool:
    return check_password_hash(stored_hash, candidate_password)

def main() -> None:
    username = "hashed_tester"
    plaintext = "testpassword123"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        );
    """)

    hashed = hash_password(plaintext)
    print(f"[1] New hash for '{plaintext}':\n{hashed}\n")

    cursor.execute(
        "INSERT OR REPLACE INTO users (username, password_hash) VALUES (?, ?);",
        (username, hashed),
    )
    conn.commit()
    print(f"[2] Stored hash for user '{username}' in DB.\n")

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?;",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise RuntimeError(f"No row found for user '{username}'")

    stored_hash_from_db = row[0]
    print(f"[3] Loaded hash from DB:\n{stored_hash_from_db}\n")

    ok = verify_password(stored_hash_from_db, plaintext)
    bad = verify_password(stored_hash_from_db, "wrong-password")

    print(f"[4] Verify correct password ('{plaintext}'): {ok}")
    print(f"[5] Verify wrong password ('wrong-password'): {bad}")

if __name__ == "__main__":
    main()
