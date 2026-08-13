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

    # --- 3. WHERE TO CHANGE ADMIN DETAILS ---
    # Change 'admin' and 'admin123' below to your preferred username and password.
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin';")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');")

    # --- 4. DEFAULT STUDENTS LIST ---
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='student';")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('230030101001', 'pass123'), ('230030101003', 'pass123'), ('230030101004', 'pass123'),
            ('230030101005', 'pass123'), ('230030101006', 'pass123'), ('230030101007', 'pass123'),
            ('230030101008', 'pass123'), ('230030101009', 'pass123'), ('230030101010', 'pass123'),
            ('230030101011', 'pass123'), ('230030101012', 'pass123'), ('230030101013', 'pass123'),
            ('230030101014', 'pass123'), ('230030101015', 'pass123'), ('230030101016', 'pass123'),
            ('230030101017', 'pass123'), ('230030101018', 'pass123'), ('230030101019', 'pass123'),
            ('230030101020', 'pass123'), ('230030101021', 'pass123'), ('230030101022', 'pass123'),
            ('230030101023', 'pass123'), ('230030101024', 'pass123'), ('230030101025', 'pass123'),
            ('230030101026', 'pass123'), ('230030101027', 'pass123'), ('230030101028', 'pass123'),
            ('230030101029', 'pass123'), ('230030101030', 'pass123'), ('230030101032', 'pass123'),
            ('230030101033', 'pass123'), ('230030101034', 'pass123'), ('230030101035', 'pass123'),
            ('230030101036', 'pass123'), ('230030101037', 'pass123'), ('230030101038', 'pass123'),
            ('230030101039', 'pass123'), ('230030101040', 'pass123'), ('230030101041', 'pass123'),
            ('230030101042', 'pass123'), ('230030101043', 'pass123'), ('230030101044', 'pass123'),
            ('230030101046', 'pass123'), ('230030101047', 'pass123'), ('230030101048', 'pass123'),
            ('230030101050', 'pass123'), ('230030101051', 'pass123'), ('230030101052', 'pass123'),
            ('230030101053', 'pass123'), ('230030101055', 'pass123'), ('230030101056', 'pass123'),
            ('230030101057', 'pass123'), ('230030101058', 'pass123'), ('230030101059', 'pass123'),
            ('230030101060', 'pass123'), ('230030101061', 'pass123'), ('230030101063', 'pass123')
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, 'student');", sample_students)

    # --- 5. DEFAULT CANDIDATES LIST ---
    cursor.execute("SELECT COUNT(*) FROM candidates;")
    if cursor.fetchone()[0] == 0:
        sample_candidates = [
            ('Monitor Name One', 0), 
            ('Monitor Name Two', 0)
        ]
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
    cursor.execute("UPDATE users SET custom_name = ?, custom_name_status = 'pending' WHERE id = ?;", (custom_name.strip(), user_id))
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
    cursor.execute("SELECT custom_name FROM users WHERE id = ?;", (user_id,))
    row = cursor.fetchone()
    if row and row['custom_name']:
        c_name = row['custom_name'].strip()
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
