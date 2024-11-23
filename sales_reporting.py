# sales_reporting.py
import streamlit as st
from firebase_init import db
import pandas as pd
import datetime
from menu import menu  # Import menu to get price and cost data

def sales_reporting():
    st.title("Sales Reporting")

    # Fetch the list of branches
    branches_ref = db.collection("branches").stream()
    branches = [{"id": branch.id, **branch.to_dict()} for branch in branches_ref]

    if branches:
        # Wrap branch selection in a container
        with st.container(border=True):
            st.subheader("Select Branch for Sales Reporting")
            # Select a branch for sales reporting
            branch_names = [branch["cafe_name"] for branch in branches]
            selected_branch_name = st.selectbox("Select Branch", branch_names)
            selected_branch_id = next(
                branch["id"] for branch in branches if branch["cafe_name"] == selected_branch_name)

        # Fetch Orders for the selected branch
        orders_ref = db.collection("orders").where("branch_id", "==", selected_branch_id).stream()
        orders = []
        for o in orders_ref:
            order_data = o.to_dict()
            order_time = order_data["order_time"]
            items = order_data.get("items", [])
            for item in items:
                coffee = item["coffee"]
                quantity = item["quantity"]
                price_per_item = menu[coffee]["price"]
                cost_per_item = menu[coffee]["cost"]
                total_price = price_per_item * quantity
                total_cost = cost_per_item * quantity
                orders.append({
                    "coffee": coffee,
                    "quantity": quantity,
                    "price": total_price,
                    "cost": total_cost,
                    "order_time": order_time
                })

        # Convert Orders to DataFrame
        if orders:
            df = pd.DataFrame(orders)
            df["order_time"] = pd.to_datetime(df["order_time"])

            # Wrap total sales report in a container
            with st.container(border=True):
                # Total Sales Report
                st.subheader("Total Sales Report")
                daily_sales = df.groupby(df["order_time"].dt.date)["price"].sum()
                st.bar_chart(daily_sales)

            # Wrap sales breakdown in a container
            with st.container(border=True):
                # Sales Breakdown by Coffee Type (Sum Quantities Correctly)
                st.subheader("Sales Breakdown by Coffee Type")
                coffee_breakdown = df.groupby("coffee")["quantity"].sum().reset_index()
                coffee_breakdown.columns = ["Coffee", "Count"]

                # Add a new "No." column starting from 1
                coffee_breakdown.insert(0, "No.", range(1, len(coffee_breakdown) + 1))
                st.dataframe(coffee_breakdown, hide_index=True)

            # Wrap best and worst sellers in a container
            with st.container(border=True):
                # Best and Worst Sellers
                st.subheader("Best and Worst Sellers")
                if not coffee_breakdown.empty:
                    best_seller = coffee_breakdown.loc[coffee_breakdown["Count"].idxmax()]
                    worst_seller = coffee_breakdown.loc[coffee_breakdown["Count"].idxmin()]
                    st.write(f"**Best Seller:** {best_seller['Coffee']} ({best_seller['Count']} units)")
                    st.write(f"**Worst Seller:** {worst_seller['Coffee']} ({worst_seller['Count']} units)")

            # Wrap total profit calculation in a container
            with st.container(border=True):
                # Total Profit Calculation
                st.subheader("Total Profit Calculation")
                # Calculate total profit by subtracting costs from prices
                df["profit"] = df["price"] - df["cost"]
                total_profit = df["profit"].sum()
                st.write(f"**Total Profit:** RM {total_profit:.2f}")
        else:
            st.warning(f"No sales data available for the selected branch: {selected_branch_name}.")
    else:
        st.warning("No branches available. Please add branches to manage sales reporting.")
