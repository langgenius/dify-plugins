import sqlite3
import os

db_path = "packages/server/suprawall.db"

def recover_data():
    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"--- Recovering Data from {db_path} ---")

    # 1. Audit Logs
    try:
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        count = cursor.fetchone()[0]
        print(f"Total Audit Logs (Traffic): {count}")
        
        if count > 0:
            print("Latest 5 logs:")
            cursor.execute("SELECT toolname, decision, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 5")
            for row in cursor.fetchall():
                print(f"- {row[0]} | {row[1]} | {row[2]}")
    except Exception as e:
        print(f"Audit Logs Error: {e}")

    # 2. Beta Testers
    try:
        cursor.execute("SELECT COUNT(*) FROM beta_testers")
        count = cursor.fetchone()[0]
        print(f"Total Beta Testers (Signups): {count}")
        
        if count > 0:
            print("Latest 5 signups:")
            cursor.execute("SELECT email, framework, created_at FROM beta_testers ORDER BY created_at DESC LIMIT 5")
            for row in cursor.fetchall():
                print(f"- {row[0]} | {row[1]} | {row[2]}")
    except Exception as e:
        # Check if table name is different
        print(f"Beta Testers Table check: {e}")

    conn.close()

if __name__ == "__main__":
    recover_data()
