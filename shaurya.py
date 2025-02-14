import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    # Create users table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    # Create expenses table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# User authentication functions
def create_user(username, password):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different username.")
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

# Expense functions
def add_expense(user_id, date, category, amount):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (user_id, date, category, amount) VALUES (?, ?, ?, ?)",
        (user_id, date, category, amount),
    )
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("SELECT date, category, amount FROM expenses WHERE user_id = ?", (user_id,))
    expenses = c.fetchall()
    conn.close()
    return pd.DataFrame(expenses, columns=["Date", "Category", "Amount"])

def delete_expense(user_id, expense_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    conn.commit()
    conn.close()

# Streamlit app
def main():
    st.title("💰 Personal Expense Tracker")

    # Session state for user authentication
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # Login/Signup page
    if st.session_state.user_id is None:
        st.sidebar.title("Login / Signup")
        choice = st.sidebar.radio("Choose an option", ["Login", "Signup"])

        if choice == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password.")

        elif choice == "Signup":
            st.subheader("Signup")
            username = st.text_input("Choose a username")
            password = st.text_input("Choose a password", type="password")
            if st.button("Signup"):
                if create_user(username, password):
                    st.success("Account created successfully! Please log in.")

    # Main app functionality
    if st.session_state.user_id is not None:
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Add Expense", "View Expenses", "Expense Statistics"])

        # Page 1: Add Expense
        if page == "Add Expense":
            st.subheader("Add New Expense")
            date = st.date_input("Date")
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Others"])
            amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
            if st.button("Add Expense"):
                add_expense(st.session_state.user_id, date, category, amount)
                st.success("Expense added successfully!")

        # Page 2: View Expenses
        elif page == "View Expenses":
            st.subheader("📋 Your Expenses")
            expenses_df = get_expenses(st.session_state.user_id)
            st.dataframe(expenses_df)

            # Option to delete an expense
            if not expenses_df.empty:
                st.subheader("Delete an Expense")
                delete_index = st.number_input("Enter the index of the expense to delete", min_value=0, max_value=len(expenses_df) - 1, value=0)
                if st.button("Delete Expense"):
                    delete_expense(st.session_state.user_id, delete_index + 1)  # +1 because SQLite IDs start at 1
                    st.success("Expense deleted successfully!")
                    st.experimental_rerun()  # Refresh the page

        # Page 3: Expense Statistics
        elif page == "Expense Statistics":
            st.subheader("📊 Expense Statistics")
            expenses_df = get_expenses(st.session_state.user_id)

            if not expenses_df.empty:
                # Total Spent
                total_spent = expenses_df["Amount"].sum()
                st.metric("Total Spent", f"${total_spent:.2f}")

                # Category-wise breakdown
                st.subheader("💡 Category-wise Spending")
                category_summary = expenses_df.groupby("Category")["Amount"].sum().reset_index()
                st.bar_chart(category_summary.set_index("Category"))

                # Monthly Spending Trend
                st.subheader("📈 Monthly Spending Trend")
                expenses_df["Date"] = pd.to_datetime(expenses_df["Date"])
                monthly_summary = expenses_df.resample("M", on="Date")["Amount"].sum().reset_index()
                st.line_chart(monthly_summary.set_index("Date"))
            else:
                st.warning("No expenses recorded yet!")

        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.experimental_rerun()

# Run the app
if __name__ == "__main__":
    main()
