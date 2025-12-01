"""Sidebar untuk input data jadwal"""
import streamlit as st


def render_sidebar(databases):
    """Render sidebar dengan form input"""
    st.sidebar.title("🧬 Input Data Jadwal")
    
    if databases is None:
        st.sidebar.error("⚠️ Tidak dapat memuat data dari file Excel")
        return None
    
    # Input fields
    inputs = {}
    inputs['dosen'] = st.sidebar.selectbox("Nama Dosen", options=databases['dosen'])
    inputs['matkul'] = st.sidebar.selectbox("Mata Kuliah", options=databases['matkul'])
    inputs['sks'] = st.sidebar.selectbox("Jumlah SKS", options=databases['sks'])
    inputs['prodi'] = st.sidebar.selectbox("Program Studi", options=databases['prodi'])
    inputs['kelas'] = st.sidebar.selectbox("Kelas", options=databases['kelas'])
    inputs['hari'] = st.sidebar.selectbox("Hari", options=databases['hari'])
    inputs['waktu'] = st.sidebar.selectbox("Waktu", options=databases['waktu'])
    inputs['ruangan'] = st.sidebar.selectbox("Ruangan", options=databases['ruangan'])
    inputs['blok'] = st.sidebar.selectbox("Blok (opsional)", options=databases['blok'])
    
    # Manual kode kromosom
    st.sidebar.markdown("---")
    input_kromosom = st.sidebar.checkbox("Masukkan Kode Kromosom secara manual?")
    kode_manual = None
    if input_kromosom:
        kode_manual = st.sidebar.text_input("Kode Kromosom (misal: C1)")
    
    # Tombol tambah
    button = st.sidebar.button("➕ Tambah ke Populasi Awal")
    
    # Tombol reset
    st.sidebar.markdown("---")
    reset_button = st.sidebar.button("🔄 Reset Populasi", type="secondary")
    
    return {
        'inputs': inputs,
        'kode_manual': kode_manual,
        'button': button,
        'reset_button': reset_button
    }