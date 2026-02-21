import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'studybuddy.db')
    if not os.path.exists(db_path):
        # Try relative path if instance/ in current dir
        db_path = 'instance/studybuddy.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding 'completed' column to 'timetable' table...")
        cursor.execute("ALTER TABLE timetable ADD COLUMN completed BOOLEAN DEFAULT 0")
        conn.commit()
        print("Success!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'completed' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
