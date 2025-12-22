"""
Page 3: Hasil dan Analisis Lengkap - OPTIMIZED VERSION
Compatible with genetic_algorithm_optimized.py
"""
import streamlit as st
import pandas as pd
import altair as alt
from utils.genetic_algorithm import (
    get_summary_stats, 
    format_kromosom_detail,
    buat_tabel_rekomendasi_jadwal
)

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Results - Genetic Scheduler",
    page_icon="📈",
    layout="wide"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 24px;
    }
    .metric-card p {
        margin: 10px 0 0 0;
        font-size: 16px;
    }
    .success-banner {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: 20px 0;
    }
    .recommendation-table {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ========== TITLE ==========
st.title("📈 Hasil dan Analisis Lengkap")
st.markdown("Analisis detail hasil optimasi Algoritma Genetika")

# ========== CHECK IF RESULTS EXIST ==========
if "ga_results" not in st.session_state:
    st.warning("⚠️ Belum ada hasil algoritma!")
    st.info("➡️ Silakan jalankan algoritma di halaman **Run Algorithm** terlebih dahulu.")
    st.stop()

# ========== LOAD RESULTS ==========
results = st.session_state.ga_results
stats = get_summary_stats(results)

# ========== EXECUTIVE SUMMARY ==========
st.markdown("### 🎯 Ringkasan Eksekutif")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Generasi", 
        results['total_generations'],
        help="Jumlah iterasi evolusi yang dijalankan"
    )

with col2:
    fitness_improvement = float(stats['fitness_improvement'])
    st.metric(
        "Fitness Akhir", 
        f"{stats['final_best_fitness']:.4f}",
        delta=f"+{fitness_improvement:.4f}",
        help="Fitness terbaik dari populasi akhir"
    )

with col3:
    initial_konflik = int(stats['initial_konflik'])
    final_konflik = int(stats['final_konflik'])
    konflik_delta = initial_konflik - final_konflik
    
    st.metric(
        "Konflik Akhir",
        final_konflik,
        delta=-konflik_delta,
        delta_color="inverse",
        help="Jumlah konflik jadwal pada solusi terbaik"
    )

with col4:
    improvement_pct = float(results['improvement']['improvement_percentage'])
    st.metric(
        "Peningkatan", 
        f"{improvement_pct}%",
        help="Persentase peningkatan fitness dari awal"
    )

with col5:
    status = "✅ OPTIMAL" if stats['reached_optimal'] else "⚠️ SUBOPTIMAL"
    st.metric(
        "Status", 
        status,
        help="Status hasil: Optimal = fitness 1.0 & konflik 0"
    )

# Success banner if optimal
if stats['reached_optimal']:
    st.markdown("""
    <div class="success-banner">
        🎉 SELAMAT! Algoritma berhasil menemukan solusi OPTIMAL tanpa konflik! 🎉
    </div>
    """, unsafe_allow_html=True)

# ========== TABEL REKOMENDASI JADWAL ==========
st.markdown("---")
st.markdown("### 📋 Tabel Rekomendasi Jadwal")

# Buat tabel rekomendasi
tabel_rekomendasi = buat_tabel_rekomendasi_jadwal(results)
df_rekomendasi = pd.DataFrame(tabel_rekomendasi)

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📊 Total Jadwal", 
        len(df_rekomendasi),
        help="Jumlah jadwal unik (tanpa duplikasi)"
    )

with col2:
    total_konflik_tabel = int(df_rekomendasi['Konflik'].sum())
    st.metric(
        "⚠️ Total Konflik", 
        total_konflik_tabel,
        help="Total konflik dalam tabel rekomendasi"
    )

with col3:
    avg_fitness_tabel = float(df_rekomendasi['Fitness'].mean())
    st.metric(
        "📈 Avg Fitness", 
        f"{avg_fitness_tabel:.4f}",
        help="Rata-rata fitness jadwal"
    )

with col4:
    jadwal_optimal = int((df_rekomendasi['Konflik'] == 0).sum())
    st.metric(
        "✅ Jadwal Optimal", 
        jadwal_optimal,
        help="Jumlah jadwal tanpa konflik"
    )

# Info box
if total_konflik_tabel == 0:
    st.success("✅ **SEMPURNA!** Semua jadwal tidak memiliki konflik.")
else:
    st.warning(f"⚠️ **Perhatian!** Masih ada {total_konflik_tabel} konflik dalam jadwal.")

# Display table with custom styling
st.markdown("<div class='recommendation-table'>", unsafe_allow_html=True)

# Highlight rows with conflicts
def highlight_konflik(row):
    if row['Konflik'] > 0:
        return ['background-color: #ffcccc'] * len(row)  # Light red
    elif row['Fitness'] >= 0.99:
        return ['background-color: #ccffcc'] * len(row)  # Light green
    return [''] * len(row)

st.dataframe(
    df_rekomendasi.style.apply(highlight_konflik, axis=1).format({
        'Fitness': '{:.4f}'
    }),
    use_container_width=True,
    height=400
)

st.markdown("</div>", unsafe_allow_html=True)

# Legend
col1, col2 = st.columns(2)
with col1:
    st.markdown("🟢 **Hijau:** Jadwal optimal (fitness ≥ 0.99)")
with col2:
    st.markdown("🔴 **Merah:** Ada konflik yang perlu diselesaikan")

# Detail view expander
with st.expander("🔍 Lihat Detail per Jadwal"):
    for idx, row in df_rekomendasi.iterrows():
        st.markdown(f"### 📌 Jadwal #{row['No']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📚 Informasi Dasar**")
            st.write(f"**Dosen:** {row['Dosen']}")
            st.write(f"**Mata Kuliah:** {row['Mata Kuliah']}")
            st.write(f"**Prodi:** {row['Prodi']}")
        
        with col2:
            st.markdown("**📅 Jadwal Perkuliahan**")
            st.write(f"**SKS:** {row['SKS']}")
            st.write(f"**Hari:** {row['Hari']}")
            st.write(f"**Waktu:** {row['Waktu']}")
            st.write(f"**Ruangan:** {row['Ruangan']}")
        
        with col3:
            st.markdown("**📊 Metrik**")
            st.write(f"**Fitness:** {row['Fitness']:.4f}")
            st.write(f"**Konflik:** {row['Konflik']}")
            
            if row['Konflik'] == 0:
                st.success("✅ Tidak ada konflik")
            else:
                st.error(f"❌ Ada {row['Konflik']} konflik")
        
        st.markdown("---")

# ========== EVOLUTION VISUALIZATION ==========
st.markdown("---")
st.markdown("### 📊 Visualisasi Evolusi")

tab1, tab2 = st.tabs(["📈 Fitness Evolution", "🎯 Konflik Progress"])

with tab1:
    st.markdown("**Evolusi Fitness per Generasi**")
    
    chart_data = pd.DataFrame({
        'Generasi': results['history']['generations'],
        'Best Fitness': results['history']['best_fitness'],
        'Average Fitness': results['history']['avg_fitness']
    })
    
    line_chart = alt.Chart(chart_data.melt('Generasi', var_name='Type', value_name='Fitness')).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill="white")
    ).encode(
        x=alt.X('Generasi:Q', title='Generasi', axis=alt.Axis(format='d')),
        y=alt.Y('Fitness:Q', title='Fitness Score', scale=alt.Scale(domain=[0, 1.05])),
        color=alt.Color('Type:N', 
                       legend=alt.Legend(title="Tipe Fitness"),
                       scale=alt.Scale(domain=['Best Fitness', 'Average Fitness'],
                                     range=['#667eea', '#38ef7d'])),
        strokeWidth=alt.value(3),
        tooltip=[
            alt.Tooltip('Generasi:Q', title='Generasi'),
            alt.Tooltip('Type:N', title='Tipe'),
            alt.Tooltip('Fitness:Q', title='Fitness', format='.4f')
        ]
    ).properties(
        width=700,
        height=400
    ).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

with tab2:
    st.markdown("**Pengurangan Konflik per Generasi**")
    
    konflik_data = pd.DataFrame({
        'Generasi': results['history']['generations'],
        'Jumlah Konflik': results['history']['best_konflik']
    })
    
    konflik_chart = alt.Chart(konflik_data).mark_area(
        line={'color': 'darkred'},
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='white', offset=0),
                alt.GradientStop(color='red', offset=1)
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        x=alt.X('Generasi:Q', title='Generasi', axis=alt.Axis(format='d')),
        y=alt.Y('Jumlah Konflik:Q', title='Jumlah Konflik'),
        tooltip=[
            alt.Tooltip('Generasi:Q', title='Generasi'),
            alt.Tooltip('Jumlah Konflik:Q', title='Konflik')
        ]
    ).properties(
        width=700,
        height=400
    ).interactive()
    
    st.altair_chart(konflik_chart, use_container_width=True)
    
    konflik_reduction = int(stats['initial_konflik'] - stats['final_konflik'])
    if konflik_reduction > 0:
        st.success(f"✅ Berhasil mengurangi {konflik_reduction} konflik!")
    elif int(stats['final_konflik']) == 0:
        st.success("✅ Tidak ada konflik sejak awal!")

# ========== ADVANCED DATA (EXPANDER) ==========
with st.expander("📊 Data Lanjutan: Progress & Populasi"):
    
    # Generation Progress Table
    st.markdown("#### 📋 Progress per Generasi")
    
    progress_data = []
    for i, gen in enumerate(results['history']['generations']):
        progress_data.append({
            'Generasi': gen,
            'Best Fitness': results['history']['best_fitness'][i],
            'Avg Fitness': results['history']['avg_fitness'][i],
            'Worst Fitness': results['history']['worst_fitness'][i],
            'Best Konflik': results['history']['best_konflik'][i],
            'Improvement': results['history']['best_fitness'][i] - results['history']['best_fitness'][0] if i > 0 else 0
        })
    
    df_progress = pd.DataFrame(progress_data)
    
    def highlight_best(row):
        if row['Best Fitness'] == df_progress['Best Fitness'].max():
            return ['background-color: #90EE90'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df_progress.style.apply(highlight_best, axis=1).format({
            'Best Fitness': '{:.4f}',
            'Avg Fitness': '{:.4f}',
            'Worst Fitness': '{:.4f}',
            'Improvement': '{:.4f}'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Detailed Comparison
    st.markdown("#### 🔄 Perbandingan Populasi Awal vs Akhir")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔴 Populasi Awal (Generasi 0)**")
        df_awal = pd.DataFrame([
            format_kromosom_detail(k) for k in results['populasi_awal']
        ])
        st.dataframe(df_awal[['Kode', 'Dosen', 'Mata Kuliah', 'Hari', 'Waktu', 'Fitness', 'Konflik']], use_container_width=True, height=300)
    
    with col2:
        st.markdown(f"**🟢 Populasi Akhir (Generasi {results['total_generations']})**")
        df_akhir = pd.DataFrame([
            format_kromosom_detail(k) for k in results['populasi_akhir']
        ])
        st.dataframe(df_akhir[['Kode', 'Dosen', 'Mata Kuliah', 'Hari', 'Waktu', 'Fitness', 'Konflik']], use_container_width=True, height=300)

# ========== RECOMMENDATIONS ==========
st.markdown("---")
st.markdown("### 💡 Rekomendasi")

if stats['reached_optimal']:
    st.success("""
    ✅ **Hasil Optimal Tercapai!**
    
    Algoritma telah menemukan solusi terbaik tanpa konflik. Jadwal ini siap digunakan!
    """)
else:
    final_konflik_display = int(stats['final_konflik'])
    current_gen = results['total_generations']
    st.info(f"""
    💡 **Tips untuk Meningkatkan Hasil:**
    
    - ✅ Tingkatkan **Jumlah Generasi** menjadi {current_gen * 2} atau lebih
    - ✅ Coba **Mutation Rate** yang lebih tinggi (15-20%)
    - ✅ Jalankan algoritma beberapa kali dan pilih hasil terbaik
    
    **Current Status:** Masih ada {final_konflik_display} konflik yang perlu diselesaikan.
    """)

# ========== DOWNLOAD SECTION ==========
st.markdown("---")
st.markdown("### 💾 Download Hasil")

col1, col2  = st.columns(2)

with col1:
    # Download tabel rekomendasi
    tabel_csv = df_rekomendasi.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Tabel Rekomendasi",
        data=tabel_csv,
        file_name="tabel_rekomendasi_jadwal.csv",
        mime="text/csv",
        use_container_width=True,
        help="Download tabel rekomendasi dalam format CSV"
    )
with col2:
    # Download progress history
    progress_csv = df_progress.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Progress History",
        data=progress_csv,
        file_name="evolution_progress.csv",
        mime="text/csv",
        use_container_width=True,
        help="Download riwayat evolusi per generasi"
    )

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📊 Genetic Scheduler - Results</p>
</div>
""", unsafe_allow_html=True)