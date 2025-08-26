import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import boto3

from supplierRankingSys import SupplierRankingSystem
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Define a function to run sync code in a thread
executor = ThreadPoolExecutor()


async def run_system_async(system, df, company, mail):
    loop = asyncio.get_running_loop()

    # Use a lambda or functools.partial to pass the function without calling it
    result = await loop.run_in_executor(executor, lambda: system.rank(df, company, mail))

    return result

def dashboard_page():


    st.set_page_config(layout="wide")
    st.title("Supplier Ranking System")

    st.markdown("""
    #### 🚀 Research Project: Help Us Improve Supplier Risk Models

    We are conducting a **research project** to develop a machine learning model for assessing supplier risk.  
    By participating and uploading your supplier data:

    - ✅ You contribute to the advancement of supply chain risk analytics.
    - 📩 In return, you'll **receive a personalized report via email** ranking your suppliers based on the risk criteria you configure below.
    - 🔒 Your data is securely stored and used only for research and model training purposes.

    Thank you for supporting research in responsible AI for supply chain management!
    """)

    st.markdown("### Company Information (Required)")
    company_name = st.text_input("Company Name")
    contact_email = st.text_input("Contact Email")
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

    if not company_name or not contact_email:
        st.warning("Please fill in both Company Name and Contact Email to proceed.")
        st.stop()

    if company_name and contact_email and uploaded_file:
        df = pd.read_csv(uploaded_file, nrows=10)
        st.success("File uploaded successfully!")
        st.dataframe(df.head(10))

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        supplier_col = st.selectbox("Select supplier identifier column", options=df.columns)
        df.rename(columns={supplier_col: "Fournisseur"}, inplace=True)

        st.markdown("### Select Criteria Columns (Defaults to all numeric columns)")
        selected_criteria = st.multiselect(
            "Choose the criteria columns:",
            options=numeric_cols,
            default=numeric_cols
        )

        criteria_data = [{
            'Criterion': col,
            'Weight': 0.1,
            'Beneficial': True,
            'Minimum': None,
            'Maximum': None
        } for col in selected_criteria]
        criteria_df = pd.DataFrame(criteria_data)

        st.markdown("### Configure Criteria")
        st.write("Adjust weights, mark as beneficial, and define optional thresholds. You can delete rows too.")

        edited_df = st.data_editor(
            criteria_df,
            column_config={
                "Weight": st.column_config.NumberColumn(
                    "Weight",
                    min_value=0.0,
                    max_value=1.0,
                    step=0.05,
                    format="%.2f"
                ),
                "Beneficial": st.column_config.CheckboxColumn(
                    "Beneficial?",
                    help="Check if higher values are better for this criterion",
                    default=True
                ),
                "Minimum": st.column_config.NumberColumn(
                    "Minimum (optional)",
                    required=False
                ),
                "Maximum": st.column_config.NumberColumn(
                    "Maximum (optional)",
                    required=False
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )

        # Legal acknowledgement section
        st.markdown("### Legal Acknowledgement")

        st.markdown(
            'Please review our [Terms and Conditions](./static/terms_and_conditions.html) before submitting.',
            unsafe_allow_html=True
        )
        legal_ack = st.checkbox("I have read and agree to the Terms and Conditions.")

        if not legal_ack:
            st.warning("You must accept the Terms and Conditions before submitting.")

        if st.button("Submit") and legal_ack:


            beneficial = edited_df[edited_df['Beneficial']]['Criterion'].tolist()
            non_beneficial = edited_df[~edited_df['Beneficial']]['Criterion'].tolist()
            weights = dict(zip(edited_df['Criterion'], edited_df['Weight']))

            system = SupplierRankingSystem(beneficial, non_beneficial, weights)
            st.success(f"You will receive the report by email in a few minutes.")
            asyncio.run(run_system_async(system, df, company_name, contact_email))
            st.success(f"Uploaded: ")
