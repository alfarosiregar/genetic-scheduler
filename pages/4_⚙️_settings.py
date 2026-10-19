"""Halaman Pengaturan Sistem, Konfigurasi Default Algoritma Genetika, dan Diagnostik Database."""
import importlib
import os
import streamlit as st
from config.settings import SETTING_IMAGE_PATH, DATABASE_PATH, KROMOSOM_PATH, COLUMN_MAPPING
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from utils.data_loader import load_databases, load_kromosom_data
from utils.storage import init_session_state, save_session_cache, clear_session_cache, DEFAULT_GA_CONFIG

st.set_page_config(
    page_title="Settings - Genetic Scheduler",
    page_icon="⚙️",
    layout="wide",
)

init_session_state()

render_page_hero(
    title="Pengaturan Sistem & Konfigurasi Default",
    subtitle=(
        "Atur nilai parameter bawaan Algoritma Genetika, kelola sesi lokal, "
        "dan pantau diagnostik koneksi database Excel."
    ),
    badge="⚙️  Konfigurasi & Diagnostik",
    image_path=SETTING_IMAGE_PATH,
    active_step=4,
)

# Reset memori sesi
st.markdown('<div class="gs-section-title">🧹 Reset & Pembersihan Memori Sesi</div>', unsafe_allow_html=True)
st.caption("Bersihkan seluruh jadwal aktif, riwayat hasil optimasi, dan cache sesi lokal jika Anda ingin memulai dari awal.")

if st.button("🗑️ Bersihkan Semua Data Sesi", type="secondary"):
    clear_session_cache()
    st.session_state.clear()
    st.cache_data.clear()
    st.success("✅ Seluruh data sesi dan cache berhasil dibersihkan!")
    st.rerun()

st.markdown("---")

# Pengaturan parameter bawaan Algoritma Genetika
st.markdown('<div class="gs-section-title">🔧 Parameter Default Algoritma Genetika</div>', unsafe_allow_html=True)
st.caption("Nilai yang diatur di sini otomatis menjadi konfigurasi bawaan di halaman **Run Algorithm**.")

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.ga_config["generations"] = st.number_input(
        "🔄 Default Jumlah Generasi",
        min_value=1,
        max_value=100,
        value=int(st.session_state.ga_config.get("generations", 20)),
    )
with col2:
    st.session_state.ga_config["mutation_rate"] = st.slider(
        "🧪 Default Mutation Rate (per gen)",
        0.0,
        1.0,
        float(st.session_state.ga_config.get("mutation_rate", 0.15)),
        0.01,
    )
with col3:
    st.session_state.ga_config["crossover_rate"] = st.slider(
        "🧬 Default Crossover Rate",
        0.0,
        1.0,
        float(st.session_state.ga_config.get("crossover_rate", 0.80)),
        0.05,
    )
save_session_cache()

if st.button("🔄 Kembalikan Parameter ke Rekomendasi Awal", width="stretch"):
    st.session_state.ga_config = dict(DEFAULT_GA_CONFIG)
    save_session_cache()
    st.success("✅ Parameter default berhasil dikembalikan ke pengaturan rekomendasi!")
    st.rerun()

st.markdown("---")

# Diagnostik status file database
st.markdown(
    '<div class="gs-section-title" style="font-size: 1.15rem;">🩺 Diagnostik Sistem & Integritas Database</div>',
    unsafe_allow_html=True,
)

databases = load_databases()
df_krom = load_kromosom_data()

db_exists = os.path.exists(DATABASE_PATH)
krom_exists = os.path.exists(KROMOSOM_PATH)

db_status = "✅ Terhubung" if db_exists else "❌ Tidak Ditemukan"
krom_status = f"✅ {len(df_krom):,} Baris" if (krom_exists and df_krom is not None) else "❌ Error"
col_status = f"{len(COLUMN_MAPPING)} Atribut Aktif"

st.markdown(
    f"""
    <div class="gs-grid-3">
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label" style="text-transform: uppercase; letter-spacing: 0.04em;">
                File Master Database
            </div>
            <div class="gs-kpi-value" style="font-size: 1.15rem;">
                {db_status}
            </div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label" style="text-transform: uppercase; letter-spacing: 0.04em;">
                File Referensi Kromosom
            </div>
            <div class="gs-kpi-value" style="font-size: 1.15rem;">
                {krom_status}
            </div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label" style="text-transform: uppercase; letter-spacing: 0.04em;">
                Pemetaan Kolom Excel
            </div>
            <div class="gs-kpi-value" style="font-size: 1.15rem;">
                {col_status}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_footer("Settings")