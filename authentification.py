import streamlit as st
import sqlite3
import hashlib

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db',timeout=20)
    c = conn.cursor()
    # Create users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     email TEXT,
                     role TEXT NOT NULL DEFAULT 'user',
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')

    # Create sessions table for tracking logins
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
    (
        session_id TEXT PRIMARY KEY,
        user_id INTEGER,
        login_time TIMESTAMP,
        FOREIGN  KEY
                 (user_id) REFERENCES users
                 (id))''')

    # Create admin user if not exists
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'))
    except sqlite3.IntegrityError:
        pass  # Admin user already exists

    conn.commit()
    conn.close()


# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Authenticate user
def authenticate(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    hashed_password = hash_password(password)
    c.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
              (username, hashed_password))
    user = c.fetchone()
    conn.close()

    return user


# Add new user (admin function)
def add_user(username, password, email, role='user'):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  (username, hashed_password, email, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


# Get all users (admin function)
def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT id, username, email, role, created_at FROM users")
    users = c.fetchall()
    conn.close()

    return users


# Delete user (admin function)
def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    affected_rows = c.rowcount
    conn.close()

    return affected_rows > 0


# Login page
def login_page():
    st.header("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            user = authenticate(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                if st.session_state.user[2] == 'admin':
                    st.session_state.page = 'user_management'
                else:
                    st.session_state.page = 'dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")


# User management page (admin only)
def user_management_page():
    st.header("User Management")

    # Add new user
    with st.expander("Add New User"):
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_email = st.text_input("Email")
            new_role = st.selectbox("Role", ["user", "admin"])
            submit = st.form_submit_button("Add User")

            if submit:
                if add_user(new_username, new_password, new_email, new_role):
                    st.success("User added successfully!")
                else:
                    st.error("Username already exists or invalid data")

    # User list with delete option
    st.subheader("User List")
    users = get_all_users()

    if users:
        for user in users:
            cols = st.columns([2, 3, 2, 2, 1])
            cols[0].write(user[1])  # username
            cols[1].write(user[2])  # email
            cols[2].write(user[3])  # role
            cols[3].write(user[4])  # created_at

            # Don't allow deleting yourself
            if user[0] != st.session_state.user[0] and cols[4].button("X", key=f"delete_{user[0]}"):
                if delete_user(user[0]):
                    st.success(f"User {user[1]} deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete user")
    else:
        st.write("No users found")
