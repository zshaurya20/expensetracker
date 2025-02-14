import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
    category_summary = df.groupby("Category")["Amount"].sum()

    # Bar Chart using Matplotlib
    st.subheader("💡 Category-wise Spending")
    fig, ax = plt.subplots()
    category_summary.plot(kind="bar", ax=ax)
    ax.set_ylabel("Amount ($)")
    ax.set_title("Category-wise Spending")
    st.pyplot(fig)

    # Pie Chart using Matplotlib
    st.subheader("🍰 Category-wise Distribution")
    fig, ax = plt.subplots()
    ax.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
    st.pyplot(fig)
else:
    st.warning("No expenses recorded yet!")
