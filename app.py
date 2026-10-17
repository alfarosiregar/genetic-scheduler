"""
Genetic Scheduler - Homepage Dashboard
"""
import importlib
import pandas as pd
import streamlit as st
from config.settings import APP_IMAGE_PATH
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 6:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from utils.data_loader import load_kromosom_data, load_databases

# Page config
st.set_page_config(
    page_title="Genetic Scheduler - Beranda",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "populasi_data" not in st.session_state:
    st.session_state.populasi_data = {}

# Hero Banner
render_page_hero(
    title="Genetic Scheduler",
    subtitle=(
        "Platform cerdas penyusunan dan optimasi jadwal perkuliahan berbasis Algoritma Genetika. "
        "Mendeteksi bentrok ruangan & dosen secara otomatis hingga mencapai jadwal optimal bebas konflik."
    ),
    badge="🧬 Evolutionary Timetable Optimizer",
    image_path=APP_IMAGE_PATH,
    active_step=0,
)

# Load Master Data
df_kromosom = load_kromosom_data()
databases = load_databases()

# Master Database KPI Metrics
st.markdown('<div class="gs-section-title">🏛️ Ringkasan Master Database Perkuliahan</div>', unsafe_allow_html=True)
n_dosen = len(databases["dosen"]) if databases else 0
n_matkul = len(databases["matkul"]) if databases else 0
n_prodi = len(databases["prodi"]) if databases else 0
n_kelas = len(databases["kelas"]) if databases else 0
n_ruangan = len(databases["ruangan"]) if databases else 0
n_waktu = len(databases["waktu"]) if databases else 0

st.markdown(
    f"""
    <div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; align-items: stretch; margin-bottom: 0.5rem;">
        <div class="gs-card" style="padding: 16px 18px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">👨‍🏫 Dosen</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_dosen}</div>
        </div>
        <div class="gs-card" style="padding: 16px 18px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">📘 Mata Kuliah</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_matkul}</div>
        </div>
        <div class="gs-card" style="padding: 16px 18px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">🎓 Program Studi</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_prodi}</div>
        </div>
        <div class="gs-card" style="padding: 16px 16px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">👥 Kelas</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_kelas}</div>
        </div>
        <div class="gs-card" style="padding: 16px 18px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">🏢 Ruangan</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_ruangan}</div>
        </div>
        <div class="gs-card" style="padding: 16px 18px; border-radius: 14px; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 4px;">⏰ Slot Waktu</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #0F172A; line-height: normal;">{n_waktu}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Feature & Workflow Cards
st.markdown('<div class="gs-section-title">🚀 Alur Kerja & Keunggulan Sistem</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; align-items: stretch;">
        <div class="gs-card" style="display: flex; flex-direction: column; height: 100%; box-sizing: border-box;">
            <div class="gs-card-icon">📊</div>
            <h4>1. Multi-Mode Input</h4>
            <p style="flex: 1;">Input penugasan kuliah secara manual, unggah dari file Excel (.xlsx), atau muat sampel langsung dari database referensi.</p>
        </div>
        <div class="gs-card" style="display: flex; flex-direction: column; height: 100%; box-sizing: border-box;">
            <div class="gs-card-icon">🧬</div>
            <h4>2. Evolusi Cerdas</h4>
            <p style="flex: 1;">Seleksi turnamen, one-cut-point crossover pada gen jadwal, mutasi terarah, dan contextual niche elitism yang monoton konvergen.</p>
        </div>
        <div class="gs-card" style="display: flex; flex-direction: column; height: 100%; box-sizing: border-box;">
            <div class="gs-card-icon">⏱️</div>
            <h4>3. Deteksi Irisan Waktu</h4>
            <p style="flex: 1;">Mendeteksi bentrok rentang menit secara presisi (termasuk tumpang tindih parsial) untuk ruangan maupun dosen pengajar.</p>
        </div>
        <div class="gs-card" style="display: flex; flex-direction: column; height: 100%; box-sizing: border-box;">
            <div class="gs-card-icon">📈</div>
            <h4>4. Analitik & Kalender</h4>
            <p style="flex: 1;">Visualisasi kurva evolusi fitness, matriks jadwal mingguan per hari, indikator warna konflik, serta ekspor ke CSV/Excel.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# Master Database Explorer Tabs
st.markdown('<div class="gs-section-title">🔍 Eksplorasi Data Referensi</div>', unsafe_allow_html=True)
tab_db, tab_krom = st.tabs(["📚 Kategori Master (Databases.xlsx)", "🧬 Dataset Referensi (Kromosom.xlsx)"])

with tab_db:
    if databases is not None:
        cat_col1, cat_col2 = st.columns([1, 2])
        with cat_col1:
            kategori_pilihan = st.selectbox(
                "Pilih Kategori Master Data",
                options=["dosen", "matkul", "prodi", "kelas", "hari", "waktu", "ruangan", "sks"],
                format_func=lambda k: {
                    "dosen": f"👨‍🏫 Daftar Dosen ({len(databases['dosen'])})",
                    "matkul": f"📘 Mata Kuliah ({len(databases['matkul'])})",
                    "prodi": f"🎓 Program Studi ({len(databases['prodi'])})",
                    "kelas": f"👥 Kelas ({len(databases['kelas'])})",
                    "hari": f"📅 Hari Perkuliahan ({len(databases['hari'])})",
                    "waktu": f"⏰ Slot Waktu ({len(databases['waktu'])})",
                    "ruangan": f"🏢 Ruangan Kuliah ({len(databases['ruangan'])})",
                    "sks": f"🔢 Opsi SKS ({len(databases['sks'])})",
                }[k],
            )
            summary_df = pd.DataFrame(
                {
                    "Kategori": ["Dosen", "Mata Kuliah", "Prodi", "Kelas", "Hari", "Slot Waktu", "Ruangan"],
                    "Jumlah Entitas Unik": [
                        len(databases["dosen"]),
                        len(databases["matkul"]),
                        len(databases["prodi"]),
                        len(databases["kelas"]),
                        len(databases["hari"]),
                        len(databases["waktu"]),
                        len(databases["ruangan"]),
                    ],
                }
            )
            st.dataframe(summary_df, width="stretch", hide_index=True)
        with cat_col2:
            df_kat = pd.DataFrame(
                {
                    "No": range(1, len(databases[kategori_pilihan]) + 1),
                    f"Nilai ({kategori_pilihan.upper()})": databases[kategori_pilihan],
                }
            )
            st.dataframe(df_kat, width="stretch", height=370, hide_index=True)

with tab_krom:
    if df_kromosom is not None:
        st.caption(f"Menampilkan {len(df_kromosom):,} baris jadwal referensi dari `mnt/db/Kromosom.xlsx`.")
        st.dataframe(df_kromosom, width="stretch", height=380)

render_footer("Beranda")