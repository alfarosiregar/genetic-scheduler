"""
Custom Sidebar Component
"""
import streamlit as st


def render_input_sidebar(databases):
    st.sidebar.title("➕ Tambah Data Jadwal")

    if databases is not None:
        with st.sidebar.form("input_form"):
            dosen = st.selectbox("Nama Dosen", options=databases['dosen'])
            matkul = st.selectbox("Mata Kuliah", options=databases['matkul'])
            prodi = st.selectbox("Program Studi", options=databases['prodi'])

            submitted = st.form_submit_button("➕ Tambah Data")
            
            if submitted:
                kode = f"C{len(st.session_state.populasi_data)+1}"
                st.session_state.populasi_data[kode] = [
                    dosen, matkul, prodi,
                ]
                st.success(f"✅ Data berhasil ditambahkan dengan kode {kode}!")
                return True
    
    return False