"""Entry point aplikasi Genetic Scheduler yang menampilkan halaman utama (landing.html) pada rute '/'."""
import importlib
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)

from utils.data_loader import load_databases, load_kromosom_data
from utils.storage import init_session_state

st.set_page_config(
    page_title="Genetic Scheduler — Sistem Penjadwalan Kuliah",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session_state()

databases = load_databases()
df_kromosom = load_kromosom_data()

n_dosen = len(databases["dosen"]) if databases else 177
n_matkul = len(databases["matkul"]) if databases else 138
n_prodi = len(databases["prodi"]) if databases else 5
n_kelas = len(databases["kelas"]) if databases else 42
n_ruangan = len(databases["ruangan"]) if databases else 32
n_waktu = len(databases["waktu"]) if databases else 50
n_ref = f"{len(df_kromosom):,}" if df_kromosom is not None else "356"

# Tautan navigasi tersembunyi untuk berpindah halaman dari dalam iframe landing.html
st.page_link("pages/0_🏠_beranda.py", label="nav_beranda")
st.page_link("pages/1_📊_input_data.py", label="nav_input_data")
st.page_link("pages/2_🧬_run_algorithm.py", label="nav_run_algorithm")
st.page_link("pages/3_📈_results.py", label="nav_results")
st.page_link("pages/4_⚙️_settings.py", label="nav_settings")

landing_path = Path(__file__).parent / "landing.html"
html_content = landing_path.read_text(encoding="utf-8")

replacements = {
    "{{N_DOSEN}}": str(n_dosen),
    "{{N_MATKUL}}": str(n_matkul),
    "{{N_PRODI}}": str(n_prodi),
    "{{N_KELAS}}": str(n_kelas),
    "{{N_RUANGAN}}": str(n_ruangan),
    "{{N_WAKTU}}": str(n_waktu),
    "{{N_REF}}": str(n_ref),
}
for placeholder, val in replacements.items():
    html_content = html_content.replace(placeholder, val)

# Sembunyikan elemen bawaan Streamlit dan tampilkan iframe landing page secara layar penuh
st.markdown(
    """
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"],
        [data-testid="stPageLink"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            background: #F8FAFC !important;
            width: 100vw !important;
            height: 100dvh !important;
        }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw !important;
            width: 100vw !important;
            height: 100dvh !important;
        }
        [data-testid="stMainBlockContainer"] iframe:not([height="0"]),
        .element-container iframe:not([height="0"]),
        iframe[title="streamlit_components_v1.html"]:not([height="0"]) {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            height: 100dvh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 999999 !important;
            display: block !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(html_content, height=900, scrolling=True)