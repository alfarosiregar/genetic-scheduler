"""
Genetic Scheduler - Aplikasi Penjadwalan Kuliah
Main application file
"""
import streamlit as st
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_kromosom_data, load_databases
from utils.genetic_algorithm import run_genetic_algorithm
from components.header import apply_custom_css, display_header, display_image
from components.sidebar import render_sidebar
from components.results import (
    display_populasi_awal, 
    display_evaluasi, 
    display_parents, 
    display_offspring
)


# Page config
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)

# Apply styling
apply_custom_css()

# Load data
df_kromosom = load_kromosom_data()
databases = load_databases()

# Initialize session state
if "populasi_data" not in st.session_state:
    st.session_state.populasi_data = {}

# Sidebar
sidebar_data = render_sidebar(databases)

if sidebar_data:
    # Handle add button
    if sidebar_data['button']:
        kode = sidebar_data['kode_manual'] if sidebar_data['kode_manual'] else f"C{len(st.session_state.populasi_data)+1}"
        inputs = sidebar_data['inputs']
        
        st.session_state.populasi_data[kode] = [
            inputs['dosen'], inputs['matkul'], inputs['sks'], inputs['prodi'],
            inputs['hari'], inputs['waktu'], inputs['ruangan'], inputs['blok']
        ]
        st.sidebar.success(f"✅ Data berhasil ditambahkan dengan kode {kode}!")
    
    # Handle reset button
    if sidebar_data['reset_button']:
        st.session_state.populasi_data = {}
        st.rerun()

# Main content
display_header()
display_image()

# Preview data
if df_kromosom is not None:
    with st.expander("📊 Preview Data dari Kromosom"):
        st.dataframe(df_kromosom, use_container_width=True)

if databases is not None:
    with st.expander("📊 Preview Data dari Databases"):
        import pandas as pd
        preview_df = pd.DataFrame({
            'Total Dosen': [len(databases['dosen'])],
            'Total Mata Kuliah': [len(databases['matkul'])],
            'Total Prodi': [len(databases['prodi'])],
        })
        st.dataframe(preview_df, use_container_width=True)

# Display populasi awal
display_populasi_awal(st.session_state.populasi_data)

# Run GA button
if st.button("🚀 Jalankan Algoritma Genetika", type="primary"):
    if len(st.session_state.populasi_data) < 2:
        st.warning("⚠️ Minimal 2 kromosom diperlukan!")
    else:
        results = run_genetic_algorithm(st.session_state.populasi_data)
        
        display_evaluasi(results['populasi'])
        display_parents(results['parent1'], results['parent2'])
        display_offspring(results['anak_list'])
        
        st.success("✅ Algoritma Genetika selesai dijalankan!")