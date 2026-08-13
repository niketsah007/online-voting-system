import sqlite3

DB_NAME = "voting_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table (Includes 'name' column)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT,
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

    # 3. Admin Account
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin';")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, name, password, role) VALUES ('niket', 'System Admin', 'Niket@1994', 'admin');")

    # 4. Students List (3 values: username, name, password)
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='student';")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('230030101001', 'Aakash Nailwal', 'pass123'),
            ('230030101003', 'Abhishek chamiyal', 'pass123'),
            ('230030101004', 'Aditya bisht', 'pass123'),
            ('230030101005', 'Aishwarya kavidayal', 'pass123'),
            ('230030101006', 'Akash Joshi', 'pass123'),
            ('230030101007', 'Aniket', 'pass123'),
            ('230030101008', 'Anshika Sharma', 'pass123'),
            ('230030101009', 'Arjun', 'pass123'),
            ('230030101010', 'Babli Bisht', 'pass123'),
            ('230030101011', 'Benika Adhikari', 'pass123'),
            ('230030101012', 'Bhavesh Gunwant', 'pass123'),
            ('230030101013', 'Bhavesh Mahtolia', 'pass123'),
            ('230030101014', 'Chankey Pandey', 'pass123'),
            ('230030101015', 'Chetna Kulora', 'pass123'),
            ('230030101016', 'Deepak Singh Bisht', 'pass123'),
            ('230030101017', 'Deepak Singh Chand', 'pass123'),
            ('230030101018', 'Deepika bisht', 'pass123'),
            ('230030101019', 'Gaurav  Joshi', 'pass123'),
            ('230030101020', 'Gaurav Mathpal', 'pass123'),
            ('230030101021', 'Gaurav Singh Chauhan', 'pass123'),
            ('230030101022', 'Himanshu Bisht', 'pass123'),
            ('230030101023', 'Himanshu Budhlakoti', 'pass123'),
            ('230030101024', 'Himanshu Singh Gaira', 'pass123'),
            ('230030101025', 'Jay Sana', 'pass123'),
            ('230030101026', 'Karan Singh Bajwal', 'pass123'),
            ('230030101027', 'Kunal Bisht', 'pass123'),
            ('230030101028', 'Kunal Goswami', 'pass123'),
            ('230030101029', 'Lakshman Singh Bisht', 'pass123'),
            ('230030101030', 'Madhav Shankhdhar', 'pass123'),
            ('230030101032', 'Mayank Bisht', 'pass123'),
            ('230030101033', 'Mayank Danu', 'pass123'),
            ('230030101034', 'Mohd. Suhail', 'pass123'),
            ('230030101035', 'Mohit Rikhari', 'pass123'),
            ('230030101036', 'Nandani joshi', 'pass123'),
            ('230030101037', 'Niket Sah', 'pass123'),
            ('230030101038', 'Nikhil Pandey', 'pass123'),
            ('230030101039', 'Nilesh Tiwari', 'pass123'),
            ('230030101040', 'Nitin Joshi', 'pass123'),
            ('230030101041', 'Nitin tiwari', 'pass123'),
            ('230030101042', 'Pankaj Bisht', 'pass123'),
            ('230030101043', 'Pawan Bisht', 'pass123'),
            ('230030101044', 'Pooja Karakoti', 'pass123'),
            ('230030101046', 'Priyanshi', 'pass123'),
            ('230030101047', 'Priyanshu Upadhyay', 'pass123'),
            ('230030101048', 'Rakesh Pandey', 'pass123'),
            ('230030101050', 'Sachin Bisht', 'pass123'),
            ('230030101051', 'Saurabh Kashyap', 'pass123'),
            ('230030101052', 'Shivam Kumar Singh', 'pass123'),
            ('230030101053', 'Shivam Sharma', 'pass123'),
            ('230030101055', 'Suraj Joshi', 'pass123'),
            ('230030101056', 'Suraj Sharma', 'pass123'),
            ('230030101057', 'Suresh Tripathi', 'pass123'),
            ('230030101058', 'Umra parveen', 'pass123'),
            ('230030101059', 'Vandana Gariya', 'pass123'),
            ('230030101060', 'Vineet Joshi', 'pass123'),
            ('230030101061', 'Yogesh Chandra Pandey', 'pass123'),
            ('230030101063', 'Zeeshan Ansari', 'pass123')
        ]
        # Updated to 3 placeholders: (?, ?, ?, 'student')
        cursor.executemany("INSERT INTO users (username, name, password, role) VALUES (?, ?, ?, 'student');", sample_students)

    # 5. Candidates
    cursor.execute("SELECT COUNT(*) FROM candidates;")
    if cursor.fetchone()[0] == 0:
        sample_candidates = [
            ('Shivam Kumar Singh', 0), 
            ('Niket Sah', 0),
            ('Both-(Shivam - Official, Niket - Unofficial)', 0)
        ]
        cursor.executemany("INSERT INTO candidates (name, vote_count) VALUES (?, ?);", sample_candidates)

    conn.commit()
    conn.close()

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
