"""Header, Hero Banner, Workflow Stepper, dan Global Responsive CSS"""
import base64
import functools
from io import BytesIO
from PIL import Image
import streamlit as st
from streamlit.navigation.page import StreamlitPage
from config.settings import (
    APP_IMAGE_PATH,
    INPUT_IMAGE_PATH,
    RUN_IMAGE_PATH,
    RESULT_IMAGE_PATH,
    SETTING_IMAGE_PATH,
)

from pathlib import Path

# Ubah label default 'app' dari app.py di navigasi sidebar menjadi '🏠 Beranda'
if not getattr(StreamlitPage, "_beranda_patched_v3", False):
    _orig_sp_init = getattr(StreamlitPage, "_orig_unpatched_init", StreamlitPage.__init__)
    StreamlitPage._orig_unpatched_init = _orig_sp_init
    _orig_wrapped_init = getattr(_orig_sp_init, "__wrapped__", _orig_sp_init)

    def _inject_beranda_kwargs(page, kwargs):
        try:
            page_stem = Path(str(page)).stem if isinstance(page, (str, Path)) else ""
            if page_stem == "app" or kwargs.get("default") is True:
                if not kwargs.get("title"):
                    kwargs = dict(kwargs, title="Beranda")
                if not kwargs.get("icon"):
                    kwargs = dict(kwargs, icon="🏠")
        except Exception:
            pass
        return kwargs

    @functools.wraps(_orig_wrapped_init)
    def _patched_wrapped_init(self, page, *args, **kwargs):
        kwargs = _inject_beranda_kwargs(page, kwargs)
        _orig_wrapped_init(self, page, *args, **kwargs)

    @functools.wraps(_orig_sp_init)
    def _patched_sp_init(self, page, *args, **kwargs):
        kwargs = _inject_beranda_kwargs(page, kwargs)
        _orig_sp_init(self, page, *args, **kwargs)

    _patched_sp_init.__wrapped__ = _patched_wrapped_init
    StreamlitPage.__init__ = _patched_sp_init
    StreamlitPage._beranda_patched = True
    StreamlitPage._beranda_patched_v2 = True
    StreamlitPage._beranda_patched_v3 = True


@st.cache_data
def _get_base64_image(path):
    """Konversi file gambar ke base64 string dengan caching agar cepat."""
    try:
        image = Image.open(path)
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=88)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return None


from contextlib import nullcontext
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx


def _main_shell_scope():
    """Scope persistent main_script_hash agar elemen tidak pernah di-unmount saat pindah halaman."""
    try:
        ctx = get_script_run_ctx(suppress_warning=True)
        if (
            ctx is not None
            and hasattr(ctx, "pages_manager")
            and hasattr(ctx.pages_manager, "main_script_hash")
            and hasattr(ctx, "run_with_active_hash")
        ):
            return ctx.run_with_active_hash(ctx.pages_manager.main_script_hash)
    except Exception:
        pass
    return nullcontext()


def apply_custom_css():
    """Terapkan Global Design System CSS secara persistent di main shell (0ms tanpa kedipan/delay)."""
    with _main_shell_scope():
        st.markdown(
            """
        <style>
            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            /* Sembunyikan Top Navbar / Header bawaan Streamlit (Deploy, Menu ⋮, garis dekorasi) */
            [data-testid="stToolbar"],
            [data-testid="stDecoration"],
            [data-testid="stStatusWidget"],
            #MainMenu {
                display: none !important;
                visibility: hidden !important;
            }
            header[data-testid="stHeader"] {
                background: transparent !important;
                height: 0px !important;
                min-height: 0px !important;
                border: none !important;
                box-shadow: none !important;
            }

            .block-container {
                padding-top: 1.2rem !important;
                padding-bottom: 3rem !important;
                max-width: 1280px !important;
            }

            /* ===== HERO BANNER ===== */
            .gs-hero {
                background: linear-gradient(135deg, #1E1B4B 0%, #312E81 45%, #4F46E5 100%);
                border-radius: 20px;
                padding: 28px 32px;
                color: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 28px;
                box-shadow: 0 12px 30px -8px rgba(79, 70, 229, 0.35);
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
            }
            .gs-hero::before {
                content: "";
                position: absolute;
                top: -60px;
                right: -60px;
                width: 240px;
                height: 240px;
                background: radial-gradient(circle, rgba(129, 140, 248, 0.28) 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
            }
            .gs-hero-content {
                flex: 1.35;
                z-index: 1;
            }
            .gs-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.24);
                color: #E0E7FF;
                font-size: 0.78rem;
                font-weight: 600;
                padding: 5px 13px;
                border-radius: 999px;
                letter-spacing: 0.3px;
                margin-bottom: 12px;
                backdrop-filter: blur(8px);
            }
            .gs-hero-title {
                font-size: 2.05rem;
                font-weight: 800;
                line-height: 1.2;
                margin: 0 0 10px 0;
                color: #FFFFFF !important;
                letter-spacing: -0.02em;
            }
            .gs-hero-sub {
                font-size: 0.98rem;
                line-height: 1.6;
                color: #C7D2FE;
                margin: 0 0 16px 0;
                max-width: 640px;
            }
            .gs-status-pills {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 8px;
            }
            .gs-pill {
                background: rgba(15, 23, 42, 0.38);
                border: 1px solid rgba(255, 255, 255, 0.16);
                color: #F8FAFC;
                padding: 5px 12px;
                border-radius: 10px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            .gs-hero-img-wrap {
                flex: 0 0 300px;
                width: 300px;
                max-width: 300px;
                height: 185px;
                background: #FFFFFF;
                border-radius: 14px;
                border: 2px solid rgba(255, 255, 255, 0.22);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.28);
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                z-index: 1;
                transition: transform 0.25s ease;
            }
            .gs-hero-img-wrap:hover {
                transform: translateY(-3px) scale(1.01);
            }
            .gs-hero-img {
                width: 100%;
                height: 100%;
                max-height: 185px;
                object-fit: contain;
                background: #FFFFFF;
                border-radius: 12px;
                display: block;
            }

            /* ===== WORKFLOW STEPPER ===== */
            .gs-stepper {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
                margin-bottom: 1.5rem;
            }
            .gs-step {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
                transition: all 0.2s ease;
            }
            .gs-step.active {
                border-color: #4F46E5;
                background: linear-gradient(135deg, #EEF2FF 0%, #FFFFFF 100%);
                box-shadow: 0 6px 16px rgba(79, 70, 229, 0.12);
            }
            .gs-step.done {
                border-color: #10B981;
                background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 100%);
            }
            .gs-step-num {
                width: 32px;
                height: 32px;
                border-radius: 10px;
                background: #F1F5F9;
                color: #475569;
                font-weight: 700;
                font-size: 0.85rem;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            .gs-step.active .gs-step-num {
                background: #4F46E5;
                color: #FFFFFF;
            }
            .gs-step.done .gs-step-num {
                background: #10B981;
                color: #FFFFFF;
            }
            .gs-step-text {
                line-height: 1.25;
            }
            .gs-step-title {
                font-size: 0.85rem;
                font-weight: 700;
                color: #0F172A;
            }
            .gs-step-desc {
                font-size: 0.73rem;
                color: #64748B;
            }

            /* ===== MODERN CARDS ===== */
            .gs-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
                padding: 22px;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
                height: 100%;
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            }
            .gs-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
                border-color: #C7D2FE;
            }
            .gs-card-icon {
                width: 44px;
                height: 44px;
                border-radius: 12px;
                background: #EEF2FF;
                color: #4F46E5;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.35rem;
                margin-bottom: 14px;
            }
            .gs-card h4 {
                margin: 0 0 8px 0;
                font-size: 1.05rem;
                font-weight: 700;
                color: #0F172A;
            }
            .gs-card p {
                margin: 0;
                font-size: 0.88rem;
                color: #475569;
                line-height: 1.55;
            }

            /* ===== STREAMLIT METRIC ENHANCEMENT ===== */
            [data-testid="stMetric"] {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                padding: 16px 18px !important;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
                transition: transform 0.18s ease, box-shadow 0.18s ease;
            }
            [data-testid="stMetric"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(79, 70, 229, 0.09);
                border-color: #C7D2FE;
            }
            [data-testid="stMetricLabel"] {
                font-weight: 600 !important;
                color: #475569 !important;
            }
            [data-testid="stMetricValue"] {
                font-weight: 800 !important;
                color: #0F172A !important;
            }

            /* ===== BANNERS & BADGES ===== */
            .gs-banner-success {
                background: linear-gradient(135deg, #059669 0%, #10B981 100%);
                color: #FFFFFF;
                padding: 18px 24px;
                border-radius: 16px;
                font-weight: 700;
                font-size: 1.02rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 8px 20px -4px rgba(16, 185, 129, 0.35);
                margin: 14px 0;
            }
            .gs-banner-warn {
                background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
                color: #FFFFFF;
                padding: 18px 24px;
                border-radius: 16px;
                font-weight: 700;
                font-size: 1.02rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 8px 20px -4px rgba(245, 158, 11, 0.3);
                margin: 14px 0;
            }
            .gs-section-title {
                font-size: 1.25rem;
                font-weight: 800;
                color: #0F172A;
                margin: 1.2rem 0 0.75rem 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            /* ===== TIMETABLE DAY CARDS ===== */
            .gs-slot-card {
                background: #FFFFFF;
                border-left: 4px solid #4F46E5;
                border-top: 1px solid #E2E8F0;
                border-right: 1px solid #E2E8F0;
                border-bottom: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 14px;
                margin-bottom: 10px;
                box-shadow: 0 2px 5px rgba(15, 23, 42, 0.03);
            }
            .gs-slot-card.conflict {
                border-left-color: #EF4444;
                background: #FEF2F2;
            }
            .gs-slot-time {
                font-size: 0.76rem;
                font-weight: 700;
                color: #4F46E5;
                background: #EEF2FF;
                padding: 2px 8px;
                border-radius: 6px;
                display: inline-block;
                margin-bottom: 6px;
            }
            .gs-slot-card.conflict .gs-slot-time {
                color: #DC2626;
                background: #FEE2E2;
            }
            .gs-slot-course {
                font-size: 0.9rem;
                font-weight: 700;
                color: #0F172A;
                margin-bottom: 4px;
            }
            .gs-slot-meta {
                font-size: 0.78rem;
                color: #475569;
            }

            /* ===== FOOTER ===== */
            .gs-footer {
                margin-top: 2.5rem;
                padding: 18px 24px;
                border-top: 1px solid #E2E8F0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                color: #64748B;
                font-size: 0.84rem;
            }

            /* ===== MODERN SIDEBAR STYLING ===== */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            [data-testid="stSidebar"] * {
                color: #F1F5F9;
            }
            /* Dropdown & input fields inside dark sidebar keep dark readable text */
            [data-testid="stSidebar"] [data-baseweb="select"] *,
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea {
                color: #0F172A !important;
            }
            /* Sidebar Multipage Navigation Links */
            [data-testid="stSidebarNav"] {
                padding-top: 0.75rem !important;
                padding-bottom: 0.5rem !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            [data-testid="stSidebarNav"] ul {
                padding: 0 10px !important;
            }
            [data-testid="stSidebarNav"] ul li a {
                border-radius: 12px !important;
                padding: 9px 14px !important;
                margin-bottom: 4px !important;
                transition: all 0.2s ease !important;
                font-weight: 600 !important;
                border: 1px solid transparent !important;
            }
            [data-testid="stSidebarNav"] ul li a:hover {
                background: rgba(255, 255, 255, 0.1) !important;
                border-color: rgba(255, 255, 255, 0.15) !important;
                transform: translateX(3px);
            }
            [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
                background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%) !important;
                border-color: rgba(165, 180, 252, 0.4) !important;
                box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45) !important;
                color: #FFFFFF !important;
            }

            /* Sidebar Custom Cards */
            .gs-sb-brand {
                background: linear-gradient(135deg, rgba(79, 70, 229, 0.35) 0%, rgba(124, 58, 237, 0.25) 100%);
                border: 1px solid rgba(165, 180, 252, 0.25);
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 14px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            }
            .gs-sb-brand-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 4px;
            }
            .gs-sb-brand-title {
                font-size: 1.02rem;
                font-weight: 800;
                color: #FFFFFF !important;
                letter-spacing: -0.01em;
            }
            .gs-sb-dot {
                font-size: 0.7rem;
                font-weight: 700;
                background: rgba(16, 185, 129, 0.2);
                border: 1px solid rgba(16, 185, 129, 0.45);
                color: #6EE7B7 !important;
                padding: 2px 8px;
                border-radius: 999px;
            }
            .gs-sb-brand-sub {
                font-size: 0.76rem;
                color: #C7D2FE !important;
                line-height: 1.35;
            }

            .gs-sb-card {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
                padding: 14px;
                margin-bottom: 14px;
                backdrop-filter: blur(8px);
            }
            .gs-sb-card-header {
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #A5B4FC !important;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .gs-sb-stat-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 10px;
            }
            .gs-sb-stat-box {
                background: rgba(15, 23, 42, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 9px 10px;
                text-align: center;
            }
            .gs-sb-stat-val {
                font-size: 1.15rem;
                font-weight: 800;
                color: #FFFFFF !important;
                line-height: 1.2;
            }
            .gs-sb-stat-lbl {
                font-size: 0.7rem;
                color: #94A3B8 !important;
                margin-top: 2px;
            }
            .gs-sb-progress-wrap {
                background: rgba(15, 23, 42, 0.6);
                border-radius: 999px;
                height: 7px;
                width: 100%;
                overflow: hidden;
                margin: 6px 0 4px 0;
            }
            .gs-sb-progress-bar {
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
                transition: width 0.3s ease;
            }
            .gs-sb-chip-row {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 5px;
                margin-top: 8px;
            }
            .gs-sb-chip {
                font-size: 0.68rem;
                font-weight: 600;
                background: rgba(79, 70, 229, 0.28);
                border: 1px solid rgba(129, 140, 248, 0.3);
                color: #E0E7FF !important;
                padding: 3px 4px;
                border-radius: 8px;
                text-align: center;
                white-space: nowrap;
            }
            /* Form container inside sidebar */
            [data-testid="stSidebar"] [data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.45) !important;
                border: 1px solid rgba(255, 255, 255, 0.14) !important;
                border-radius: 14px !important;
                padding: 14px !important;
            }
            /* Expander 'Tambah Jadwal Cepat' inside sidebar (non-white indigo theme) */
            [data-testid="stSidebar"] [data-testid="stExpander"],
            [data-testid="stSidebar"] [data-testid="stExpander"] details {
                background: rgba(30, 27, 75, 0.85) !important;
                border: 1px solid rgba(129, 140, 248, 0.35) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary:focus,
            [data-testid="stSidebar"] [data-testid="stExpander"] details[open] > summary {
                background: linear-gradient(135deg, #312E81 0%, #4338CA 100%) !important;
                color: #FFFFFF !important;
                padding: 10px 14px !important;
                border-radius: 11px !important;
                font-weight: 700 !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] summary *,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
                color: #FFFFFF !important;
                fill: #FFFFFF !important;
            }
            /* Buttons inside sidebar ('Muat 15 Sampel Instan' & 'Tambahkan Jadwal') */
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
                background: linear-gradient(135deg, #0D9488 0%, #10B981 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(110, 231, 183, 0.4) !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
            [data-testid="stSidebar"] .stButton > button:focus,
            [data-testid="stSidebar"] .stButton > button:active {
                background: linear-gradient(135deg, #0F766E 0%, #059669 100%) !important;
                color: #FFFFFF !important;
                border-color: rgba(167, 243, 208, 0.65) !important;
                transform: translateY(-1px);
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button,
            [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
                background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(165, 180, 252, 0.4) !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
            }
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button:hover,
            [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
                background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
                color: #FFFFFF !important;
                border-color: rgba(199, 210, 254, 0.65) !important;
            }
            [data-testid="stSidebar"] button * {
                color: #FFFFFF !important;
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: rgba(15, 23, 42, 0.55) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
            }
            [data-testid="stSidebar"] [data-testid="stMetricLabel"] *,
            [data-testid="stSidebar"] [data-testid="stMetricValue"] * {
                color: #FFFFFF !important;
            }

            /* Hide zero-height utility iframes */
            iframe[height="0"] {
                display: none !important;
                height: 0px !important;
                width: 0px !important;
                border: none !important;
                position: absolute !important;
                pointer-events: none !important;
            }
            [data-testid="stElementContainer"]:has(iframe[height="0"]) {
                display: none !important;
                height: 0px !important;
                margin: 0px !important;
                padding: 0px !important;
            }

            /* ===== RESPONSIVE MEDIA QUERIES ===== */
            @media (max-width: 900px) {
                .gs-hero {
                    flex-direction: column;
                    padding: 22px 20px;
                    text-align: left;
                }
                .gs-hero-img-wrap {
                    max-width: 100%;
                    width: 100%;
                }
                .gs-hero-title {
                    font-size: 1.6rem;
                }
                .gs-stepper {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            @media (max-width: 540px) {
                .gs-stepper {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "_sb_width_reset_done" not in st.session_state:
        st.session_state["_sb_width_reset_done"] = True
        import streamlit.components.v1 as components

        with _main_shell_scope():
            components.html(
                """
                <script>
                (function() {
                    try {
                        const p = window.parent;
                        p.localStorage.setItem("sidebarWidth", "300");
                        const sb = p.document.querySelector('[data-testid="stSidebar"]');
                        if (sb) {
                            const handle = sb.querySelector('div[style*="col-resize"], .eelgd2m3');
                            if (handle) {
                                handle.dispatchEvent(new MouseEvent("dblclick", { bubbles: true, cancelable: true }));
                            }
                            if (sb.getAttribute("aria-expanded") === "true") {
                                sb.style.width = "300px";
                            }
                        }
                        if (!p.__gsSidebarResetHooked) {
                            p.__gsSidebarResetHooked = true;
                            p.addEventListener("beforeunload", function() {
                                try { p.localStorage.removeItem("sidebarWidth"); } catch (e) {}
                            });
                        }
                    } catch (e) {}
                })();
                </script>
                """,
                height=0,
                width=0,
            )


def render_workflow_stepper(active_step=0):
    """
    Tampilkan indikator alur kerja 4 tahap yang interaktif dan kontekstual.
    active_step: 0 (Home), 1 (Input Data), 2 (Run GA), 3 (Results), 4 (Settings)
    """
    pop_count = len(st.session_state.get("populasi_data", {}))
    has_results = st.session_state.get("ga_results") is not None

    steps = [
        (1, "📊 Input Data", f"{pop_count} jadwal aktif" if pop_count > 0 else "Tambah / upload jadwal", pop_count >= 2),
        (2, "🧬 Run Algorithm", "Optimasi selesai" if has_results else "Atur parameter & evolusi", has_results),
        (3, "📈 Results", "Analisis & ekspor siap" if has_results else "Visualisasi & unduh jadwal", has_results and active_step == 3),
        (4, "⚙️ Settings", "Konfigurasi sistem", False),
    ]

    items_html = []
    for num, title, desc, is_done in steps:
        state_cls = "active" if active_step == num else ("done" if is_done else "")
        badge_txt = "✓" if (is_done and active_step != num) else str(num)
        items_html.append(
            f'<div class="gs-step {state_cls}">'
            f'<div class="gs-step-num">{badge_txt}</div>'
            f'<div class="gs-step-text">'
            f'<div class="gs-step-title">{title}</div>'
            f'<div class="gs-step-desc">{desc}</div>'
            f'</div></div>'
        )

    st.markdown(f'<div class="gs-stepper">{"".join(items_html)}</div>', unsafe_allow_html=True)


_HEADER_REV = 6


def render_page_hero(title, subtitle, badge="🧬 Genetic Scheduler", image_path=APP_IMAGE_PATH, active_step=0):
    """Render Hero Banner modern 2 kolom beserta global sidebar secara instan."""
    apply_custom_css()
    st.session_state["_sb_rendered_this_run"] = False

    if active_step != 1:
        from components.sidebar import render_global_sidebar
        if render_global_sidebar(active_step=active_step):
            st.rerun()

    pop_count = len(st.session_state.get("populasi_data", {}))
    ga_results = st.session_state.get("ga_results")
    if ga_results is not None:
        final_konflik = ga_results["history"]["total_konflik"][-1]
        status_hasil = f"✅ Hasil GA: {final_konflik} Konflik"
    else:
        status_hasil = "⏳ Belum Dijalankan"

    img_b64 = _get_base64_image(image_path)
    img_html = (
        f'<div class="gs-hero-img-wrap" style="background: #FFFFFF; width: 300px; height: 185px; border-radius: 14px; overflow: hidden; display: flex; align-items: center; justify-content: center;">'
        f'<img class="gs-hero-img" style="width: 100%; height: 100%; object-fit: contain; background: #FFFFFF; border: none; box-shadow: none;" src="data:image/jpeg;base64,{img_b64}" alt="Banner">'
        f'</div>'
        if img_b64
        else ""
    )

    st.markdown(
        f"""
        <div class="gs-hero">
            <div class="gs-hero-content">
                <div class="gs-badge">{badge}</div>
                <h1 class="gs-hero-title">{title}</h1>
                <p class="gs-hero-sub">{subtitle}</p>
                <div class="gs-status-pills">
                    <span class="gs-pill">📋 Data Aktif: {pop_count} Jadwal</span>
                    <span class="gs-pill">{status_hasil}</span>
                </div>
            </div>
            {img_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(page_name="Home"):
    """Render footer konsisten di bagian bawah halaman."""
    st.markdown(
        f"""
        <div class="gs-footer">
            <div><strong>🧬 Genetic Scheduler</strong> · Sistem Optimasi Penjadwalan Kuliah Berbasis Algoritma Genetika</div>
            <div>Halaman: <strong>{page_name}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===== FUNGSI KOMPATIBILITAS LAMA =====
def display_header():
    render_page_hero(
        title="Genetic Scheduler",
        subtitle="Otomatisasi dan optimasi penyusunan jadwal perkuliahan bebas bentrok menggunakan Algoritma Genetika.",
        badge="🧬 Evolutionary Timetable Optimizer",
        image_path=APP_IMAGE_PATH,
        active_step=0,
    )


def display_image_on_app():
    pass


def display_image_on_input():
    pass


def display_image_on_run():
    pass


def display_image_on_results():
    pass


def display_image_on_settings():
    pass