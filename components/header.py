"""Komponen Header, Hero Banner, Stepper Alur Kerja, Footer, dan CSS Responsif Global."""
import base64
import functools
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit.navigation.page import StreamlitPage
from config.settings import APP_IMAGE_PATH

# Sembunyikan rute 'app.py' (Landing Page) dari daftar menu navigasi di Sidebar Dashboard
if not getattr(StreamlitPage, "_landing_patched_v5", False):
    _orig_sp_init = getattr(StreamlitPage, "_orig_unpatched_init", StreamlitPage.__init__)
    StreamlitPage._orig_unpatched_init = _orig_sp_init
    _orig_wrapped_init = getattr(_orig_sp_init, "__wrapped__", _orig_sp_init)

    def _inject_landing_kwargs(page, kwargs):
        try:
            page_stem = Path(str(page)).stem if isinstance(page, (str, Path)) else ""
            if page_stem == "app" or kwargs.get("default") is True:
                kwargs = dict(kwargs, title="Landing Page", icon="✨", visibility="hidden")
        except Exception:
            pass
        return kwargs

    @functools.wraps(_orig_wrapped_init)
    def _patched_wrapped_init(self, page, *args, **kwargs):
        kwargs = _inject_landing_kwargs(page, kwargs)
        _orig_wrapped_init(self, page, *args, **kwargs)

    @functools.wraps(_orig_sp_init)
    def _patched_sp_init(self, page, *args, **kwargs):
        kwargs = _inject_landing_kwargs(page, kwargs)
        _orig_sp_init(self, page, *args, **kwargs)

    _patched_sp_init.__wrapped__ = _patched_wrapped_init
    StreamlitPage.__init__ = _patched_sp_init
    StreamlitPage._landing_patched_v5 = True


@st.cache_data
def _get_base64_image(path):
    """Mengonversi file gambar menjadi string base64 dengan caching."""
    try:
        image = Image.open(path)
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=88)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return None


def _main_shell_scope():
    """Mengembalikan konteks standar halaman agar elemen tidak saling menimpa antar rute."""
    return nullcontext()


def apply_custom_css():
    """Menyuntikkan CSS global dan pengatur ukuran sidebar responsif untuk seluruh halaman Dashboard."""
    st.markdown(
        """
        <style>
            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            /* Sembunyikan menu toolbar kanan bawaan Streamlit */
            [data-testid="stToolbarActions"],
            [data-testid="stAppDeployButton"],
            .stDeployButton,
            [data-testid="stMainMenu"],
            #MainMenu,
            [data-testid="stStatusWidget"],
            [data-testid="stDecoration"] {
                display: none !important;
                visibility: hidden !important;
            }
            header[data-testid="stHeader"] {
                background: transparent !important;
                height: 3.5rem !important;
                min-height: 3.5rem !important;
                border: none !important;
                box-shadow: none !important;
                pointer-events: none !important;
                z-index: 999990 !important;
            }
            header[data-testid="stHeader"] [data-testid="stToolbar"] {
                background: transparent !important;
                pointer-events: none !important;
            }

            /* Tombol buka & tutup sidebar */
            [data-testid="stExpandSidebarButton"],
            [data-testid="collapsedControl"] button {
                pointer-events: auto !important;
                display: inline-flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 6px !important;
                position: fixed !important;
                top: 12px !important;
                left: 14px !important;
                z-index: 999999 !important;
                background: linear-gradient(135deg, #1E1B4B 0%, #4F46E5 100%) !important;
                color: #FFFFFF !important;
                border: 1.5px solid rgba(165, 180, 252, 0.65) !important;
                border-radius: 12px !important;
                padding: 8px 14px !important;
                min-height: 40px !important;
                width: auto !important;
                height: auto !important;
                box-shadow: 0 6px 18px rgba(30, 27, 75, 0.38) !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stExpandSidebarButton"],
            [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) [data-testid="collapsedControl"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
            [data-testid="stExpandSidebarButton"]:hover,
            [data-testid="collapsedControl"] button:hover {
                background: linear-gradient(135deg, #312E81 0%, #6366F1 100%) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 8px 22px rgba(79, 70, 229, 0.5) !important;
            }
            [data-testid="stExpandSidebarButton"]::after,
            [data-testid="collapsedControl"] button::after {
                content: "Buka Sidebar";
                font-size: 0.82rem !important;
                font-weight: 700 !important;
                color: #FFFFFF !important;
                letter-spacing: 0.01em !important;
                line-height: 1 !important;
                white-space: nowrap !important;
            }
            [data-testid="stExpandSidebarButton"] *,
            [data-testid="stExpandSidebarButton"] svg,
            [data-testid="collapsedControl"] button * {
                color: #FFFFFF !important;
            }
            [data-testid="stExpandSidebarButton"] svg,
            [data-testid="stExpandSidebarButton"] svg path:not([fill="none"]),
            [data-testid="collapsedControl"] button svg,
            [data-testid="collapsedControl"] button svg path:not([fill="none"]) {
                fill: #FFFFFF !important;
            }
            [data-testid="stSidebarHeader"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto !important;
                position: relative !important;
                z-index: 999999 !important;
            }
            [data-testid="stSidebarCollapseButton"] {
                opacity: 1 !important;
                visibility: visible !important;
                display: flex !important;
                pointer-events: auto !important;
                position: relative !important;
                z-index: 999999 !important;
            }
            [data-testid="stSidebarCollapseButton"] button {
                pointer-events: auto !important;
                cursor: pointer !important;
                background: rgba(255, 255, 255, 0.14) !important;
                border: 1px solid rgba(255, 255, 255, 0.28) !important;
                border-radius: 10px !important;
                padding: 5px 10px !important;
                color: #FFFFFF !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 4px !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stSidebarCollapseButton"] button:hover {
                background: rgba(255, 255, 255, 0.24) !important;
                border-color: rgba(255, 255, 255, 0.5) !important;
            }
            [data-testid="stSidebarCollapseButton"] button *,
            [data-testid="stSidebarCollapseButton"] button svg {
                color: #FFFFFF !important;
            }
            [data-testid="stSidebarCollapseButton"] button svg,
            [data-testid="stSidebarCollapseButton"] button svg path:not([fill="none"]) {
                fill: #FFFFFF !important;
            }

            .block-container {
                padding-top: 1.4rem !important;
                padding-bottom: 3rem !important;
                max-width: 1280px !important;
            }
            [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) .block-container {
                padding-top: 3.8rem !important;
            }

            /* Hero Banner */
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
                box-sizing: border-box;
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
                flex: 1 1 0%;
                min-width: 0;
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
                max-width: 100%;
            }
            .gs-hero-title {
                font-size: 2.05rem;
                font-weight: 800;
                line-height: 1.2;
                margin: 0 0 10px 0;
                color: #FFFFFF !important;
                letter-spacing: -0.02em;
                word-break: break-word;
            }
            .gs-hero-sub {
                font-size: 0.98rem;
                line-height: 1.6;
                color: #C7D2FE;
                margin: 0 0 16px 0;
                max-width: 640px;
                word-break: break-word;
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
                max-width: 100%;
                box-sizing: border-box;
            }
            .gs-hero-img-wrap {
                flex: 0 0 290px;
                width: 290px;
                max-width: 290px;
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
                box-sizing: border-box;
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

            /* Indikator Alur Kerja (Stepper) */
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

            /* Kartu & Metrik */
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

            /* Banner Status & Judul Section */
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

            /* Kartu Jadwal Mingguan */
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

            /* Footer */
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
            .gs-footer-brand {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                flex-wrap: wrap;
            }
            .gs-footer-name {
                color: #1E293B;
                font-weight: 700;
            }

            /* Gaya Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0F172A 0%, #1E1B4B 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            [data-testid="stSidebar"][aria-expanded="true"] {
                visibility: visible !important;
                opacity: 1 !important;
                transform: translateX(0) !important;
                pointer-events: auto !important;
            }
            /* Sembunyikan seluruh elemen sidebar ketika ditutup */
            [data-testid="stSidebar"][aria-expanded="false"] {
                width: 0px !important;
                min-width: 0px !important;
                max-width: 0px !important;
                flex: 0 0 0px !important;
                margin: 0px !important;
                padding: 0px !important;
                border: none !important;
                box-shadow: none !important;
                overflow: hidden !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                transform: translateX(-120vw) !important;
            }
            [data-testid="stSidebar"][aria-expanded="false"] > *,
            [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"],
            [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarHeader"],
            [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"],
            [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                width: 0px !important;
                overflow: hidden !important;
                pointer-events: none !important;
            }
            [data-testid="stSidebar"] * {
                color: #F1F5F9;
            }
            [data-testid="stSidebar"] [data-baseweb="select"] *,
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea {
                color: #0F172A !important;
            }
            [data-testid="stSidebarNav"] {
                padding-top: 0.75rem !important;
                padding-bottom: 0.5rem !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            [data-testid="stSidebarNav"] ul {
                padding: 0 10px !important;
            }
            [data-testid="stSidebarNavItems"] > li:has(a[href$="/"]),
            [data-testid="stSidebarNavItems"] > li:has(a[href$="/app"]) {
                display: none !important;
            }
            [data-testid="stSidebarNav"] ul li a {
                border-radius: 12px !important;
                padding: 9px 14px !important;
                margin-bottom: 4px !important;
                transition: all 0.2s ease !important;
                font-weight: 600 !important;
                border: 1px solid transparent !important;
                text-transform: capitalize !important;
            }
            [data-testid="stSidebarNav"] ul li a span,
            [data-testid="stSidebarNavItems"] a span,
            [data-testid="stSidebarNavItems"] a {
                text-transform: capitalize !important;
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

            /* Kartu Identitas & Monitor di Sidebar */
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
            [data-testid="stSidebar"] [data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.45) !important;
                border: 1px solid rgba(255, 255, 255, 0.14) !important;
                border-radius: 14px !important;
                padding: 14px !important;
            }
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
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary svg path:not([fill="none"]) {
                fill: #FFFFFF !important;
            }
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
            [data-testid="stSidebar"] .stButton > button *,
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button *,
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] *,
            [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] * {
                color: #FFFFFF !important;
            }
            [data-testid="stSidebar"] .stButton > button svg,
            [data-testid="stSidebar"] .stButton > button svg path:not([fill="none"]),
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button svg,
            [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button svg path:not([fill="none"]) {
                fill: #FFFFFF !important;
            }
            /* Ikon panah dropdown (chevron) pada input selectbox di sidebar */
            [data-testid="stSidebar"] [data-testid="stSelectbox"] button[aria-label="Open"],
            [data-testid="stSidebar"] [data-testid="stSelectbox"] button[aria-label="Clear value"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #1E1B4B !important;
                opacity: 1 !important;
                visibility: visible !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0 6px !important;
            }
            [data-testid="stSidebar"] [data-testid="stSelectbox"] svg,
            [data-testid="stSidebar"] [data-baseweb="select"] svg {
                color: #1E1B4B !important;
                fill: #1E1B4B !important;
                opacity: 1 !important;
                visibility: visible !important;
                width: 1.25rem !important;
                height: 1.25rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stSelectbox"] svg path:not([fill="none"]),
            [data-testid="stSidebar"] [data-baseweb="select"] svg path:not([fill="none"]) {
                fill: #1E1B4B !important;
            }
            svg path[fill="none"] {
                fill: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: rgba(15, 23, 42, 0.55) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
            }
            [data-testid="stSidebar"] [data-testid="stMetricLabel"] *,
            [data-testid="stSidebar"] [data-testid="stMetricValue"] * {
                color: #FFFFFF !important;
            }

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

            /* Kelas Grid Responsif */
            .gs-grid-6 {
                display: grid;
                grid-template-columns: repeat(6, minmax(0, 1fr));
                gap: 12px;
                align-items: stretch;
                margin-bottom: 0.75rem;
            }
            .gs-grid-5 {
                display: grid;
                grid-template-columns: repeat(5, minmax(0, 1fr));
                gap: 12px;
                align-items: stretch;
                margin-bottom: 1rem;
            }
            .gs-grid-4 {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 16px;
                align-items: stretch;
            }
            .gs-grid-3 {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 14px;
                align-items: stretch;
            }
            .gs-kpi-card {
                padding: 15px 16px !important;
                border-radius: 14px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                box-sizing: border-box !important;
                min-width: 0 !important;
            }
            .gs-kpi-label {
                font-size: 0.84rem;
                font-weight: 600;
                color: #475569;
                margin-bottom: 6px;
                line-height: 1.3;
                word-break: break-word;
            }
            .gs-kpi-value {
                font-size: 1.85rem;
                font-weight: 800;
                color: #0F172A;
                line-height: 1.15;
                word-break: break-word;
            }
            .gs-kpi-sub {
                font-size: 0.74rem;
                color: #64748B;
                margin-top: 6px;
                line-height: 1.3;
            }

            [data-baseweb="tab-list"] {
                overflow-x: auto !important;
                overflow-y: hidden !important;
                flex-wrap: nowrap !important;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: thin;
                gap: 6px !important;
            }
            [data-baseweb="tab"] {
                white-space: nowrap !important;
                flex-shrink: 0 !important;
            }

            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stFormSubmitButton"] > button {
                min-height: 42px !important;
                height: auto !important;
                white-space: normal !important;
                word-break: break-word !important;
                line-height: 1.35 !important;
                padding: 0.5rem 0.9rem !important;
            }

            /* Media Queries untuk Tablet & Mobile */
            @media (max-width: 1100px) {
                .gs-grid-6,
                .gs-grid-5 {
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                }
                .gs-grid-4 {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }

            @media (min-width: 769px) and (max-width: 1024px) {
                [data-testid="stHorizontalBlock"] {
                    flex-wrap: wrap !important;
                }
                [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                    min-width: calc(50% - 1rem) !important;
                    flex: 1 1 calc(50% - 1rem) !important;
                }
            }

            @media (max-width: 900px) {
                .gs-hero {
                    flex-direction: column !important;
                    align-items: stretch !important;
                    padding: 20px 18px !important;
                    gap: 16px !important;
                    text-align: left;
                }
                .gs-hero-content {
                    width: 100% !important;
                    flex: 1 1 auto !important;
                }
                .gs-hero-img-wrap {
                    flex: 0 0 auto !important;
                    max-width: 100% !important;
                    width: 100% !important;
                    height: 170px !important;
                    max-height: 170px !important;
                }
                .gs-hero-img {
                    width: 100% !important;
                    height: 100% !important;
                    max-height: 170px !important;
                    object-fit: contain !important;
                }
                .gs-hero-title {
                    font-size: 1.5rem !important;
                    line-height: 1.25 !important;
                }
                .gs-hero-sub {
                    font-size: 0.9rem !important;
                    line-height: 1.5 !important;
                    margin-bottom: 12px !important;
                }
                .gs-stepper {
                    grid-template-columns: repeat(2, 1fr);
                }
                .gs-grid-3 {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 3.8rem !important;
                    padding-left: 0.9rem !important;
                    padding-right: 0.9rem !important;
                    padding-bottom: 2.5rem !important;
                }
                [data-testid="stHorizontalBlock"] {
                    flex-wrap: wrap !important;
                    gap: 0.65rem !important;
                }
                [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                    width: 100% !important;
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                }
                .gs-grid-6,
                .gs-grid-5 {
                    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
                    gap: 10px !important;
                }
                .gs-grid-5 > :last-child:nth-child(odd) {
                    grid-column: 1 / -1;
                }
                .gs-grid-4,
                .gs-grid-3 {
                    grid-template-columns: 1fr !important;
                    gap: 10px !important;
                }
                .gs-kpi-card {
                    padding: 13px 14px !important;
                }
                .gs-kpi-value {
                    font-size: 1.45rem !important;
                }
                .gs-card {
                    padding: 16px !important;
                }
                .gs-banner-success,
                .gs-banner-warn {
                    flex-direction: column !important;
                    align-items: flex-start !important;
                    gap: 8px !important;
                    padding: 14px 16px !important;
                    font-size: 0.86rem !important;
                    white-space: normal !important;
                    word-break: break-word !important;
                }
                .gs-section-title {
                    font-size: 1.08rem !important;
                    line-height: 1.35 !important;
                }
                .gs-footer {
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                    text-align: center !important;
                    padding: 16px 12px !important;
                    font-size: 0.80rem !important;
                    gap: 4px !important;
                }
                .gs-footer div,
                .gs-footer-brand,
                .gs-footer-page {
                    text-align: center !important;
                    width: 100% !important;
                    line-height: 1.45 !important;
                }
                .gs-footer-brand {
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                    gap: 3px !important;
                }
                .gs-footer-icon {
                    display: block !important;
                    font-size: 1rem !important;
                    line-height: 1.2 !important;
                }
                .gs-footer-name,
                .gs-footer-desc {
                    display: block !important;
                    width: 100% !important;
                }
                .gs-footer-sep {
                    display: none !important;
                }
                /* Lebar sidebar 80vw saat dibuka dan tersembunyi penuh saat ditutup pada layar mobile */
                [data-testid="stSidebar"][aria-expanded="true"] {
                    width: 80vw !important;
                    min-width: 80vw !important;
                    max-width: 80vw !important;
                    flex: 0 0 80vw !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    transform: translateX(0) !important;
                    pointer-events: auto !important;
                }
                [data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {
                    width: 100% !important;
                    max-width: 100% !important;
                    box-sizing: border-box !important;
                }
                [data-testid="stSidebar"][aria-expanded="false"] {
                    width: 0px !important;
                    min-width: 0px !important;
                    max-width: 0px !important;
                    flex: 0 0 0px !important;
                    margin: 0px !important;
                    padding: 0px !important;
                    border: none !important;
                    box-shadow: none !important;
                    overflow: hidden !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    pointer-events: none !important;
                    transform: translateX(-120vw) !important;
                }
                [data-testid="stSidebar"] div[style*="col-resize"] {
                    display: none !important;
                    pointer-events: none !important;
                }
            }

            .gs-mobile-spacer {
                display: none;
            }
            @media (max-width: 768px) {
                .gs-mobile-spacer {
                    display: block !important;
                    height: 12px !important;
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
            }
            @media (max-width: 540px) {
                .gs-stepper {
                    grid-template-columns: 1fr !important;
                }
                .gs-hero-title {
                    font-size: 1.35rem !important;
                }
                .gs-status-pills {
                    gap: 6px !important;
                }
                .gs-pill {
                    font-size: 0.75rem !important;
                    padding: 4px 10px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    import streamlit.components.v1 as components

    components.html(
        r"""
        <script>
        (function() {
            try {
                const p = window.parent;
                p.localStorage.setItem("sidebarWidth", "300");
                const sb = p.document.querySelector('[data-testid="stSidebar"]');
                if (!sb) return;
                const lockedProps = ["width", "min-width", "max-width", "visibility", "opacity", "transform", "overflow"];
                lockedProps.forEach(function(prop) {
                    sb.style.removeProperty(prop);
                });
                if (sb.getAttribute("aria-expanded") === "true" && p.innerWidth > 768) {
                    sb.style.width = "300px";
                }
                if (!sb.__gsSetPropPatched) {
                    sb.__gsSetPropPatched = true;
                    const origSetProp = sb.style.setProperty.bind(sb.style);
                    sb.style.setProperty = function(prop, val, priority) {
                        if (priority === "important" && lockedProps.indexOf(prop) !== -1) {
                            sb.style.removeProperty(prop);
                            return;
                        }
                        return origSetProp(prop, val, priority);
                    };
                }
                const navSpans = p.document.querySelectorAll('[data-testid="stSidebarNav"] a span, [data-testid="stSidebarNavItems"] a span');
                navSpans.forEach(function(s) {
                    if (s && s.textContent) {
                        s.textContent = s.textContent.replace(/(?:^|\s|_)\w/g, function(l) {
                            return l.toUpperCase().replace('_', ' ');
                        });
                    }
                });
            } catch (e) {}
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_workflow_stepper(active_step=0):
    """Merender indikator 4 tahap alur kerja sesuai halaman yang sedang aktif."""
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


_HEADER_REV = 22


def render_page_hero(title, subtitle, badge="🧬 Genetic Scheduler", image_path=APP_IMAGE_PATH, active_step=0):
    """Merender Hero Banner halaman Dashboard beserta sidebar global."""
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
        f'<div class="gs-hero-img-wrap">'
        f'<img class="gs-hero-img" src="data:image/jpeg;base64,{img_b64}" alt="Banner">'
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
    """Merender footer halaman Dashboard."""
    st.markdown(
        f"""
        <div class="gs-footer">
            <div class="gs-footer-brand">
                <span class="gs-footer-icon">🧬</span>
                <strong class="gs-footer-name">Genetic Scheduler</strong>
                <span class="gs-footer-sep">·</span>
                <span class="gs-footer-desc">Aplikasi Penyusunan Jadwal Perkuliahan Otomatis</span>
            </div>
            <div class="gs-footer-page">Halaman: <strong>{page_name}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_header():
    """Fungsi kompatibilitas untuk merender header default."""
    render_page_hero(
        title="Genetic Scheduler",
        subtitle="Susun jadwal perkuliahan otomatis dengan optimasi ruang dan dosen.",
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