import streamlit as st
import sqlite3
import datetime
import qrcode
from io import BytesIO
import plotly.express as px
import database as db

# Initialize Database Schema
db.init_db()

st.set_page_config(page_title="Class Election Voting System", page_icon="🗳️", layout="wide")

# Session State Initializations
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# Helper to generate QR Code Image
def generate_qr(text_data):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(text_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ---------------------------------------------------------
# LOGIN SCREEN (login.php replacement)
# ---------------------------------------------------------
def render_login():
    st.markdown("<h2 style='text-align: center;'>🔒 Class Election Voting System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Secure Student & Admin Portal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            username_input = st.text_input("Roll Number / Username")
            password_input = st.text_input("Password", type="password")
            login_button = st.button("Login", type="primary", use_container_width=True)
            
            if login_button:
                if not username_input or not password_input:
                    st.warning("Please fill in all credentials.")
                else:
                    user = db.get_user_by_username(username_input.strip())
                    if user and user['password'] == password_input:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = dict(user)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password!")
            
            st.caption("ℹ️ **Default Accounts:**")
            st.caption("- Student: `101` | Password: `pass123`")
            st.caption("- Admin: `admin` | Password: `admin123`")

# ---------------------------------------------------------
# STUDENT DASHBOARD (dashboard.php & vote.php replacement)
# ---------------------------------------------------------
def render_student_dashboard():
    user = db.get_user_by_username(st.session_state["user"]["username"])
    
    # Top Bar
    c1, c2 = st.columns([4, 1])
    with c1:
        st.title("🗳️ Student Election Dashboard")
        st.subheader(f"Welcome, Student ID: `{user['username']}`")
    with c2:
        if st.button("Logout", type="secondary"):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()
            
    st.divider()

    # Force Password Change if using default password
    if user['password'] == 'pass123':
        st.warning("⚙️ **Security Alert:** Please change your default password.")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            if new_pass.strip():
                db.change_user_password(user['id'], new_pass.strip())
                st.success("Password updated successfully!")
                st.rerun()
            else:
                st.error("Password cannot be empty.")
        st.stop()

    # Case 1: Already Voted OR Custom Name Approved -> Show Digital Receipt
    if user['has_voted'] == 1 or user['custom_name_status'] == 'approved':
        st.balloons()
        with st.container(border=True):
            st.markdown("### ✅ Vote Cast Successfully")
            
            candidate_name = "Custom Candidate"
            if user['voted_for']:
                cands = db.get_candidates()
                for c in cands:
                    if c['id'] == user['voted_for']:
                        candidate_name = c['name']
                        break
            elif user['custom_name_status'] == 'approved':
                candidate_name = f"{user['custom_name']} (Custom Approved)"

            timestamp = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
            
            rc1, rc2 = st.columns([2, 1])
            with rc1:
                st.markdown(f"**Student Roll No:** `{user['username']}`")
                st.markdown(f"**Voted For:** `{candidate_name}`")
                st.markdown(f"**Timestamp:** `{timestamp}`")
                st.markdown(f"**Status:** `VERIFIED & LOGGED`")
            with rc2:
                receipt_url = "https://online-voting-system-niket.streamlit.app"
                qr_bytes = generate_qr(receipt_url)
                st.image(qr_bytes, caption="Digital Receipt Verification QR", width=150)
                
    # Case 2: Custom Name Request Pending
    elif user['custom_name_status'] == 'pending':
        st.info(f"⏳ **Custom Name Request Pending:** Your requested candidate ' **{user['custom_name']}** ' is currently under administrator review.")

    # Case 3: Ready to Vote
    else:
        if user['custom_name_status'] == 'rejected':
            st.error("❌ Your previous custom candidate request was rejected. Please select an existing candidate below.")

        st.subheader("Select a Candidate to Cast Your Vote:")
        candidates = db.get_candidates()
        
        cand_dict = {f"👤 {c['name']}": c['id'] for c in candidates}
        selected_cand = st.radio("Official Candidates List", list(cand_dict.keys()))
        
        if st.button("Confirm Vote", type="primary"):
            selected_id = cand_dict[selected_cand]
            db.cast_vote(user['id'], selected_id)
            st.success("Your vote has been submitted!")
            st.rerun()

        st.divider()
        st.markdown("#### OR Request a Custom Candidate")
        with st.form("custom_name_form"):
            custom_input = st.text_input("Enter Custom Candidate Name")
            submit_custom = st.form_submit_button("Submit Request")
            if submit_custom:
                if custom_input.strip():
                    db.submit_custom_name(user['id'], custom_input.strip())
                    st.success("Custom candidate submitted for admin review!")
                    st.rerun()
                else:
                    st.error("Please enter a valid candidate name.")

# ---------------------------------------------------------
# ADMIN DASHBOARD (admin.php replacement)
# ---------------------------------------------------------
def render_admin_dashboard():
    c1, c2 = st.columns([4, 1])
    with c1:
        st.title("📊 Live Election Results & Admin Panel")
    with c2:
        if st.button("Logout", type="secondary"):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()

    st.divider()

    candidates = db.get_candidates()
    total_votes = sum([c['vote_count'] for c in candidates])
    
    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Votes Cast", total_votes)
    m2.metric("Total Candidates", len(candidates))
    leading_name = candidates[0]['name'] if candidates and total_votes > 0 else "N/A"
    m3.metric("Leading Candidate", leading_name)

    st.divider()

    col_chart, col_moderation = st.columns([1.5, 1])

    # Column 1: Doughnut Chart & Tally
    with col_chart:
        st.subheader("🍩 Live Results Breakdown")
        if total_votes > 0:
            df_labels = [c['name'] for c in candidates]
            df_counts = [c['vote_count'] for c in candidates]
            
            fig = px.pie(
                names=df_labels, 
                values=df_counts, 
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No votes recorded yet.")

        st.subheader("Candidate Standings")
        for c in candidates:
            pct = (c['vote_count'] / total_votes * 100) if total_votes > 0 else 0
            st.write(f"**{c['name']}** — {c['vote_count']} votes ({pct:.1f}%)")
            st.progress(pct / 100)

    # Column 2: Moderation Queue
    with col_moderation:
        st.subheader("📑 Pending Custom Names")
        pending_list = db.get_pending_custom_names()
        
        if pending_list:
            for p in pending_list:
                with st.container(border=True):
                    st.write(f"**Student:** `{p['username']}`")
                    st.write(f"**Requested Name:** `{p['custom_name']}`")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    if btn_col1.button("✔ Approve", key=f"app_{p['id']}", type="primary"):
                        db.approve_custom_name(p['id'])
                        st.success("Approved!")
                        st.rerun()
                    if btn_col2.button("✖ Reject", key=f"rej_{p['id']}"):
                        db.reject_custom_name(p['id'])
                        st.warning("Rejected.")
                        st.rerun()
        else:
            st.success("No pending custom name requests.")

# ---------------------------------------------------------
# MAIN ROUTER
# ---------------------------------------------------------
if not st.session_state["logged_in"]:
    render_login()
else:
    if st.session_state["user"]["role"] == "admin":
        render_admin_dashboard()
    else:
        render_student_dashboard()
