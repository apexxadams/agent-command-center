import streamlit as st
import pandas as pd
from utils import load_opsi_data

def get_opsi_status():
    """Return OPSI agent status"""
    return "Active"

def load_opsi_tasks():
    """Load OPSI tasks from Google Sheets"""
    try:
        return load_opsi_data()
    except:
        return pd.DataFrame()
