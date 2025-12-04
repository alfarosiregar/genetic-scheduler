"""
Page 3: Hasil dan Analisis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from components.header import display_image_on_results

st.set_page_config(
    page_title="Results - Genetic Scheduler",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Hasil dan Analisis")
display_image_on_results()
st.markdown("""---""")

# Check if results exist
if "ga_results" not in st.session_state:
    st.warning("⚠️ Belum ada hasil algoritma!")
    st.info("➡️ Silakan jalankan algoritma di halaman **Run Algorithm** terlebih dahulu.")
    st.stop()

results = st.session_state.ga_results

# Best solution
st.markdown("### 🏆 Solusi Terbaik")

best = max(results['anak_list'], key=lambda x: x['fitness'])

col1, col2 = st.columns(2)
with col1:
    st.metric("Kode", best['kode'])
    st.metric("Fitness", best['fitness'])
    st.metric("Konflik", best['konflik'])

with col2:
    st.markdown("**Detail:**")
    st.write(f"- Dosen: {best['data'][0]}")
    st.write(f"- Matkul: {best['data'][1]}")
    st.write(f"- Hari: {best['data'][4]}")
    st.write(f"- Waktu: {best['data'][5]}")
    st.write(f"- Ruangan: {best['data'][6]}")

st.markdown("""---""")

# Comparison chart
st.markdown("### 📊 Perbandingan Fitness")

fitness_data = []
for p in results['populasi']:
    fitness_data.append({'Kode': p['kode'], 'Fitness': p['fitness'], 'Type': 'Populasi Awal'})
for a in results['anak_list']:
    fitness_data.append({'Kode': a['kode'], 'Fitness': a['fitness'], 'Type': 'Offspring'})

df_fitness = pd.DataFrame(fitness_data)

fig = px.bar(df_fitness, x='Kode', y='Fitness', color='Type', 
             title='Perbandingan Fitness Score',
             barmode='group')
st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

# Download results
st.markdown("### 💾 Download Hasil")

col1, col2 = st.columns(2)
with col1:
    csv = pd.DataFrame([best]).to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Best Solution (CSV)",
        data=csv,
        file_name="best_solution.csv",
        mime="text/csv"
    )

with col2:
    all_csv = df_fitness.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download All Results (CSV)",
        data=all_csv,
        file_name="all_results.csv",
        mime="text/csv"
    )