import sqlite3

DB_NAME = "voting_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            has_voted INTEGER DEFAULT 0,
            voted_for INTEGER,
            custom_name TEXT,
            custom_name_status TEXT DEFAULT 'none'
        );
    """)

    # 2. Candidates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            vote_count INTEGER DEFAULT 0
        );
    """)

    # Seed Default Admin & Sample Students if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        # Admin Account (username: admin, pass: admin123)
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');")
        # Sample Student Accounts (pass: pass123)
        sample_students = [('101', 'pass123'), ('102', 'pass123'), ('103', 'pass123'), ('104', 'pass123')]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, 'student');", sample_students)

    # Seed Default Candidates if empty
    cursor.execute("SELECT COUNT(*) FROM candidates;")
    if cursor.fetchone()[0] == 0:
        sample_candidates = [('Alex Smith', 0), ('Sarah Johnson', 0), ('Michael Brown', 0)]
        cursor.executemany("INSERT INTO candidates (name, vote_count) VALUES (?, ?);", sample_candidates)

    conn.commit()
    conn.close()

# Helper Query Functions
def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_candidates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY vote_count DESC;")
    candidates = cursor.fetchall()
    conn.close()
    return candidates

def cast_vote(user_id, candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?;", (candidate_id,))
    cursor.execute("UPDATE users SET has_voted = 1, voted_for = ? WHERE id = ?;", (candidate_id, user_id))
    conn.commit()
    conn.close()

def submit_custom_name(user_id, custom_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET custom_name = ?, custom_name_status = 'pending' 
        WHERE id = ?;
    """, (custom_name.strip(), user_id))
    conn.commit()
    conn.close()

def get_pending_custom_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, custom_name FROM users WHERE custom_name_status = 'pending';")
    pending = cursor.fetchall()
    conn.close()
    return pending

def approve_custom_name(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch custom name
    cursor.execute("SELECT custom_name FROM users WHERE id = ?;", (user_id,))
    row = cursor.fetchone()
    if row and row['custom_name']:
        c_name = row['custom_name'].strip()
        
        # Check if candidate exists
        cursor.execute("SELECT id FROM candidates WHERE name = ?;", (c_name,))
        cand = cursor.fetchone()
        if cand:
            cursor.execute("UPDATE candidates SET vote_count = vote_count + 1 WHERE id = ?;", (cand['id'],))
        else:
            cursor.execute("INSERT INTO candidates (name, vote_count) VALUES (?, 1);", (c_name,))
            
        cursor.execute("UPDATE users SET custom_name_status = 'approved', has_voted = 1 WHERE id = ?;", (user_id,))
        conn.commit()
    conn.close()

def reject_custom_name(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET custom_name_status = 'rejected' WHERE id = ?;", (user_id,))
    conn.commit()
    conn.close()

def change_user_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?;", (new_password, user_id))
    conn.commit()
    conn.close()
