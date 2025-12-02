"""
Genetic Scheduler - Homepage
"""
import streamlit as st
from components.header import apply_custom_css, display_header, display_image

# Page config
st.set_page_config(
    page_title="Genetic Scheduler",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_custom_css()

# Header
display_header()
display_image()

# Welcome content
st.markdown("""
## 👋 Selamat Datang di Genetic Scheduler!

Aplikasi ini membantu Anda membuat jadwal kuliah optimal menggunakan **Algoritma Genetika**.

### 🚀 Fitur Utama:

1. **📊 Input Data** - Tambahkan data jadwal kuliah
2. **🧬 Run Algorithm** - Jalankan algoritma genetika untuk optimasi
3. **📈 Results** - Lihat hasil penjadwalan terbaik
4. **⚙️ Settings** - Atur konfigurasi aplikasi

### 📖 Cara Menggunakan:

1. Pilih menu di **sidebar kiri** ⬅️
2. Mulai dari **Input Data** untuk menambahkan jadwal
3. Jalankan **Algorithm** untuk optimasi
4. Lihat **Results** untuk melihat jadwal terbaik

---

**💡 Tips:** Minimal tambahkan 2 jadwal sebelum menjalankan algoritma!
""")

# Quick stats
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📚 Total Dosen", "84")
    
with col2:
    st.metric("📖 Total Mata Kuliah", "113")
    
with col3:
    st.metric("🏫 Total Prodi", "18")

# Footer
st.markdown("---")
st.markdown("<center>🧬 Genetic Scheduler v1.0 | Dibuat dengan ❤️ menggunakan Streamlit</center>", unsafe_allow_html=True)