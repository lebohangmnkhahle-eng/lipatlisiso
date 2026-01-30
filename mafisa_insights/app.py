import streamlit as st
import uuid
import sys
import os
import pandas as pd
import dataclasses

# Add the parent directory of 'mafisa_insights' to sys.path
# This allows 'import mafisa_insights.data_models' to work when running as a script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from mafisa_insights.data_models import MSME, Financials
from mafisa_insights.storage import DataStore
from mafisa_insights.credit_scoring import calculate_credit_score

def render_msme_portal():
    st.header("MSME Registration & Data Entry")
    st.markdown("Join the Mafisa Insights platform to unlock financial opportunities.")

    with st.form("msme_form"):
        st.subheader("1. Business Profile")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Business Name")
            sector = st.selectbox("Sector", ["Agriculture", "Retail", "Manufacturing", "Services", "Technology", "Other"])
            location = st.text_input("Location (District/City)")
        with col2:
            years = st.number_input("Years in Business", min_value=0, step=1)
            employees = st.number_input("Number of Employees", min_value=1, step=1)
            contact = st.text_input("Contact Info (Phone/Email)")

        st.subheader("2. Financial Information (Monthly Average)")
        col3, col4 = st.columns(2)
        with col3:
            revenue = st.number_input("Monthly Revenue (LSL)", min_value=0.0, step=100.0)
            expenses = st.number_input("Monthly Expenses (LSL)", min_value=0.0, step=100.0)
        with col4:
            inventory = st.number_input("Inventory Value (LSL)", min_value=0.0, step=100.0)
            transactions = st.number_input("Transaction Frequency (per month)", min_value=0, step=1)

        st.subheader("3. Payment Methods")
        payment_methods = st.multiselect("Select Payment Methods Accepted",
                                         ["Cash", "Mobile Money (M-Pesa/EcoCash)", "Bank Transfer", "Card", "Check"])

        submitted = st.form_submit_button("Submit & Calculate Credit Score")

        if submitted:
            if not name or not location or not contact:
                st.error("Please fill in all required fields (Name, Location, Contact).")
            else:
                # Create objects
                fin = Financials(
                    monthly_revenue=revenue,
                    monthly_expenses=expenses,
                    inventory_value=inventory,
                    transaction_frequency=transactions,
                    payment_methods=payment_methods
                )

                msme_id = str(uuid.uuid4())[:8]
                msme = MSME(
                    id=msme_id,
                    name=name,
                    sector=sector,
                    location=location,
                    years_in_business=years,
                    employee_count=employees,
                    contact_info=contact,
                    financials=fin
                )

                # Calculate Score
                score, risk = calculate_credit_score(msme, fin)
                msme.credit_score = score
                msme.risk_category = risk

                # Save
                store = DataStore()
                store.save_msme(msme)

                st.success(f"Registration Successful! Your MSME ID is {msme_id}")
                st.metric("Alternative Credit Score", f"{score}/850", risk)

                if risk == "Low Risk":
                    st.balloons()
                    st.success("Congratulations! You qualify for premium financial products.")
                elif risk == "Medium Risk":
                    st.info("Good standing. Improving transaction volume could help.")
                else:
                    st.warning("Consider digitizing more payments to improve your score.")

def render_lender_dashboard():
    st.header("Lender & Partner Dashboard (DaaS)")
    st.markdown("Access verified MSME data and alternative credit scores.")

    store = DataStore()
    msmes = store.load_msmes()

    if not msmes:
        st.info("No MSMEs registered yet. Please register some businesses first.")
        return

    # Convert to DataFrame for easier analysis
    data = []
    for m in msmes:
        row = {
            "ID": m.id,
            "Name": m.name,
            "Sector": m.sector,
            "Location": m.location,
            "Years in Business": m.years_in_business,
            "Employees": m.employee_count,
            "Revenue": m.financials.monthly_revenue,
            "Credit Score": m.credit_score,
            "Risk Category": m.risk_category
        }
        data.append(row)

    df = pd.DataFrame(data)

    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Registered MSMEs", len(df))
    avg_score = int(df['Credit Score'].mean()) if not df.empty else 0
    kpi2.metric("Average Credit Score", f"{avg_score}")

    low_risk_count = len(df[df['Risk Category'] == 'Low Risk'])
    low_risk_pct = (low_risk_count / len(df)) * 100 if len(df) > 0 else 0
    kpi3.metric("Low Risk MSMEs", f"{low_risk_pct:.1f}%")

    # Filters
    st.subheader("Filter & Search")
    col1, col2 = st.columns(2)
    with col1:
        sectors = df['Sector'].unique().tolist()
        selected_sector = st.multiselect("Filter by Sector", sectors, default=sectors)
    with col2:
        risks = df['Risk Category'].unique().tolist()
        risk_filter = st.multiselect("Filter by Risk Category", risks, default=risks)

    filtered_df = df[df['Sector'].isin(selected_sector) & df['Risk Category'].isin(risk_filter)]

    st.dataframe(filtered_df, use_container_width=True)

    # Deep Dive
    st.subheader("MSME Deep Dive")
    if not filtered_df.empty:
        msme_options = filtered_df['ID'].astype(str) + " - " + filtered_df['Name']
        msme_id_selection = st.selectbox("Select MSME for Details", msme_options)

        if msme_id_selection:
            selected_id = msme_id_selection.split(" - ")[0]
            selected_msme = next((m for m in msmes if m.id == selected_id), None)

            if selected_msme:
                st.write(f"### {selected_msme.name}")
                st.write(f"**Contact:** {selected_msme.contact_info} | **Location:** {selected_msme.location}")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Credit Score", selected_msme.credit_score, selected_msme.risk_category)
                    st.markdown("#### Financials")
                    st.write(f"- **Monthly Revenue:** {selected_msme.financials.monthly_revenue:,.2f} LSL")
                    st.write(f"- **Monthly Expenses:** {selected_msme.financials.monthly_expenses:,.2f} LSL")
                    st.write(f"- **Inventory Value:** {selected_msme.financials.inventory_value:,.2f} LSL")
                with col_b:
                    st.markdown("#### Operational")
                    st.write(f"- **Years in Business:** {selected_msme.years_in_business}")
                    st.write(f"- **Employees:** {selected_msme.employee_count}")
                    st.write(f"- **Payment Methods:** {', '.join(selected_msme.financials.payment_methods)}")
                    st.write(f"- **Transaction Freq:** {selected_msme.financials.transaction_frequency}/mo")
    else:
        st.info("No MSMEs match the current filters.")

def main():
    st.set_page_config(page_title="Mafisa Insights", layout="wide")
    st.sidebar.title("Mafisa Insights")
    st.sidebar.info("Connecting MSMEs to Capital")

    page = st.sidebar.radio("Navigation", ["MSME Portal", "Lender Dashboard"])

    if page == "MSME Portal":
        render_msme_portal()
    elif page == "Lender Dashboard":
        render_lender_dashboard()

if __name__ == "__main__":
    main()
