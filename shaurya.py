import streamlit as st
import pandas as pd

# Set up the app title
st.title("💰 Personal Expense Tracker Dashboard")

# Load existing expenses
@st.cache_data
def load_data():
    try:
        return pd.read_csv("expenses.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Category", "Amount"])

# Save expenses
def save_data(df):
    df.to_csv("expenses.csv", index=False)

# Load data
df = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Expense", "View Expenses", "Expense Statistics"])

# Page 1: Add Expense
if page == "Add Expense":
    st.subheader("Add New Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Others"])
    amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")

    if st.button("Add Expense"):
        new_data = pd.DataFrame([[date, category, amount]], columns=["Date", "Category", "Amount"])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success("Expense added successfully!")

# Page 2: View Expenses
elif page == "View Expenses":
    st.subheader("📋 Your Expenses")
    st.dataframe(df)

    # Option to delete an expense
    if not df.empty:
        st.subheader("Delete an Expense")
        delete_index = st.number_input("Enter the index of the expense to delete", min_value=0, max_value=len(df) - 1, value=0)
        if st.button("Delete Expense"):
            df = df.drop(index=delete_index).reset_index(drop=True)
            save_data(df)
            st.success("Expense deleted successfully!")

# Page 3: Expense Statistics
elif page == "Expense Statistics":
    st.subheader("📊 Expense Statistics")

    if not df.empty:
        # Total Spent
        total_spent = df["Amount"].sum()
        st.metric("Total Spent", f"${total_spent:.2f}")

        # Category-wise breakdown
        st.subheader("💡 Category-wise Spending")
        category_summary = df.groupby("Category")["Amount"].sum().reset_index()
        st.table(category_summary)

        # Monthly Spending Trend
        st.subheader("📈 Monthly Spending Trend")
        df["Date"] = pd.to_datetime(df["Date"])
        monthly_summary = df.resample("M", on="Date")["Amount"].sum().reset_index()
        st.line_chart(monthly_summary.set_index("Date"))

        # Expense Distribution (Pie Chart Alternative)
        st.subheader("🍰 Expense Distribution")
        st.bar_chart(category_summary.set_index("Category"))
    else:
        st.warning("No expenses recorded yet!")
