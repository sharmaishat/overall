# -*- coding: utf-8 -*-
"""Overall.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AqApkr5rKLlqJJrlXcUvPiq7qX4c7M6u
"""


import openpyxl
print(openpyxl.__version__)

import streamlit as st
import pandas as pd
import requests
import io

def load_data():
    """Fetch live data from Google Sheets."""
    sheet_url = "https://docs.google.com/spreadsheets/d/1JEfUN-C0NAPlymKD3euvHDkbCf6BDGBmq1RVjJKD46E/edit?usp=sharing"
    csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=xlsx")

    response = requests.get(csv_url)
    response.raise_for_status()

    with io.BytesIO(response.content) as f:
        orders_df = pd.read_excel(f, sheet_name="Orders", engine='openpyxl')
        metal_df = pd.read_excel(f, sheet_name="Metal Outstanding", engine='openpyxl')

    orders_df.columns = ["Order Date", "Processing Date", "Due Date", "Party Code", "Party Name", "Branch Name",
                         "Status", "Order No.", "Custom Order No", "Quantity", "Column 10", "Column 11",
                         "Metal Required", "Metal Outstanding", "Adjusted Metal Outstanding",
                         "Out Weight", "Out Date", "Description", "Start / Hold", "Notification Status", "Total Metal Required"]

    metal_df = metal_df[["Party Name", "Metal Outstanding", "Updated M Outstanding"]]

    return orders_df, metal_df

def order_tracking_page(orders_df):
    st.title("🔍 Order Tracking Portal - ITAN Jewels")

    search_option = st.radio("Search by:", ["Order Number", "Party Name"])

    # Initialize result as an empty DataFrame
    result = pd.DataFrame()  # This line is added

    if search_option == "Order Number":
        order_number = st.text_input("Enter Order Number:")
        if order_number:
            result = orders_df[orders_df["Custom Order No"].astype(str) == order_number]
    else:
        party_name = st.text_input("Enter Party Name:")
        if party_name:
            result = orders_df[orders_df["Party Name"].str.contains(party_name, case=False, na=False)]

    if not result.empty:
        st.write("### Order Details")
        st.dataframe(result[["Custom Order No", "Party Name", "Status", "Due Date", "Start / Hold"]])
    else:
        st.warning("No matching orders found. Please check your input.")

def client_status_checker(orders_df, metal_df):
    st.title("📊 Client Status Checker")

    party_name = st.text_input("Enter Party Name:")

    if party_name:
        orders = orders_df[orders_df["Party Name"].str.contains(party_name, case=False, na=False)]
        metal_balance = metal_df[metal_df["Party Name"].str.contains(party_name, case=False, na=False)]

        if not orders.empty:
            st.write("### Orders Overview")
            st.dataframe(orders[["Order No.", "Status", "Due Date", "Start / Hold"]])
        else:
            st.warning("No orders found for this client.")

        if not metal_balance.empty:
            st.write("### Metal Balance Status")
            st.write("Outstanding Balance for Metal:")
            st.dataframe(metal_balance[["Metal Outstanding", "Updated M Outstanding"]])
        else:
            st.success("No outstanding metal balance for this client.")

def generate_message_page(orders_df):
    st.title("✉️ Message Maker")

    party_name = st.selectbox("Select Party Name:", orders_df["Party Name"].unique())

    if party_name:
        on_hold_orders = orders_df[(orders_df["Party Name"] == party_name) & (orders_df["Start / Hold"] == "Hold")]
        order_numbers = on_hold_orders["Custom Order No"].dropna().astype(str).tolist()

        message = f"""
        **Subject:** Urgent: Action Required for On-Hold Orders and Outstanding Metal Balance

        Dear {party_name},

        We would like to bring to your attention that the following orders are currently on hold:
        {', '.join(order_numbers) if order_numbers else 'No orders on hold'}

        Additionally, there remains an outstanding metal balance associated with your account.

        We kindly request you to review the details and take the necessary steps at your earliest convenience. Should you require any further clarification or assistance, please do not hesitate to reach out.

        Looking forward to your prompt response.
        Best regards,
        Order Department
        ITAN Jewels """

        st.text_area("Generated Message:", message, height=200)

def main():
    orders_df, metal_df = load_data()

    page = st.sidebar.selectbox("Select a Page", ["Order Tracking", "Client Status Checker", "Message Maker"])

    if page == "Order Tracking":
        order_tracking_page(orders_df)
    elif page == "Client Status Checker":
        client_status_checker(orders_df, metal_df)
    elif page == "Message Maker":
        generate_message_page(orders_df)

if __name__ == "__main__":
    main()

