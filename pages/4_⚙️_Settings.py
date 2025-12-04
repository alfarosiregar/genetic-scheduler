"""
Page 4: Pengaturan
"""
import streamlit as st
from components.header import display_image_on_settings

st.set_page_config(
    page_title="Settings - Genetic Scheduler",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Pengaturan Aplikasi")
display_image_on_settings()

st.markdown("""---""")

st.markdown("### 🎨 Tema")
theme = st.selectbox("Pilih Tema", ["Light", "Dark", "Auto"])

st.markdown("### 🔧 Konfigurasi Algoritma")

col1, col2 = st.columns(2)
with col1:
    st.number_input("Default Generations", min_value=1, max_value=1000, value=10)
    st.number_input("Default Population Size", min_value=2, max_value=1000, value=20)

with col2:
    st.slider("Default Mutation Rate", 0.0, 1.0, 0.1)
    st.slider("Default Crossover Rate", 0.0, 1.0, 0.8)

st.markdown("""---""")

st.markdown("### 📁 Data Management")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.clear()
        st.success("✅ Semua data telah dihapus!")

with col2:
    if st.button("💾 Export Settings"):
        st.info("Feature coming soon!")

with col3:
    if st.button("📥 Import Settings"):
        st.info("Feature coming soon!")

st.markdown("""---""")

st.markdown("### ℹ️ Informasi Aplikasi")
st.info("""
**Genetic Scheduler v1.0**

Aplikasi penjadwalan kuliah menggunakan Algoritma Genetika.
- Technology: Streamlit + Python
""")