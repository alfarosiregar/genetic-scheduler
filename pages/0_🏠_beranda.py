"""Halaman Beranda Dashboard untuk ringkasan dan eksplorasi master database perkuliahan."""
import importlib
import pandas as pd
import streamlit as st
from config.settings import APP_IMAGE_PATH
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from utils.data_loader import load_kromosom_data, load_databases
from utils.storage import init_session_state

st.set_page_config(
    page_title="Beranda - Genetic Scheduler",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="auto",
)

init_session_state()

render_page_hero(
    title="Beranda Dashboard · Genetic Scheduler",
    subtitle=(
        "Pusat kendali dan ringkasan master database perkuliahan berbasis Algoritma Genetika. "
        "Pantau statistik entitas akademik, eksplorasi dataset referensi, dan mulai penyusunan jadwal bebas konflik."
    ),
    badge="🏠 Beranda · Course Timetable Optimizer",
    image_path=APP_IMAGE_PATH,
    active_step=0,
)

df_kromosom = load_kromosom_data()
databases = load_databases()

# Ringkasan metrik utama database
st.markdown('<div class="gs-section-title">🏛️ Ringkasan Master Database Perkuliahan</div>', unsafe_allow_html=True)
n_dosen = len(databases["dosen"]) if databases else 0
n_matkul = len(databases["matkul"]) if databases else 0
n_prodi = len(databases["prodi"]) if databases else 0
n_kelas = len(databases["kelas"]) if databases else 0
n_ruangan = len(databases["ruangan"]) if databases else 0
n_waktu = len(databases["waktu"]) if databases else 0

st.markdown(
    f"""
    <div class="gs-grid-6">
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">👨‍🏫 Dosen</div>
            <div class="gs-kpi-value">{n_dosen}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">📘 Mata Kuliah</div>
            <div class="gs-kpi-value">{n_matkul}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">🎓 Program Studi</div>
            <div class="gs-kpi-value">{n_prodi}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">👥 Kelas</div>
            <div class="gs-kpi-value">{n_kelas}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">🏢 Ruangan</div>
            <div class="gs-kpi-value">{n_ruangan}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">⏰ Slot Waktu</div>
            <div class="gs-kpi-value">{n_waktu}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Kartu ringkasan alur kerja sistem
st.markdown('<div class="gs-section-title">🚀 Alur Kerja & Keunggulan Sistem</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="gs-grid-4">
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

# Tabel eksplorasi data referensi
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

st.markdown("---")
nav_c1, nav_c2 = st.columns(2)
with nav_c1:
    if st.button("📊 Mulai Input Data Jadwal", type="primary", width="stretch"):
        st.switch_page("pages/1_📊_input_data.py")
with nav_c2:
    if st.button("🧬 Buka Eksekusi Algoritma Genetika", width="stretch"):
        st.switch_page("pages/2_🧬_run_algorithm.py")

render_footer("Beranda")
