import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Multi-Product CVP Analysis", layout="wide")

st.title("Multiple Product CVP Analysis")
st.markdown("""
Adjust the product parameters below to perform a multi-product CVP analysis.  
""")

fixed_cost = st.number_input("Total Fixed Cost ($)", min_value=0.0, value=5000.0, step=1000.0, format="%.2f")

max_products = 100
num_products = st.number_input("Number of Active Products", min_value=1, max_value=max_products, value=3, step=1)

st.divider()
st.subheader("Product Data Inputs")

products = []

for i in range(1, int(num_products) + 1):
    with st.expander(f"Product {i} Inputs", expanded=(i <= 3)):
        col1, col2, col3 = st.columns(3)
        with col1:
            selling_price = st.number_input(f"Selling Price (Product {i})", min_value=0.0, value=10.0, step=1.0, format="%.2f", key=f"sp_{i}")
        with col2:
            variable_cost = st.number_input(f"Variable Cost (Product {i})", min_value=0.0, value=5.0, step=1.0, format="%.2f", key=f"vc_{i}")
        with col3:
            quantity = st.number_input(f"Quantity Sold (Product {i})", min_value=0.0, value=500.0, step=100.0, format="%.0f", key=f"q_{i}")

        products.append({
            "Product": f"Product {i}",
            "Selling Price ($)": selling_price,
            "Variable Cost ($)": variable_cost,
            "Quantity Sold": quantity
        })

df = pd.DataFrame(products)

df_active = df[df["Quantity Sold"] > 0].copy()

if not df_active.empty:
    df_active["Total Revenue ($)"] = df_active["Selling Price ($)"] * df_active["Quantity Sold"]
    df_active["Total Variable Cost ($)"] = df_active["Variable Cost ($)"] * df_active["Quantity Sold"]
    df_active["Contribution Margin ($)"] = df_active["Total Revenue ($)"] - df_active["Total Variable Cost ($)"]

    st.markdown("### Active Product Summary")
    st.dataframe(df_active, use_container_width=True)

    total_revenue = df_active["Total Revenue ($)"].sum()
    total_variable_cost = df_active["Total Variable Cost ($)"].sum()
    total_cm = df_active["Contribution Margin ($)"].sum()
    total_quantity = df_active["Quantity Sold"].sum()

    if total_quantity > 0 and total_revenue > 0:
        cm_per_unit = total_cm / total_quantity
        cm_ratio = total_cm / total_revenue
        vc_ratio = total_variable_cost / total_revenue
        break_even_units = fixed_cost / cm_per_unit if cm_per_unit != 0 else float('inf')
        break_even_dollars = fixed_cost / cm_ratio if cm_ratio != 0 else float('inf')
        mos_units = total_quantity - break_even_units
        mos_dollars = total_revenue - break_even_dollars
        net_operating_income = total_cm - fixed_cost
        dol = total_cm / net_operating_income if net_operating_income != 0 else float('inf')

        st.markdown("### CVP Results Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Contribution Margin per Unit", f"${cm_per_unit:,.2f}")
        col2.metric("Contribution Margin Ratio", f"{cm_ratio:.2%}")
        col3.metric("Variable Cost Ratio", f"{vc_ratio:.2%}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Break-even Units", f"{break_even_units:,.2f}")
        col5.metric("Break-even Dollars", f"${break_even_dollars:,.2f}")
        col6.metric("Net Operating Income", f"${net_operating_income:,.2f}")

        col7, col8, col9 = st.columns(3)
        col7.metric("Total Contribution Margin", f"${total_cm:,.2f}")
        col8.metric("Margin of Safety (Units)", f"{mos_units:,.2f}")
        col9.metric("Margin of Safety (Dollars)", f"${mos_dollars:,.2f}")

        st.markdown("### CVP Graph")

        plt.style.use('Solarize_Light2')

        max_units = int(total_quantity * 1.2) if total_quantity > 0 else 1
        units = range(0, max_units + 1, max(1, int(max_units / 100)))

        total_cost_line = [fixed_cost + (total_variable_cost / total_quantity) * u for u in units]
        total_revenue_line = [(total_revenue / total_quantity) * u for u in units]
        max_y = max(max(total_cost_line), max(total_revenue_line)) * 1.1

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(units, total_revenue_line, label="Total Revenue", color="#814d05", linewidth=1)
        ax.plot(units, total_cost_line, label="Total Cost", color="#6a6359", linewidth=1)
        ax.axhline(fixed_cost, color="#6a563a", linestyle="--", label="Fixed Cost")
        ax.axvline(break_even_units, color="#cfa367", linestyle="--", label="Break-even Point")

        ax.set_xlim(0, max_units)
        ax.set_ylim(0, max_y)
        ax.set_xlabel("Units Sold", fontsize=10)
        ax.set_ylabel("Dollars ($)", fontsize=10)
        ax.set_title("CVP (Cost-Volume-Profit) Graph", fontsize=12, fontweight='bold', color= '#3a2f1f')
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.6)

        be_y = fixed_cost + (total_variable_cost / total_quantity) * break_even_units
        ax.scatter(break_even_units, be_y, color="#cfa367", s=50, zorder=5)
        ax.text(break_even_units, be_y, f"  BEP: {break_even_units:,.0f} units", color="#cfa367", va="top", fontsize=8)

        st.pyplot(fig)
    else:
        st.warning("Please enter valid non-zero values for price and quantity to compute CVP.")
else:
    st.info("⚠️ All products have quantity = 0. Add at least one active product to compute CVP.")
