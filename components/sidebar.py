"""
Modern Interactive Sidebar Component (Global Session Monitor + Quick Schedule Input)
"""
import importlib
import random
import streamlit as st
import components.header as _hdr

if not hasattr(_hdr, "_main_shell_scope"):
    importlib.reload(_hdr)
from components.header import _main_shell_scope
from utils.data_loader import load_databases


def _render_sidebar_header_and_monitor():
    """Render Brand Card & Live Session Monitor di bagian atas Sidebar (persistent shell)."""
    pop_data = st.session_state.get("populasi_data", {})
    pop_count = len(pop_data)
    ga_results = st.session_state.get("ga_results")
    ga_cfg = st.session_state.get(
        "ga_config",
        {"generations": 20, "mutation_rate": 0.15, "crossover_rate": 0.80, "early_stopping": True},
    )

    if ga_results is not None:
        konf_akhir = ga_results["history"]["total_konflik"][-1]
        fit_akhir = ga_results["history"]["avg_fitness"][-1]
        status_label = "OPTIMAL" if konf_akhir == 0 else f"{konf_akhir} KONFLIK"
        fit_label = f"{fit_akhir:.2f}"
        pct_ready = 100 if konf_akhir == 0 else 75
    else:
        status_label = "SIAP" if pop_count >= 2 else "INPUT"
        fit_label = "—"
        pct_ready = min(int((pop_count / 10) * 100), 100) if pop_count > 0 else 8

    with _main_shell_scope():
        st.sidebar.markdown(
            f"""
            <div class="gs-sb-brand">
                <div class="gs-sb-brand-top">
                    <span class="gs-sb-brand-title">🧬 Genetic Scheduler</span>
                </div>
                <div class="gs-sb-brand-sub">AI Course Timetable Optimizer</div>
            </div>

            <div class="gs-sb-card">
                <div class="gs-sb-card-header">
                    <span>📡 Live Session Monitor</span>
                    <span>{status_label}</span>
                </div>
                <div class="gs-sb-stat-grid">
                    <div class="gs-sb-stat-box">
                        <div class="gs-sb-stat-val">{pop_count}</div>
                        <div class="gs-sb-stat-lbl">Jadwal Aktif</div>
                    </div>
                    <div class="gs-sb-stat-box">
                        <div class="gs-sb-stat-val">{fit_label}</div>
                        <div class="gs-sb-stat-lbl">Avg Fitness</div>
                    </div>
                </div>
                <div class="gs-sb-progress-wrap">
                    <div class="gs-sb-progress-bar" style="width: {pct_ready}%;"></div>
                </div>
                <div class="gs-sb-chip-row" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; margin-top: 8px;">
                    <span class="gs-sb-chip" style="text-align: center; white-space: nowrap; padding: 3px 4px; font-size: 0.68rem;">🔄 {ga_cfg.get('generations', 20)} Gen</span>
                    <span class="gs-sb-chip" style="text-align: center; white-space: nowrap; padding: 3px 4px; font-size: 0.68rem;">🧪 Mut {int(ga_cfg.get('mutation_rate', 0.15)*100)}%</span>
                    <span class="gs-sb-chip" style="text-align: center; white-space: nowrap; padding: 3px 4px; font-size: 0.68rem;">🧬 Cross {int(ga_cfg.get('crossover_rate', 0.80)*100)}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_quick_add_form(databases, expanded=True):
    """Render form tambah jadwal cepat di sidebar."""
    if databases is None:
        return False

    if "populasi_data" not in st.session_state:
        st.session_state.populasi_data = {}

    container = st.sidebar.container() if expanded else st.sidebar.expander("➕ Tambah Jadwal Cepat", expanded=False)
    with container:
        if expanded:
            st.markdown("#### ➕ Tambah Jadwal Cepat")
        with st.form("sidebar_quick_input_form", clear_on_submit=False):
            dosen_options = databases["dosen"]
            matkul_options = databases["matkul"]
            prodi_options = databases["prodi"]

            if not dosen_options or not matkul_options or not prodi_options:
                st.error("❌ Database kosong.")
                return False

            idx_dosen = st.selectbox(
                "👨‍🏫 Nama Dosen",
                range(len(dosen_options)),
                format_func=lambda i: dosen_options[i],
            )
            idx_matkul = st.selectbox(
                "📘 Mata Kuliah",
                range(len(matkul_options)),
                format_func=lambda i: matkul_options[i],
            )
            idx_prodi = st.selectbox(
                "🎓 Program Studi",
                range(len(prodi_options)),
                format_func=lambda i: prodi_options[i],
            )

            dosen = dosen_options[idx_dosen]
            matkul = matkul_options[idx_matkul]
            prodi = prodi_options[idx_prodi]

            submitted = st.form_submit_button("➕ Tambahkan Jadwal", type="primary", width="stretch")

            if submitted:
                for existing in st.session_state.populasi_data.values():
                    if existing[0] == dosen and existing[1] == matkul and existing[2] == prodi:
                        st.warning("⚠️ Kombinasi jadwal sudah ada!")
                        return False

                next_idx = len(st.session_state.populasi_data) + 1
                kode = f"C{next_idx}"
                while kode in st.session_state.populasi_data:
                    next_idx += 1
                    kode = f"C{next_idx}"

                st.session_state.populasi_data[kode] = [dosen, matkul, prodi]
                st.success(f"✅ Jadwal {kode} ditambahkan!")
                return True

        # Tombol Muat 15 Sampel Instan di Sidebar jika belum ada data
        if len(st.session_state.populasi_data) < 5:
            if st.button("⚡ Muat 15 Sampel Instan", width="stretch", key="sb_quick_sample_btn"):
                added = 0
                attempts = 0
                while added < 15 and attempts < 150:
                    attempts += 1
                    d = random.choice(databases["dosen"])
                    m = random.choice(databases["matkul"])
                    p = random.choice(databases["prodi"])
                    if not any(ex[0] == d and ex[1] == m and ex[2] == p for ex in st.session_state.populasi_data.values()):
                        next_idx = len(st.session_state.populasi_data) + 1
                        kode = f"C{next_idx}"
                        while kode in st.session_state.populasi_data:
                            next_idx += 1
                            kode = f"C{next_idx}"
                        st.session_state.populasi_data[kode] = [d, m, p]
                        added += 1
                return True

    return False


def render_global_sidebar(active_step=0, databases=None):
    """
    Render sidebar terpadu di semua halaman (dipanggil otomatis oleh render_page_hero
    pada halaman selain Input Data, atau melalui render_input_sidebar pada halaman Input Data).
    """
    if st.session_state.get("_sb_rendered_this_run"):
        return False
    st.session_state["_sb_rendered_this_run"] = True

    _render_sidebar_header_and_monitor()
    if databases is None:
        databases = load_databases()
    return _render_quick_add_form(databases, expanded=(active_step == 1))


def render_input_sidebar(databases):
    """Fungsi sidebar khusus halaman Input Data (kompatibel penuh dengan pemanggilan lama)."""
    st.session_state["_sb_rendered_this_run"] = True
    _render_sidebar_header_and_monitor()
    return _render_quick_add_form(databases, expanded=True)