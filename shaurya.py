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
            password TEXT NOT NULL,
            monthly_budget REAL DEFAULT 0
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

def reset_password(username, new_password):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def get_user_budget(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("SELECT monthly_budget FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0  # Return 0 if no budget is set

def set_user_budget(user_id, budget):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("UPDATE users SET monthly_budget = ? WHERE id = ?", (budget, user_id))
    conn.commit()
    conn.close()

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
    c.execute("SELECT id, date, category, amount FROM expenses WHERE user_id = ?", (user_id,))
    expenses = c.fetchall()
    conn.close()
    return pd.DataFrame(expenses, columns=["ID", "Date", "Category", "Amount"])

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

    # Login/Signup/Forgot Password page
    if st.session_state.user_id is None:
        st.sidebar.title("Login / Signup / Forgot Password")
        choice = st.sidebar.radio("Choose an option", ["Login", "Signup", "Forgot Password"])

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

        elif choice == "Forgot Password":
            st.subheader("Forgot Password")
            username = st.text_input("Enter your username")
            new_password = st.text_input("Enter a new password", type="password")
            if st.button("Reset Password"):
                reset_password(username, new_password)
                st.success("Password reset successfully! Please log in with your new password.")

    # Main app functionality
    if st.session_state.user_id is not None:
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Add Expense", "View Expenses", "Expense Statistics", "Set Budget"])

        # Page 1: Add Expense
        if page == "Add Expense":
            st.subheader("Add New Expense")
            date = st.date_input("Date")
            category = st.text_input("Category (e.g., Food, Transport, etc.)")
            amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
            if st.button("Add Expense"):
                add_expense(st.session_state.user_id, date, category, amount)
                st.success("Expense added successfully!")

        # Page 2: View Expenses
        elif page == "View Expenses":
            st.subheader("📋 Your Expenses")
            expenses_df = get_expenses(st.session_state.user_id)
            if not expenses_df.empty:
                st.dataframe(expenses_df)

                # Export expenses to CSV
                st.subheader("Export Expenses")
                csv = expenses_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Expenses as CSV",
                    data=csv,
                    file_name="expenses.csv",
                    mime="text/csv",
                )

                # Option to delete an expense
                st.subheader("Delete an Expense")
                delete_index = st.number_input("Enter the ID of the expense to delete", min_value=1, max_value=expenses_df["ID"].max(), value=1)
                if st.button("Delete Expense"):
                    delete_expense(st.session_state.user_id, delete_index)
                    st.success("Expense deleted successfully!")
                    st.experimental_rerun()  # Refresh the page
            else:
                st.warning("No expenses recorded yet!")

        # Page 3: Expense Statistics
        elif page == "Expense Statistics":
            st.subheader("📊 Expense Statistics")
            expenses_df = get_expenses(st.session_state.user_id)

            if not expenses_df.empty:
                # Total Spent
                total_spent = expenses_df["Amount"].sum()
                st.metric("Total Spent", f"${total_spent:.2f}")

                # Check monthly budget
                budget = get_user_budget(st.session_state.user_id)
                if budget > 0:
                    st.metric("Monthly Budget", f"${budget:.2f}")
                    if total_spent > budget:
                        st.error("You have exceeded your monthly budget!")
                    else:
                        st.success(f"You have ${budget - total_spent:.2f} left in your budget.")

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

        # Page 4: Set Budget
        elif page == "Set Budget":
            st.subheader("Set Monthly Budget")
            budget = st.number_input("Enter your monthly budget ($)", min_value=0.0, format="%.2f")
            if st.button("Set Budget"):
                set_user_budget(st.session_state.user_id, budget)
                st.success("Monthly budget set successfully!")

        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.experimental_rerun()

# Run the app
if __name__ == "__main__":
    main()
