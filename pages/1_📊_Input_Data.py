"""
Page 1: Input Data Jadwal
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_databases
from components.header import apply_custom_css, display_image_on_input
from components.sidebar import render_input_sidebar

# Page config
st.set_page_config(
    page_title="Input Data - Genetic Scheduler",
    page_icon="📊",
    layout="wide"
)

apply_custom_css()

st.title("📊 Input Data Jadwal")
st.markdown("Tambahkan data jadwal kuliah yang akan dioptimasi")
display_image_on_input()
st.markdown("""---""")

# Initialize session state
if "populasi_data" not in st.session_state:
    st.session_state.populasi_data = {}

# Load databases
databases = load_databases()

# Sidebar input form
submitted = render_input_sidebar(databases)
if submitted:
    st.rerun()

# Upload data from Excel
st.markdown("### 📁 Upload Data dari Excel")
uploaded_file = st.file_uploader("Pilih file Excel (.xlsx) dengan kolom: **Dosen**, **Matkul**, **Prodi**", type=["xlsx", "xls"])
if uploaded_file is not None:
    try:
        df_upload = pd.read_excel(uploaded_file)
        required_cols = ["Dosen", "Matkul", "Prodi"]
        
        if all(col in df_upload.columns for col in required_cols):
            if st.button("➕ Tambahkan Data dari File", type="primary"):
                added_count = 0
                for _, row in df_upload.iterrows():
                    kode = f"C{len(st.session_state.populasi_data)+1}"
                    st.session_state.populasi_data[kode] = [
                        str(row["Dosen"]), str(row["Matkul"]), str(row["Prodi"])
                    ]
                    added_count += 1
                st.success(f"✅ Berhasil menambahkan {added_count} data jadwal!")
                st.rerun()
        else:
            missing = [col for col in required_cols if col not in df_upload.columns]
            st.error(f"❌ File tidak valid! Kolom yang wajib ada namun tidak ditemukan: {', '.join(missing)}")
    except Exception as e:
        st.error(f"❌ Error membaca file: {e}")

st.markdown("""---""")

# Display data
st.markdown("### 📌 Data Jadwal yang Sudah Ditambahkan")

if len(st.session_state.populasi_data) == 0:
    st.info("💡 Belum ada data. Silakan tambahkan dari sidebar.")
else:
    df = pd.DataFrame.from_dict(
        st.session_state.populasi_data,
        orient="index",
        columns=["Dosen", "Matkul", "Prodi"]
    )
    
    st.dataframe(df, use_container_width=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("🗑️ Hapus Semua", type="secondary"):
            st.session_state.populasi_data = {}
            st.rerun()
    
    with col2:
        csv = df.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name="jadwal_data.csv",
            mime="text/csv"
        )
    
    # Stats
    st.markdown("""---""")
    st.markdown("### 📊 Statistik")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jadwal", len(st.session_state.populasi_data))
    with col2:
        st.metric("Dosen Unik", df['Dosen'].nunique())
    with col3:
        st.metric("Mata Kuliah Unik", df['Matkul'].nunique())
    with col4:
        st.metric("Prodi Unik", df['Prodi'].nunique())

# Navigation hint
st.markdown("---")
st.info("➡️ **Jika sudah Input Data,** Selanjutnya: Pergi ke halaman **Run Algorithm** untuk optimasi jadwal!")
if st.button("🧬 Buka Halaman Run Algorithm", use_container_width=True):
    st.switch_page("pages/2_🧬_Run_Algorithm.py")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🧬 Genetic Scheduler - Input Data</p>
</div>
""", unsafe_allow_html=True)