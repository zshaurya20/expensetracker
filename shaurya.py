import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
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

# User functions
def get_user_budget(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("SELECT monthly_budget FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result and result[0] is not None else 0

def set_user_budget(user_id, budget):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("UPDATE users SET monthly_budget = ? WHERE id = ?", (budget, user_id))
    conn.commit()
    conn.close()

# Expense functions
def get_expenses(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()
    c.execute("SELECT date, category, amount FROM expenses WHERE user_id = ?", (user_id,))
    expenses = c.fetchall()
    conn.close()
    df = pd.DataFrame(expenses, columns=["Date", "Category", "Amount"])
    df["Date"] = pd.to_datetime(df["Date"])  # Ensure Date column is in datetime format
    return df

# Streamlit app
def main():
    st.title("💰 Personal Expense Tracker")

    if "user_id" not in st.session_state:
        st.session_state.user_id = 1  # Default user for testing

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["View Expenses", "Expense Statistics", "Set Budget"])

    # View Expenses
    if page == "View Expenses":
        st.subheader("📋 Your Expenses")
        expenses_df = get_expenses(st.session_state.user_id)
        st.dataframe(expenses_df)

    # Expense Statistics
    elif page == "Expense Statistics":
        st.subheader("📊 Expense Statistics")
        expenses_df = get_expenses(st.session_state.user_id)

        if not expenses_df.empty:
            total_spent = expenses_df["Amount"].sum()
            st.metric("Total Spent", f"${total_spent:.2f}")

            budget = get_user_budget(st.session_state.user_id)
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
            monthly_summary = expenses_df.resample("M", on="Date")["Amount"].sum().reset_index()
            st.line_chart(monthly_summary.set_index("Date"))
        else:
            st.warning("No expenses recorded yet!")

    # Set Budget
    elif page == "Set Budget":
        st.subheader("Set Monthly Budget")
        current_budget = get_user_budget(st.session_state.user_id)
        st.write(f"Current Budget: **${current_budget:.2f}**")
        new_budget = st.number_input("Enter your monthly budget ($)", min_value=0.0, format="%.2f")
        if st.button("Set Budget"):
            set_user_budget(st.session_state.user_id, new_budget)
            st.success(f"Monthly budget set to ${new_budget:.2f}!")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
