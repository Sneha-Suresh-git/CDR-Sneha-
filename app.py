import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import PyPDF2
import re
import plotly.express as px

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Page config
st.set_page_config(page_title="CDR Analysis Pro", page_icon="📡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        border: none;
    }
    .stButton>button:hover {background-color: #45a049;}
</style>
""", unsafe_allow_html=True)

def get_tower_location(mcc, mnc, lac, cid, api_key):
    """Get cell tower location from Unwired Labs API"""
    try:
        url = "https://us1.unwiredlabs.com/v2/process.php"
        payload = {
            "token": api_key,
            "radio": "gsm",
            "mcc": int(mcc),
            "mnc": int(mnc),
            "cells": [{"lac": int(lac), "cid": int(cid)}],
            "address": 1
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return {
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'accuracy': data.get('accuracy', 1000),
                    'address': data.get('address', 'N/A')
                }
        return {'error': 'Failed to get location'}
    except Exception as e:
        return {'error': str(e)}

def create_map(lat, lon, accuracy, address):
    """Create folium map with tower location"""
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], popup=address, tooltip="Cell Tower").add_to(m)
    folium.Circle([lat, lon], radius=accuracy, color='red', fill=True, fillOpacity=0.2).add_to(m)
    return m

def parse_call_records(text):
    """Parse call records from Jio bill text"""
    records = []
    lines = text.split('\n')
    
    for line in lines:
        if len(line.strip()) < 15:
            continue
        
        # Find phone numbers
        phones = re.findall(r'\b[6-9]\d{9}\b', line)
        if not phones:
            continue
        
        # Find dates and times
        dates = re.findall(r'\b\d{1,2}[-/][A-Z]{3}[-/]\d{2,4}\b', line, re.IGNORECASE)
        times = re.findall(r'\b\d{1,2}:\d{2}\b', line)
        
        # Find duration in seconds
        parts = line.split()
        duration_seconds = 0
        
        for i, part in enumerate(parts):
            if part in phones:
                for j in range(i+1, min(i+5, len(parts))):
                    try:
                        potential_duration = int(parts[j])
                        if 1 <= potential_duration <= 14400:  # Max 4 hours
                            duration_seconds = potential_duration
                            break
                    except:
                        continue
                if duration_seconds > 0:
                    break
        
        if phones and duration_seconds > 0:
            records.append({
                'phone': phones[0],
                'date': dates[0] if dates else 'N/A',
                'time': times[0] if times else 'N/A',
                'duration_seconds': duration_seconds
            })
    
    return records

def analyze_records(records):
    """Analyze call records and return statistics"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    df = df[df['duration_seconds'] > 0]
    
    if len(df) == 0:
        return None
    
    phone_stats = df.groupby('phone').agg({
        'duration_seconds': ['sum', 'count', 'mean', 'max']
    }).round(2)
    
    phone_stats.columns = ['Total (s)', 'Count', 'Avg (s)', 'Max (s)']
    phone_stats = phone_stats.sort_values('Total (s)', ascending=False)
    
    most_contacted = df['phone'].value_counts()
    
    return {
        'df': df,
        'total_calls': len(df),
        'total_duration': df['duration_seconds'].sum(),
        'avg_duration': df['duration_seconds'].mean(),
        'longest_call': df['duration_seconds'].max(),
        'phone_stats': phone_stats,
        'most_contacted': most_contacted.index[0] if len(most_contacted) > 0 else 'N/A',
        'most_contacted_count': most_contacted.values[0] if len(most_contacted) > 0 else 0
    }

# Main App
st.title("📡 CDR Analysis Pro")
st.markdown("**Professional Call Data Record Analysis & Tower Location Tracking**")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Feature", ["🗼 Tower Location", "📊 Bill Analysis"])
    
    st.markdown("---")
    st.header("Settings")
    api_key = st.text_input("Unwired Labs API Key", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
    
    st.markdown("---")
    st.info("Get your free API key at [unwiredlabs.com](https://unwiredlabs.com/)")

# Tower Location Page
if page == "🗼 Tower Location":
    st.header("🗼 Cell Tower Location Tracker")
    
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your API key in the sidebar")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            mcc = st.number_input("MCC (Mobile Country Code)", min_value=0, value=404, help="India: 404, 405")
            mnc = st.number_input("MNC (Mobile Network Code)", min_value=0, value=11, help="Jio: 11, Airtel: 10, 45, 49")
        
        with col2:
            lac = st.number_input("LAC/TAC (Location Area Code)", min_value=0, value=1234)
            cid = st.number_input("Cell ID", min_value=0, value=12345)
        
        if st.button("🔍 Locate Tower", type="primary"):
            with st.spinner("Locating tower..."):
                result = get_tower_location(mcc, mnc, lac, cid, st.session_state.api_key)
                
                if 'error' in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.success("✅ Tower location found!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Latitude", f"{result['lat']:.6f}")
                    col2.metric("Longitude", f"{result['lon']:.6f}")
                    col3.metric("Accuracy", f"±{result['accuracy']}m")
                    
                    st.info(f"📍 Address: {result['address']}")
                    
                    tower_map = create_map(result['lat'], result['lon'], result['accuracy'], result['address'])
                    st_folium(tower_map, width=700, height=500)
                    
                    st.markdown(f"[📍 Open in Google Maps](https://www.google.com/maps?q={result['lat']},{result['lon']})")

# Bill Analysis Page
else:
    st.header("📊 Call Bill Analysis")
    
    uploaded_file = st.file_uploader("Upload your Jio call bill (PDF)", type=['pdf'])
    
    if uploaded_file:
        if st.button("🔍 Analyze Bill", type="primary"):
            with st.spinner("Analyzing bill..."):
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    records = parse_call_records(text)
                    
                    if not records:
                        st.warning("⚠️ No call records found in the PDF")
                    else:
                        analysis = analyze_records(records)
                        
                        if analysis:
                            st.success(f"✅ Successfully analyzed {analysis['total_calls']} calls!")
                            
                            # Metrics
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Total Calls", analysis['total_calls'])
                            col2.metric("Total Duration", f"{int(analysis['total_duration']//60)}m {int(analysis['total_duration']%60)}s")
                            col3.metric("Average Duration", f"{int(analysis['avg_duration']//60)}m {int(analysis['avg_duration']%60)}s")
                            col4.metric("Longest Call", f"{int(analysis['longest_call']//60)}m {int(analysis['longest_call']%60)}s")
                            
                            st.info(f"📱 Most Contacted: **{analysis['most_contacted']}** ({analysis['most_contacted_count']} calls)")
                            
                            # Statistics Table
                            st.subheader("📱 Contact Statistics")
                            st.dataframe(analysis['phone_stats'], use_container_width=True)
                            
                            # Chart
                            st.subheader("📊 Top 10 Contacts")
                            top10 = analysis['phone_stats'].head(10)
                            fig = px.bar(
                                x=top10.index,
                                y=top10['Count'],
                                labels={'x': 'Phone Number', 'y': 'Number of Calls'},
                                title="Top 10 Most Called Numbers"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Download CSV
                            csv = analysis['df'].to_csv(index=False)
                            st.download_button(
                                label="📥 Download Full Report (CSV)",
                                data=csv,
                                file_name="call_records.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error("❌ Failed to analyze records")
                            
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")

# Footer
st.markdown("---")
st.caption("CDR Analysis Pro v2.0 | Built with Streamlit | © 2026")
