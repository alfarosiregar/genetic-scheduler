"""
Page 4: Pengaturan Aplikasi & Diagnostik Sistem
"""
import json
import os
import streamlit as st
from config.settings import SETTING_IMAGE_PATH, DATABASE_PATH, KROMOSOM_PATH, COLUMN_MAPPING
from components.header import render_page_hero, render_footer
from utils.data_loader import load_databases, load_kromosom_data

st.set_page_config(
    page_title="Settings - Genetic Scheduler",
    page_icon="⚙️",
    layout="wide",
)

DEFAULT_GA_CONFIG = {
    "generations": 20,
    "mutation_rate": 0.15,
    "crossover_rate": 0.80,
}

if "ga_config" not in st.session_state:
    st.session_state.ga_config = dict(DEFAULT_GA_CONFIG)

# Hero Banner & Stepper
render_page_hero(
    title="Pengaturan Sistem & Konfigurasi Default",
    subtitle=(
        "Atur nilai parameter bawaan Algoritma Genetika, ekspor profil konfigurasi JSON, "
        "dan pantau diagnostik koneksi database Excel."
    ),
    badge="⚙️  Konfigurasi & Diagnostik",
    image_path=SETTING_IMAGE_PATH,
    active_step=4,
)

# ========== DEFAULT GA CONFIGURATION ==========
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

if st.button("🔄 Kembalikan Parameter ke Rekomendasi Awal", width="stretch"):
    st.session_state.ga_config = dict(DEFAULT_GA_CONFIG)
    st.success("✅ Parameter default berhasil dikembalikan ke pengaturan rekomendasi!")
    st.rerun()

st.markdown("---")

# ========== EXPORT SETTINGS & SESSION MANAGEMENT ==========
st.markdown('<div class="gs-section-title">📁 Manajemen Profil Konfigurasi & Memori Sesi</div>', unsafe_allow_html=True)

m_col1, m_col2 = st.columns(2)

with m_col1:
    st.markdown("**💾 Ekspor Profil (.json)**")
    st.caption("Simpan konfigurasi parameter GA beserta daftar jadwal aktif ke dalam file JSON.")
    export_payload = {
        "app": "Genetic Scheduler",
        "ga_config": st.session_state.ga_config,
        "populasi_data": st.session_state.get("populasi_data", {}),
    }
    st.download_button(
        label="📥 Download Profil JSON",
        data=json.dumps(export_payload, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name="genetic_scheduler_profile.json",
        mime="application/json",
        type="primary",
        width="stretch",
    )

with m_col2:
    st.markdown("**🧹 Reset Memori Sesi**")
    st.caption("Bersihkan seluruh jadwal aktif, hasil optimasi, dan cache pembacaan database.")
    if st.button("🗑️ Bersihkan Semua Data Sesi", type="secondary", width="stretch"):
        st.session_state.clear()
        st.cache_data.clear()
        st.success("✅ Seluruh data sesi dan cache berhasil dibersihkan!")
        st.rerun()

st.markdown("---")

# ========== DATABASE & SYSTEM DIAGNOSTICS ==========
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
    <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; align-items: stretch;">
        <div class="gs-card" style="padding: 1.0rem 1.25rem; display: flex; flex-direction: column; justify-content: center; box-sizing: border-box;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.35rem;">
                File Master Database
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                {db_status}
            </div>
        </div>
        <div class="gs-card" style="padding: 1.0rem 1.25rem; display: flex; flex-direction: column; justify-content: center; box-sizing: border-box;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.35rem;">
                File Referensi Kromosom
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                {krom_status}
            </div>
        </div>
        <div class="gs-card" style="padding: 1.0rem 1.25rem; display: flex; flex-direction: column; justify-content: center; box-sizing: border-box;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.35rem;">
                Pemetaan Kolom Excel
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                {col_status}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_footer("Settings")