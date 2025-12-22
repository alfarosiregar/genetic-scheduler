"""
Page 2: Jalankan Algoritma
"""
import streamlit as st
import pandas as pd
from utils.genetic_algorithm import run_genetic_algorithm, get_summary_stats, format_kromosom_detail
from utils.data_loader import load_databases

st.set_page_config(
    page_title="Run Algorithm - Genetic Scheduler",
    page_icon="🧬",
    layout="wide"
)

# ========== INITIALIZE SESSION STATE ==========
if 'ga_config' not in st.session_state:
    st.session_state.ga_config = {
        'generations': 10,
        'mutation_rate': 0.15,
        'elite_size': 2
    }

st.title("🧬 Jalankan Algoritma Genetika")
st.markdown("Optimasi jadwal menggunakan Algoritma Genetika dengan multi-generasi iterasi")

# Check if data exists
if "populasi_data" not in st.session_state or len(st.session_state.populasi_data) == 0:
    st.warning("⚠️ Belum ada data jadwal!")
    st.info("➡️ Silakan tambahkan data di halaman **Input Data** terlebih dahulu.")
    st.stop()

# Load databases untuk mutasi
databases = load_databases()

# Display current data
st.markdown("### 📋 Data Jadwal yang Akan Dioptimasi")
df = pd.DataFrame.from_dict(
    st.session_state.populasi_data,
    orient="index",
    columns=["Dosen", "Matkul", "Prodi"]
)
st.dataframe(df, use_container_width=True)

# ========== ALGORITHM PARAMETERS ==========
st.markdown("### ⚙️ Parameter Algoritma Genetika")

col1, col2, col3, col4 = st.columns(4)

with col1:
    generations = st.number_input(
        "Jumlah Generasi", 
        min_value=1, 
        max_value=100, 
        value=st.session_state.ga_config['generations'],
        help="Jumlah iterasi evolusi (semakin banyak semakin optimal)"
    )
    st.session_state.ga_config['generations'] = generations

with col2:
    mutation_rate = st.slider(
        "Mutation Rate", 
        0.0, 
        1.0, 
        st.session_state.ga_config['mutation_rate'],
        help="Probabilitas mutasi (rekomendasi: 0.15)"
    )
    st.session_state.ga_config['mutation_rate'] = mutation_rate

with col3:
    elite_size = st.number_input(
        "Elite Size", 
        min_value=1, 
        max_value=len(st.session_state.populasi_data), 
        value=st.session_state.ga_config['elite_size'],
        help="Jumlah individu terbaik yang dipertahankan"
    )
    st.session_state.ga_config['elite_size'] = elite_size

with col4:
    st.metric("Ukuran Populasi", len(st.session_state.populasi_data))

# Info box
st.info("""
**📚 Penjelasan Parameter:**
- **Jumlah Generasi**: Berapa kali proses evolusi diulang. Semakin banyak = hasil lebih optimal.
- **Mutation Rate**: Peluang gen berubah secara acak. Rekomendasi: 0.15-0.20.
- **Elite Size**: Jumlah jadwal terbaik yang otomatis lolos ke generasi berikutnya.
""")

# Recommended settings
with st.expander("💡 Pengaturan Rekomendasi"):
    st.markdown("#### Berdasarkan Ukuran Dataset:")
    
    data_size = len(st.session_state.populasi_data)
    
    if data_size < 10:
        st.success("""
        **Dataset Kecil (< 10 jadwal):**
        - Generasi: 10
        - Mutation Rate: 0.15
        - Elite Size: 2
        """)
    elif data_size < 50:
        st.info("""
        **Dataset Sedang (10-50 jadwal):**
        - Generasi: 30
        - Mutation Rate: 0.15
        - Elite Size: 3
        """)
    else:
        st.warning("""
        **Dataset Besar (> 50 jadwal):**
        - Generasi: 50
        - Mutation Rate: 0.20
        - Elite Size: 5
        """)

# ========== RUN BUTTON ==========
if st.button("🚀 Jalankan Algoritma Genetika", type="primary", use_container_width=True):
    if len(st.session_state.populasi_data) < 2:
        st.error("⚠️ Minimal 2 kromosom diperlukan!")
    else:
        # Progress indicator
        with st.spinner('🔄 Menjalankan Algoritma Genetika...'):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📦 Mempersiapkan populasi...")
            progress_bar.progress(20)
            
            status_text.text("🧬 Evolusi sedang berlangsung...")
            progress_bar.progress(40)
            
            # Run algorithm
            try:
                results = run_genetic_algorithm(
                    st.session_state.populasi_data,
                    databases,
                    generations=generations,
                    mutation_rate=mutation_rate,
                    elite_size=elite_size
                )
                
                progress_bar.progress(90)
                status_text.text("💾 Menyimpan hasil...")
                
                # Save results to session state
                st.session_state.ga_results = results
                
                progress_bar.progress(100)
                status_text.text("✅ Selesai!")
                
                st.success(f"✅ Algoritma berhasil dijalankan! ({results['total_generations']} generasi)")
                
            except Exception as e:
                st.error(f"❌ Error saat menjalankan algoritma: {str(e)}")
                st.stop()
        
        st.rerun()

# ========== DISPLAY RESULTS FROM SESSION STATE ==========
if "ga_results" in st.session_state and st.session_state.ga_results is not None:
    
    st.markdown("---")
    
    results = st.session_state.ga_results
    stats = get_summary_stats(results)
    
    st.markdown("### 📊 Ringkasan Hasil")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Fitness Awal", 
            f"{stats['initial_best_fitness']:.4f}",
            help="Fitness terbaik dari populasi awal"
        )
    
    with col2:
        st.metric(
            "Fitness Akhir", 
            f"{stats['final_best_fitness']:.4f}",
            delta=f"+{stats['fitness_improvement']:.4f}",
            delta_color="normal",
            help="Fitness terbaik setelah evolusi"
        )
    
    with col3:
        st.metric(
            "Konflik Awal",
            stats['initial_konflik'],
            help="Jumlah konflik di populasi awal"
        )
    
    with col4:
        st.metric(
            "Konflik Akhir",
            stats['final_konflik'],
            delta=-(stats['initial_konflik'] - stats['final_konflik']),
            delta_color="inverse",
            help="Jumlah konflik setelah optimasi"
        )
    
    # Status indicator
    if stats['reached_optimal']:
        st.success("🎉 **OPTIMAL!** Fitness = 1.0 dengan 0 konflik tercapai!")
    else:
        improvement_pct = results['improvement']['improvement_percentage']
        st.info(f"📈 **Peningkatan Fitness: {improvement_pct}%** - Masih ada {stats['final_konflik']} konflik")
    
    # ========== EVOLUTION CHART ==========
    st.markdown("### 📈 Grafik Evolusi Fitness")
    
    chart_data = pd.DataFrame({
        'Generasi': results['history']['generations'],
        'Best Fitness': results['history']['best_fitness'],
        'Average Fitness': results['history']['avg_fitness']
    })
    
    st.line_chart(chart_data.set_index('Generasi'))
    
    # ========== COMPARISON TABLE ==========
    with st.expander("🔍 Lihat Perbandingan Populasi Awal vs Akhir"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Populasi Awal (Generasi 0)**")
            df_awal = pd.DataFrame([
                format_kromosom_detail(k) for k in results['populasi_awal']
            ])
            st.dataframe(df_awal[['Kode', 'Dosen', 'Mata Kuliah', 'Fitness', 'Konflik']], use_container_width=True)
        
        with col2:
            st.markdown(f"**✨ Populasi Akhir (Generasi {results['total_generations']})**")
            df_akhir = pd.DataFrame([
                format_kromosom_detail(k) for k in results['populasi_akhir']
            ])
            st.dataframe(df_akhir[['Kode', 'Dosen', 'Mata Kuliah', 'Fitness', 'Konflik']], use_container_width=True)
    
    # Navigation hint
    st.markdown("---")
    st.info("➡️ **Langkah Selanjutnya:** Lihat analisis detail di halaman **Results**!")
    
    if st.button("📈 Buka Halaman Results", use_container_width=True):
        st.switch_page("pages/3_📈_Results.py")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🧬 Genetic Scheduler - Run Algorithm</p>
</div>
""", unsafe_allow_html=True)