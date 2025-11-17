import streamlit as st
import pandas as pd
from utils import load_cora_data

def get_cora_status():
    """Return CORA agent status"""
    return "Active"

def get_cora_leads():
    """Get CORA leads as list of dictionaries"""
    try:
        df = load_cora_data()
        return df.to_dict('records') if not df.empty else []
    except:
        return []
