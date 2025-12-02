"""
Page 2: Jalankan Algoritma Genetika
"""
import streamlit as st
import pandas as pd
from utils.genetic_algorithm import run_genetic_algorithm
from components.results import display_evaluasi, display_parents, display_offspring

st.set_page_config(
    page_title="Run Algorithm - Genetic Scheduler",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Jalankan Algoritma Genetika")

# Check if data exists
if "populasi_data" not in st.session_state or len(st.session_state.populasi_data) == 0:
    st.warning("⚠️ Belum ada data jadwal!")
    st.info("➡️ Silakan tambahkan data di halaman **Input Data** terlebih dahulu.")
    st.stop()

# Display current data
st.markdown("### 📋 Data Jadwal yang Akan Dioptimasi")
df = pd.DataFrame.from_dict(
    st.session_state.populasi_data,
    orient="index",
    columns=["Dosen", "Matkul", "SKS", "Prodi", "Hari", "Waktu", "Ruangan", "Blok"]
)
st.dataframe(df, use_container_width=True)

# Algorithm parameters
st.markdown("### ⚙️ Parameter Algoritma")

col1, col2, col3 = st.columns(3)
with col1:
    generations = st.number_input("Jumlah Generasi", min_value=1, max_value=100, value=10)
with col2:
    population_size = st.number_input("Ukuran Populasi", min_value=2, max_value=100, value=len(st.session_state.populasi_data))
with col3:
    mutation_rate = st.slider("Mutation Rate", 0.0, 1.0, 0.1)

# Run button
if st.button("🚀 Jalankan Algoritma", type="primary", use_container_width=True):
    if len(st.session_state.populasi_data) < 2:
        st.error("⚠️ Minimal 2 jadwal diperlukan!")
    else:
        with st.spinner("🔄 Menjalankan algoritma genetika..."):
            # Run algorithm
            results = run_genetic_algorithm(st.session_state.populasi_data)
            
            # Save results to session state
            st.session_state.ga_results = results
            
            # Display results
            st.success("✅ Algoritma selesai dijalankan!")
            
            display_evaluasi(results['populasi'])
            display_parents(results['parent1'], results['parent2'])
            display_offspring(results['anak_list'])
            
            # Navigation hint
            st.markdown("---")
            st.info("➡️ **Langkah Selanjutnya:** Lihat analisis lengkap di halaman **Results**!")