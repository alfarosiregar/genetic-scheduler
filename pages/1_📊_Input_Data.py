"""
Page 1: Input Data Jadwal
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_databases
from components.header import apply_custom_css

# Page config
st.set_page_config(
    page_title="Input Data - Genetic Scheduler",
    page_icon="📊",
    layout="wide"
)

apply_custom_css()

st.title("📊 Input Data Jadwal")
st.markdown("Tambahkan data jadwal kuliah yang akan dioptimasi")

# Initialize session state
if "populasi_data" not in st.session_state:
    st.session_state.populasi_data = {}

# Load databases
databases = load_databases()

# Sidebar input form
st.sidebar.title("➕ Tambah Data Jadwal")

if databases is not None:
    with st.sidebar.form("input_form"):
        dosen = st.selectbox("Nama Dosen", options=databases['dosen'])
        matkul = st.selectbox("Mata Kuliah", options=databases['matkul'])
        sks = st.selectbox("SKS", options=databases['sks'])
        prodi = st.selectbox("Program Studi", options=databases['prodi'])
        kelas = st.selectbox("Kelas", options=databases['kelas'])
        hari = st.selectbox("Hari", options=databases['hari'])
        waktu = st.selectbox("Waktu", options=databases['waktu'])
        ruangan = st.selectbox("Ruangan", options=databases['ruangan'])
        blok = st.selectbox("Blok", options=databases['blok'])
        
        submitted = st.form_submit_button("➕ Tambah Data")
        
        if submitted:
            kode = f"C{len(st.session_state.populasi_data)+1}"
            st.session_state.populasi_data[kode] = [
                dosen, matkul, sks, prodi, hari, waktu, ruangan, blok
            ]
            st.success(f"✅ Data berhasil ditambahkan dengan kode {kode}!")
            st.rerun()

# Display data
st.markdown("### 📌 Data Jadwal yang Sudah Ditambahkan")

if len(st.session_state.populasi_data) == 0:
    st.info("💡 Belum ada data. Silakan tambahkan dari sidebar.")
else:
    df = pd.DataFrame.from_dict(
        st.session_state.populasi_data,
        orient="index",
        columns=["Dosen", "Matkul", "SKS", "Prodi", "Hari", "Waktu", "Ruangan", "Blok"]
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
    st.markdown("### 📊 Statistik")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jadwal", len(st.session_state.populasi_data))
    with col2:
        st.metric("Dosen Unik", df['Dosen'].nunique())
    with col3:
        st.metric("Ruangan Unik", df['Ruangan'].nunique())
    with col4:
        st.metric("Hari Unik", df['Hari'].nunique())

# Navigation hint
st.markdown("---")
st.info("➡️ **Langkah Selanjutnya:** Pergi ke halaman **Run Algorithm** untuk optimasi jadwal!")