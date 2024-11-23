# analytics.py
import streamlit as st
from firebase_init import db
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from menu import menu  # Import menu to get price and cost data

def analytics_dashboard():
    st.title("Analytics Dashboard")

    # Branch Selection
    branches_ref = db.collection("branches").stream()
    branches = [{"Branch Name": b.to_dict()["cafe_name"], "Branch ID": b.id} for b in branches_ref]

    if not branches:
        st.warning("No branches available. Please contact admin.")
        return  # Exit the function if no branches are available
    else:
        branch_names = [branch["Branch Name"] for branch in branches]
        selected_branch_name = st.selectbox("Select Branch for Analytics", branch_names)
        selected_branch_id = next(
            branch["Branch ID"] for branch in branches if branch["Branch Name"] == selected_branch_name
        )

    # Real-Time Monitoring
    st.subheader(f"Real-Time Monitoring for {selected_branch_name}")

    # Fetch Orders for the Selected Branch
    orders_ref = db.collection("orders").where("branch_id", "==", selected_branch_id).stream()
    orders = []
    for o in orders_ref:
        order_data = o.to_dict()
        order_time = order_data["order_time"]
        customer = order_data.get("customer", "Unknown")
        items = order_data.get("items", [])
        for item in items:
            coffee = item["coffee"]
            quantity = item["quantity"]
            price_per_item = menu[coffee]["price"]
            total_price = price_per_item * quantity
            orders.append({
                "Order Time": order_time,
                "Coffee": coffee,
                "Quantity": quantity,
                "Price (RM)": total_price,
                "Customer": customer
            })

    if orders:
        # Convert orders to DataFrame
        df_orders = pd.DataFrame(orders)
        df_orders["Order Time"] = pd.to_datetime(df_orders["Order Time"])
        df_orders["Price (RM)"] = df_orders["Price (RM)"].astype(float)

        # Latest Orders
        container = st.container(border=True)
        with container:
            st.subheader("Latest Orders")
            latest_orders = df_orders.sort_values("Order Time", ascending=False).head(10)
            # Format the Price (RM) column to two decimal places
            latest_orders["Price (RM)"] = latest_orders["Price (RM)"].map('{:.2f}'.format)
            # Reset the index to start from 1 and name it 'No.'
            latest_orders = latest_orders.reset_index(drop=True)
            latest_orders.index += 1
            latest_orders.index.name = 'No.'
            st.write("Latest 10 Order Items:")
            st.table(latest_orders)

        # Sales Stats
        container = st.container(border=True)
        with container:
            st.subheader("Sales Stats (Today)")
            today = datetime.datetime.now().date()
            df_today = df_orders[df_orders["Order Time"].dt.date == today]
            total_sales = df_today["Price (RM)"].sum()
            avg_order_value = df_today.groupby("Customer")["Price (RM)"].sum().mean() if not df_today.empty else 0
            total_orders = df_today["Customer"].nunique()

            st.metric("Total Sales", f"RM {total_sales:.2f}")
            st.metric("Average Order Value", f"RM {avg_order_value:.2f}")
            st.metric("Total Orders", total_orders)

        # Generate Sales Charts
        if not df_today.empty:
            st.subheader("Sales Charts (Today)")

            # Hourly Sales Over Time
            container = st.container(border=True)
            with container:
                df_today['Hour'] = df_today["Order Time"].dt.hour
                hourly_sales = df_today.groupby('Hour')["Price (RM)"].sum().reset_index()
                hourly_sales["Hour"] = hourly_sales["Hour"].apply(lambda x: f"{x}:00")

                # Create a copy for display formatting
                hourly_sales_display = hourly_sales.copy()
                hourly_sales_display["Price (RM)"] = hourly_sales_display["Price (RM)"].map('{:.2f}'.format)

                fig1 = px.bar(
                    hourly_sales,
                    x="Hour",
                    y="Price (RM)",
                    title="Hourly Sales Trends",
                    labels={"Hour": "Time", "Price (RM)": "Total Sales (RM)"},
                    text=hourly_sales_display["Price (RM)"]
                )
                fig1.update_traces(textposition="outside")
                fig1.update_layout(
                    xaxis=dict(tickmode="linear", title="Time"),
                    yaxis=dict(title="Total Sales (RM)"),
                    template="plotly_white"
                )
                fig1.update_yaxes(tickformat=".2f")
                st.plotly_chart(fig1, use_container_width=True)

            # Coffee-wise Sales Distribution
            container = st.container(border=True)
            with container:
                coffee_sales = df_today.groupby("Coffee")["Price (RM)"].sum().reset_index()
                coffee_sales = coffee_sales.sort_values("Price (RM)", ascending=True)

                # Create a copy for display formatting
                coffee_sales_display = coffee_sales.copy()
                coffee_sales_display["Price (RM)"] = coffee_sales_display["Price (RM)"].map('{:.2f}'.format)

                fig2 = px.bar(
                    coffee_sales,
                    x="Price (RM)",
                    y="Coffee",
                    orientation="h",
                    labels={"Price (RM)": "Total Sales (RM)", "Coffee": "Coffee Types"},
                    title="Coffee-wise Sales Distribution",
                    text=coffee_sales_display["Price (RM)"]
                )
                fig2.update_traces(textposition="outside")
                fig2.update_layout(
                    xaxis=dict(title="Total Sales (RM)"),
                    yaxis=dict(title="Coffee Types"),
                    template="plotly_white",
                    height=500
                )
                fig2.update_xaxes(tickformat=".2f")
                st.plotly_chart(fig2, use_container_width=True)

            # Top Customers
            container = st.container(border=True)
            with container:
                st.subheader("Top Customers (Today)")
                top_customers = df_today.groupby("Customer")["Price (RM)"].sum().reset_index()
                top_customers = top_customers.sort_values("Price (RM)", ascending=False).head(5)
                # Format the Price (RM) column to two decimal places
                top_customers["Price (RM)"] = top_customers["Price (RM)"].map('{:.2f}'.format)
                # Reset the index to start from 1 and name it 'Rank'
                top_customers = top_customers.reset_index(drop=True)
                top_customers.index += 1
                top_customers.index.name = 'Rank'
                st.table(top_customers)

            # Profit Analysis
            container = st.container(border=True)
            with container:
                st.subheader("Profit Analysis (Today)")
                df_today["Cost"] = df_today.apply(
                    lambda row: menu[row["Coffee"]]["cost"] * row["Quantity"], axis=1)
                df_today["Profit"] = df_today["Price (RM)"] - df_today["Cost"]
                total_profit = df_today["Profit"].sum()
                profit_margin = (total_profit / total_sales) * 100 if total_sales else 0
                st.metric("Total Profit", f"RM {total_profit:.2f}")
                st.metric("Profit Margin", f"{profit_margin:.2f}%")
        else:
            st.info("No sales data available for today.")
    else:
        st.warning(f"No orders placed yet for {selected_branch_name}.")

    # Inventory Health Check
    container = st.container(border=True)
    with container:
        st.subheader(f"Inventory Health Check for {selected_branch_name}")

        # Fetch Inventory for the Selected Branch
        branch_ref = db.collection("branches").document(selected_branch_id).get()
        branch_inventory = branch_ref.to_dict()["inventory"] if branch_ref.exists else {}
        low_stock_threshold = {
            "coffee_beans": 100,
            "cup": 50,
            "milk": 20,
            "sugar": 10
        }

        # Inventory Health Check section
        inventory_items = [
            {
                "Item": item_key.replace('_', ' ').title(),
                "Stock": stock,
                "Threshold": low_stock_threshold.get(item_key, 50)
            }
            for item_key, stock in branch_inventory.items()
        ]

        if inventory_items:
            df_inventory = pd.DataFrame(inventory_items)
            # Reset the index to start from 1 and name it 'No.'
            df_inventory = df_inventory.reset_index(drop=True)
            df_inventory.index += 1
            df_inventory.index.name = 'No.'
            st.write("Current Inventory Levels:")
            st.table(df_inventory)

            # Generate Inventory Chart using Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_inventory["Item"],
                y=df_inventory["Stock"],
                name="Stock",
                marker_color="#83c9ff"
            ))
            fig.add_trace(go.Scatter(
                x=df_inventory["Item"],
                y=df_inventory["Threshold"],
                mode="lines+markers+text",
                name="Threshold",
                line=dict(color="red", dash="dot"),
                text=df_inventory["Threshold"],
                textposition="top center"
            ))
            fig.update_layout(
                title="Inventory Levels and Thresholds",
                xaxis_title="Items",
                yaxis_title="Units",
                legend_title="Legend",
                template="plotly_white",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display Low Stock Alerts
            low_stock_items = [row for row in inventory_items if row["Stock"] < row["Threshold"]]
            if low_stock_items:
                low_stock_df = pd.DataFrame(low_stock_items)
                # Reset index for low stock items
                low_stock_df = low_stock_df.reset_index(drop=True)
                low_stock_df.index += 1
                low_stock_df.index.name = 'No.'
                st.warning("The following items are running low:")
                st.table(low_stock_df)
            else:
                st.success("All inventory items are healthy.")
        else:
            st.warning("No inventory data available for this branch.")
