import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime

# ========================================
# GOOGLE SHEETS CONNECTION
# ========================================

@st.cache_resource
def connect_to_sheets():
    """Connect to Google Sheets using service account credentials"""
    try:
        credentials_dict = dict(st.secrets["google_credentials"])
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"❌ Google Sheets connection error: {e}")
        return None

# ========================================
# CORA DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cora_data():
    """Load CORA leads from Google Sheets"""
    try:
        client = connect_to_sheets()
        if client:
            # Get CORA sheet ID from secrets or use default
            sheet_id = st.secrets.get("CORA_SHEET_ID", st.secrets.get("GOOGLE_SHEET_ID"))
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading CORA data: {e}")
        return pd.DataFrame()

def send_approved_leads_to_mark(lead_ids):
    """Send approved Lead IDs to MARK webhook"""
    webhook_url = "https://apexxadams.app.n8n.cloud/webhook/mark-approve-leads"
    
    payload = {
        "approved_leads": lead_ids,
        "approved_by": "Dashboard User",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Increased timeout for processing multiple leads
        response = requests.post(webhook_url, json=payload, timeout=30)
        
        # Check for successful response
        if response.status_code == 200:
            try:
                # Try to parse JSON response from n8n
                result = response.json()
                return True, result
            except:
                # If no JSON, still consider it success
                return True, {"message": "Leads approved successfully"}
        else:
            # Return error details
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                error_msg = f"{error_msg}: {error_detail}"
            except:
                error_msg = f"{error_msg}: {response.text}"
            return False, error_msg
            
    except requests.exceptions.Timeout:
        return False, "Request timed out - workflow may still be processing"
    except requests.exceptions.ConnectionError:
        return False, "Connection failed - check webhook URL and n8n status"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ========================================
# OPSI DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_opsi_data():
    """Load OPSI tasks from Google Sheets"""
    try:
        client = connect_to_sheets()
        if client:
            # OPSI sheet ID
            sheet_id = st.secrets.get("OPSI_SHEET_ID", "1kt4z_zcfiX_Xx3jhahihWMB5LMrh0-GpmQDBxKjSl4A")
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading OPSI data: {e}")
        return pd.DataFrame()

def send_opsi_task(task_data):
    """Send new OPSI task to n8n webhook"""
    # UPDATED: Correct webhook URL for apexxadams
    webhook_url = "https://apexxadams.app.n8n.cloud/webhook/opsi-create-task"
    
    try:
        response = requests.post(webhook_url, json=task_data, timeout=30)
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"success": True, "message": "Task created successfully"}
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                st.error(f"❌ OPSI webhook error: {error_msg} - {error_detail}")
            except:
                st.error(f"❌ OPSI webhook error: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out - task may still be processing")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection failed - check webhook URL and n8n status")
        return None
    except Exception as e:
        st.error(f"❌ Error sending OPSI task: {e}")
        return None

def update_opsi_task(update_data):
    """Update existing OPSI task via n8n webhook"""
    # UPDATED: Correct webhook URL for apexxadams
    webhook_url = "https://apexxadams.app.n8n.cloud/webhook/opsi-update-task"
    
    try:
        response = requests.post(webhook_url, json=update_data, timeout=30)
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"success": True, "message": "Task updated successfully"}
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_detail = response.json()
                st.error(f"❌ OPSI update webhook error: {error_msg} - {error_detail}")
            except:
                st.error(f"❌ OPSI update webhook error: {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out - task update may still be processing")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection failed - check webhook URL and n8n status")
        return None
    except Exception as e:
        st.error(f"❌ Error updating OPSI task: {e}")
        return None
