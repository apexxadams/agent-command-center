import streamlit as st
import pandas as pd
from utils import load_cora_data
from datetime import datetime

def get_cora_status():
    return "Active"

def get_cora_leads():
    try:
        df = load_cora_data()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

def cora_page():
    st.header("CORA - Lead Generation Dashboard")

    df = load_cora_data()

    if df.empty:
        st.info("No CORA data available.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Leads", len(df))

    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = df["timestamp"].str.contains(today, na=False).sum() if "timestamp" in df.columns else 0
        st.metric("Today", today_count)

    with col3:
        cities = df["organization"].str.contains("City", case=False, na=False).sum()
        st.metric("Cities", cities)

    with col4:
        churches = df["organization"].str.contains("Church", case=False, na=False).sum()
        st.metric("Churches", churches)

    st.markdown("---")

    search = st.text_input("Search leads...")
    filtered = df.copy()

    if search:
        mask = (
            df["name"].str.contains(search, case=False, na=False)
            | df["email"].str.contains(search, case=False, na=False)
            | df["organization"].str.contains(search, case=False, na=False)
        )
        filtered = df[mask]

    st.subheader(f"All Leads ({len(filtered)})")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "Export CSV",
        filtered.to_csv(index=False),
        f"cora_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv"
    )

