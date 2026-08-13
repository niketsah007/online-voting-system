import streamlit as st
import sqlite3
import datetime
import qrcode
from io import BytesIO
import plotly.express as px
import database as db
import os

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
# LOGIN SCREEN (Tabbed Interface)
# ---------------------------------------------------------
def render_login():
    st.markdown("<h2 style='text-align: center;'>🔒 Class Election Voting System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Official Election Portal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🎓 Student Login", "🛡️ Admin Login"])
        
        # --- STUDENT LOGIN TAB ---
        with tab1:
            with st.container(border=True):
                st.subheader("Student Portal")
                # Default login values applied here
                student_user = st.text_input("Roll Number", value="230030101001", key="student_user")
                if student_user:
                    user_info = db.get_user_by_username(student_user.strip())
                    if user_info and user_info['role'] == 'student':
                        # Display the student's name in a nice success box
                        st.success(f"👋 Welcome, **{user_info['name']}**!")
                    elif user_info and user_info['role'] == 'admin':
                        st.error("Admins must log in via the Admin tab.")
                    else:
                        st.warning("Roll number not found. Please check and try again.")
                        
                student_pass = st.text_input("Password", value="pass123", type="password", key="student_pass")
                student_login = st.button("Login as Student", type="primary", use_container_width=True)
                
                if student_login:
                    if not student_user or not student_pass:
                        st.warning("Please fill in all credentials.")
                    else:
                        user = db.get_user_by_username(student_user.strip())
                        if user and user['password'] == student_pass and user['role'] == 'student':
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = dict(user)
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid Roll Number or Password!")

        # --- ADMIN LOGIN TAB ---
        with tab2:
            with st.container(border=True):
                st.subheader("Admin Portal")
                # No hints or default values for Admin
                admin_user = st.text_input("Admin Username", key="admin_user")
                admin_pass = st.text_input("Password", type="password", key="admin_pass")
                admin_login = st.button("Login as Admin", type="primary", use_container_width=True)
                
                if admin_login:
                    if not admin_user or not admin_pass:
                        st.warning("Please fill in all credentials.")
                    else:
                        user = db.get_user_by_username(admin_user.strip())
                        if user and user['password'] == admin_pass and user['role'] == 'admin':
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = dict(user)
                            st.success("Admin login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid Admin Credentials!")

# ---------------------------------------------------------
# STUDENT DASHBOARD 
# ---------------------------------------------------------
def render_student_dashboard():
    user = db.get_user_by_username(st.session_state["user"]["username"])
    
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

    # -- VOLUNTARY STUDENT PASSWORD CHANGE --
    with st.expander("⚙️ Account Settings (Change Password)"):
        with st.form("voluntary_pass_change"):
            vol_new_pass = st.text_input("Enter New Password", type="password")
            submit_new_pass = st.form_submit_button("Update Password")
            if submit_new_pass:
                if vol_new_pass.strip():
                    db.change_user_password(user['id'], vol_new_pass.strip())
                    st.success("Your password has been updated securely!")
                else:
                    st.error("Password cannot be empty.")

    # Force Password Change if using default password
    if user['password'] == 'pass123':
        st.warning("⚙️ **Security Alert:** Please change your default password to continue.")
        new_pass = st.text_input("New Password", type="password", key="force_new_pass")
        if st.button("Update Password", key="force_update_btn"):
            if new_pass.strip():
                db.change_user_password(user['id'], new_pass.strip())
                st.success("Password updated successfully!")
                st.rerun()
            else:
                st.error("Password cannot be empty.")
        st.stop()

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
                # Text-based QR code for direct mobile scanning
                receipt_text = f"OFFICIAL ELECTION RECEIPT\n----------------------\nRoll No: {user['username']}\nCandidate: {candidate_name}\nStatus: VERIFIED & LOGGED\nTimestamp: {timestamp}"
                qr_bytes = generate_qr(receipt_text)
                st.image(qr_bytes, caption="Scan to view receipt on phone", width=150)
                
    elif user['custom_name_status'] == 'pending':
        st.info(f"⏳ **Custom Name Request Pending:** Your requested candidate ' **{user['custom_name']}** ' is currently under administrator review.")

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
# ADMIN DASHBOARD 
# ---------------------------------------------------------
def render_admin_dashboard():
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        st.title("📊 Live Election Results & Admin Panel")
    with c2:
        # -- DOWNLOAD DATABASE BUTTON --
        if os.path.exists("voting_system.db"):
            with open("voting_system.db", "rb") as file:
                st.download_button(
                    label="💾 Database",
                    data=file,
                    file_name="voting_system.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )
    with c3:
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()

    st.divider()

    candidates = db.get_candidates()
    total_votes = sum([c['vote_count'] for c in candidates])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Votes Cast", total_votes)
    m2.metric("Total Candidates", len(candidates))
    leading_name = candidates[0]['name'] if candidates and total_votes > 0 else "N/A"
    m3.metric("Leading Candidate", leading_name)

    st.divider()
    
    # -- ADMIN PASSWORD RESET TOOL --
    with st.expander("🔑 Reset a Student's Password"):
        with st.form("reset_pass_form"):
            roll_to_reset = st.text_input("Enter Student Roll No (e.g., 230030101001)")
            submit_reset = st.form_submit_button("Reset to Default ('pass123')")
            if submit_reset:
                user_to_reset = db.get_user_by_username(roll_to_reset.strip())
                if user_to_reset:
                    db.change_user_password(user_to_reset['id'], "pass123")
                    st.success(f"Successfully reset password for {roll_to_reset} back to 'pass123'.")
                else:
                    st.error("Student Roll No not found in the database.")
                    
    st.divider()

    col_chart, col_moderation = st.columns([1.5, 1])

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
