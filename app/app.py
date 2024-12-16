import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.data_processing import calculate_budget, update_budget
from modules.eda import generate_pie_chart
from modules.upi_integration import process_payment
import os

# Initialize session state for budget and transactions
if "budget_data" not in st.session_state:
    st.session_state["budget_data"] = None
if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

# App configuration
st.set_page_config(page_title="Financial AI Assistant", page_icon="💸", layout="wide")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Home", "Transaction History"])

# Page: Home
if menu == "Home":
    st.title("💸 Financial AI Assistant")

    # Step 1: Input Monthly Income
    st.markdown("### Enter Monthly Income")
    income = st.number_input("Monthly Income (₹):", min_value=0, step=1000)

    # Step 2: Automatically Generate Budget
    if income > 0:
        st.markdown("### Generated Budget")
        categories = ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Savings"]
        percentages = [30, 20, 15, 10, 10, 15]  # Budget percentages

        if st.session_state["budget_data"] is None:
            budget = calculate_budget(income, percentages)
            st.session_state["budget_data"] = pd.DataFrame({"Category": categories, "Remaining Budget (₹)": budget})

        budget_df = st.session_state["budget_data"]
        st.dataframe(budget_df)

        # Expense distribution chart
        st.markdown("### 📊 Expense Distribution")
        fig = generate_pie_chart(budget_df["Remaining Budget (₹)"], budget_df["Category"])
        st.pyplot(fig)

        # Payment Feature
        st.markdown("### 💳 UPI Payment")
        payment_category = st.selectbox("Select category to pay:", categories[:-1])  # Exclude "Savings"
        payment_amount = st.number_input(f"Enter amount to pay for {payment_category}:", min_value=0, step=50)

        if st.button("Make Payment"):
            # Update budget and transactions
            payment_status, updated_budget = update_budget(
                st.session_state["budget_data"], payment_category, payment_amount
            )
            st.session_state["budget_data"] = updated_budget

            if "paid" in payment_status:
                st.session_state["transactions"].append(
                    {"Category": payment_category, "Amount Paid (₹)": payment_amount}
                )
            st.success(payment_status)

        # Save budget data
        if st.button("Save Budget Data"):
            budget_df.to_csv("auto_budget_data.csv", index=False)
            st.success("Budget data saved successfully!")

    else:
        st.warning("Please enter your monthly income to generate the budget.")

# Page: Transaction History
elif menu == "Transaction History":
    st.title("📜 Transaction History")

    # Display transaction history
    if st.session_state["transactions"]:
        st.markdown("### Payments Made")
        transactions_df = pd.DataFrame(st.session_state["transactions"])
        st.dataframe(transactions_df)

        # Display updated budget
        st.markdown("### Updated Budget")
        st.dataframe(st.session_state["budget_data"])

    else:
        st.info("No transactions made yet.")
