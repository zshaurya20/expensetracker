import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💰 Personal Expense Tracker")

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

# Input fields for new expense
st.subheader("Add New Expense")
date = st.date_input("Date")
category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Others"])
amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")

if st.button("Add Expense"):
    new_data = pd.DataFrame([[date, category, amount]], columns=["Date", "Category", "Amount"])
    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df)
    st.success("Expense added successfully!")
    st.experimental_rerun()  # Refresh page

# Show expense table
st.subheader("📋 Your Expenses")
st.dataframe(df)

# Stats and Charts
st.subheader("📊 Expense Statistics")

if not df.empty:
    total_spent = df["Amount"].sum()
    st.metric("Total Spent", f"${total_spent:.2f}")

    # Category-wise breakdown
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()

    # Bar Chart using Plotly
    st.subheader("💡 Category-wise Spending")
    fig_bar = px.bar(category_summary, x="Category", y="Amount", title="Category-wise Spending")
    st.plotly_chart(fig_bar)

    # Pie Chart using Plotly
    st.subheader("🍰 Category-wise Distribution")
    fig_pie = px.pie(category_summary, values="Amount", names="Category", title="Category-wise Distribution")
    st.plotly_chart(fig_pie)
else:
    st.warning("No expenses recorded yet!")




