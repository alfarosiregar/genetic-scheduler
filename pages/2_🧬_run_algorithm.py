"""Halaman konfigurasi parameter dan eksekusi optimasi Algoritma Genetika."""
import importlib
import time
import altair as alt
import pandas as pd
import streamlit as st
from config.settings import RUN_IMAGE_PATH
from utils.data_loader import load_databases
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from utils.storage import init_session_state, save_session_cache
from utils.genetic_algorithm import (
    run_genetic_algorithm,
    get_summary_stats,
    format_kromosom_detail,
)

st.set_page_config(
    page_title="Run Algorithm - Genetic Scheduler",
    page_icon="🧬",
    layout="wide",
)

init_session_state()

render_page_hero(
    title="Eksekusi Optimasi Algoritma Genetika",
    subtitle=(
        "Konfigurasikan parameter evolusi (Jumlah Generasi, Crossover Rate, dan Mutation Rate) "
        "untuk mencari susunan jadwal perkuliahan optimal tanpa bentrok."
    ),
    badge="🧬 Tahap 2 · Mesin Evolusi Genetika",
    image_path=RUN_IMAGE_PATH,
    active_step=2,
)

if "populasi_data" not in st.session_state or len(st.session_state.populasi_data) < 2:
    st.markdown(
        """
        <div style="background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 10px 16px; border-radius: 10px; font-size: 0.86rem; margin-bottom: 12px;">
            ⚠️ Dibutuhkan minimal <strong>2 data jadwal</strong> untuk menjalankan Algoritma Genetika.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_back1, c_back2 = st.columns([3.2, 1])
    with c_back1:
        st.markdown(
            """
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 10px 16px; border-radius: 10px; font-size: 0.86rem;">
                💡 Silakan tambahkan penugasan kuliah atau muat sampel cepat di halaman <strong>Input Data</strong> terlebih dahulu.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_back2:
        st.markdown('<div class="gs-mobile-spacer"></div>', unsafe_allow_html=True)
        if st.button("📊 Buka Input Data", type="primary", width="stretch"):
            st.switch_page("pages/1_📊_input_data.py")
    render_footer("Run Algorithm")
    st.stop()

databases = load_databases()

df_input = pd.DataFrame.from_dict(
    st.session_state.populasi_data,
    orient="index",
    columns=["Dosen", "Matkul", "Prodi"],
)
df_input.index.name = "Kode"

with st.expander(f"📋 Pratinjau Dataset Aktif ({len(df_input)} Jadwal Siap Dioptimasi)", expanded=len(df_input) > 0):
    st.dataframe(df_input, width="stretch", height=240)

# Preset parameter cepat
st.markdown('<div class="gs-section-title">⚡ Preset Parameter Cepat</div>', unsafe_allow_html=True)
p_col1, p_col2, p_col3 = st.columns(3)
with p_col1:
    if st.button("⚡ Cepat (10 Generasi)", width="stretch"):
        st.session_state.ga_config.update(
            {"generations": 10, "mutation_rate": 0.15, "crossover_rate": 0.80}
        )
        st.rerun()
with p_col2:
    if st.button("⚖️ Seimbang (25 Generasi · Rekomendasi)", width="stretch"):
        st.session_state.ga_config.update(
            {"generations": 25, "mutation_rate": 0.15, "crossover_rate": 0.80}
        )
        st.rerun()
with p_col3:
    if st.button("🎯 Intensif (50 Generasi · Dataset Besar)", width="stretch"):
        st.session_state.ga_config.update(
            {"generations": 50, "mutation_rate": 0.20, "crossover_rate": 0.85}
        )
        st.rerun()

# Input parameter Algoritma Genetika
st.markdown('<div class="gs-section-title">⚙️ Konfigurasi Parameter Algoritma Genetika</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    generations = st.number_input(
        "🔄 Jumlah Generasi Maksimum",
        min_value=1,
        max_value=100,
        value=int(st.session_state.ga_config.get("generations", 20)),
        help="Batas maksimum siklus evolusi yang akan dijalankan.",
    )
    st.session_state.ga_config["generations"] = generations

with col2:
    mutation_rate = st.slider(
        "🧪 Mutation Rate (per gen)",
        0.0,
        1.0,
        float(st.session_state.ga_config.get("mutation_rate", 0.15)),
        0.01,
        help="Probabilitas mutasi acak pada masing-masing gen penjadwalan (Rekomendasi: 0.10 - 0.20).",
    )
    st.session_state.ga_config["mutation_rate"] = mutation_rate

with col3:
    crossover_rate = st.slider(
        "🧬 Crossover Rate",
        0.0,
        1.0,
        float(st.session_state.ga_config.get("crossover_rate", 0.80)),
        0.05,
        help="Probabilitas rekombinasi one-cut-point antara dua induk terpilih (Rekomendasi: 0.70 - 0.90).",
    )
    st.session_state.ga_config["crossover_rate"] = crossover_rate

with col4:
    st.markdown(
        f"""
        <div class="gs-card" style="padding: 12px 16px; border-radius: 14px;">
            <div style="font-size: 0.82rem; font-weight: 600; color: #475569; margin-bottom: 4px;">
                📦 Ukuran Populasi
            </div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; line-height: 1.2;">
                {len(st.session_state.populasi_data)} Kromosom
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Eksekusi proses optimasi
if st.button("🚀 Jalankan Optimasi Algoritma Genetika Sekarang", type="primary", width="stretch"):
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(gen, total):
        pct = int(gen / total * 100)
        progress_bar.progress(min(pct, 100))
        status_text.markdown(f"⏳ **Sedang Mengevolusi Populasi:** Generasi `{gen}/{total}` ...")

    try:
        t_start = time.perf_counter()
        results = run_genetic_algorithm(
            st.session_state.populasi_data,
            databases,
            generations=generations,
            mutation_rate=mutation_rate,
            crossover_rate=crossover_rate,
            early_stopping=True,
            patience=generations + 1,
            seed=None,
            progress_callback=update_progress,
        )
        elapsed_ms = round((time.perf_counter() - t_start) * 1000, 1)
        results["elapsed_ms"] = elapsed_ms

        progress_bar.progress(100)
        st.session_state.ga_results = results
        save_session_cache()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat menjalankan algoritma: {str(e)}")
        st.stop()

# Tampilan ringkasan hasil optimasi
if "ga_results" in st.session_state and st.session_state.ga_results is not None:
    st.markdown("---")
    results = st.session_state.ga_results
    stats = get_summary_stats(results)
    elapsed_ms = results.get("elapsed_ms", 0)

    if stats["reached_optimal"]:
        st.markdown(
            f"""
            <div class="gs-banner-success" style="font-size: 0.88rem; padding: 14px 20px; gap: 12px;">
                <span>🎉 SOLUSI OPTIMAL TERCAPAI! Seluruh jadwal bebas konflik (Fitness = 1.0000) dalam {results['total_generations']} generasi.</span>
                <span style="flex-shrink: 0;">⚡ {elapsed_ms} ms</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="gs-banner-warn" style="font-size: 0.88rem; padding: 14px 20px; gap: 12px;">
                <span>📈 Evolusi selesai ({results['total_generations']} generasi). Tersisa {stats['final_konflik']} konflik dari {stats['initial_konflik']} konflik awal.</span>
                <span style="flex-shrink: 0;">⚡ {elapsed_ms} ms</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="gs-section-title">📊 Ringkasan Performa Optimasi</div>', unsafe_allow_html=True)
    fit_awal_str = f"{stats['initial_best_fitness']:.4f}"
    fit_akhir_str = f"{stats['final_best_fitness']:.4f}"
    fit_delta_str = f"+{stats['fitness_improvement']:.4f}"
    konf_awal_val = stats["initial_konflik"]
    konf_akhir_val = stats["final_konflik"]
    konf_diff = konf_awal_val - konf_akhir_val
    konf_delta_str = f"-{konf_diff} Konflik" if konf_diff > 0 else "0 Perubahan"
    gen_str = f"{results['total_generations']} Generasi"

    st.markdown(
        f"""
        <div class="gs-grid-5">
            <div class="gs-card gs-kpi-card">
                <div class="gs-kpi-label">🎯 Fitness Awal</div>
                <div class="gs-kpi-value" style="font-size: 1.35rem;">{fit_awal_str}</div>
                <div class="gs-kpi-sub">Generasi 0</div>
            </div>
            <div class="gs-card gs-kpi-card">
                <div class="gs-kpi-label">🏆 Fitness Akhir</div>
                <div class="gs-kpi-value" style="font-size: 1.35rem;">{fit_akhir_str}</div>
                <div class="gs-kpi-sub" style="font-weight: 600; color: #059669;">▲ {fit_delta_str}</div>
            </div>
            <div class="gs-card gs-kpi-card">
                <div class="gs-kpi-label">⚠️ Konflik Awal</div>
                <div class="gs-kpi-value" style="font-size: 1.35rem;">{konf_awal_val}</div>
                <div class="gs-kpi-sub">Sebelum Optimasi</div>
            </div>
            <div class="gs-card gs-kpi-card">
                <div class="gs-kpi-label">✅ Konflik Akhir</div>
                <div class="gs-kpi-value" style="font-size: 1.35rem;">{konf_akhir_val}</div>
                <div class="gs-kpi-sub" style="font-weight: 600; color: #059669;">▼ {konf_delta_str}</div>
            </div>
            <div class="gs-card gs-kpi-card">
                <div class="gs-kpi-label">🔄 Siklus Evolusi</div>
                <div class="gs-kpi-value" style="font-size: 1.35rem;">{gen_str}</div>
                <div class="gs-kpi-sub">Waktu: {elapsed_ms} ms</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gs-section-title">📈 Kurva Konvergensi Evolusi</div>', unsafe_allow_html=True)
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        chart_df = pd.DataFrame(
            {
                "Generasi": results["history"]["generations"],
                "Best Fitness": results["history"]["best_fitness"],
                "Average Fitness": results["history"]["avg_fitness"],
            }
        )
        fit_chart = (
            alt.Chart(chart_df.melt("Generasi", var_name="Metrik", value_name="Fitness"))
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("Generasi:Q", title="Generasi", axis=alt.Axis(tickMinStep=1, format="d")),
                y=alt.Y("Fitness:Q", title="Skor Fitness", scale=alt.Scale(domain=[0, 1.05])),
                color=alt.Color(
                    "Metrik:N",
                    scale=alt.Scale(domain=["Best Fitness", "Average Fitness"], range=["#4F46E5", "#10B981"]),
                ),
                tooltip=["Generasi:Q", "Metrik:N", alt.Tooltip("Fitness:Q", format=".4f")],
            )
            .properties(height=300, title="Progres Skor Fitness per Generasi")
            .interactive()
        )
        st.altair_chart(fit_chart, width="stretch")

    with ch_col2:
        konf_df = pd.DataFrame(
            {
                "Generasi": results["history"]["generations"],
                "Total Konflik": results["history"]["total_konflik"],
            }
        )
        konf_chart = (
            alt.Chart(konf_df)
            .mark_area(
                line={"color": "#EF4444", "strokeWidth": 3},
                point={"color": "#DC2626", "size": 60},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="rgba(239, 68, 68, 0.05)", offset=0),
                        alt.GradientStop(color="rgba(239, 68, 68, 0.45)", offset=1),
                    ],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
            )
            .encode(
                x=alt.X("Generasi:Q", title="Generasi", axis=alt.Axis(tickMinStep=1, format="d")),
                y=alt.Y("Total Konflik:Q", title="Total Konflik Jadwal"),
                tooltip=["Generasi:Q", "Total Konflik:Q"],
            )
            .properties(height=300, title="Penurunan Total Konflik per Generasi")
            .interactive()
        )
        st.altair_chart(konf_chart, width="stretch")

    with st.expander("🔍 Bandingkan Populasi Awal (Generasi 0) vs Populasi Akhir", expanded=False):
        c_awal, c_akhir = st.columns(2)
        with c_awal:
            st.markdown("**📋 Populasi Awal (Generasi 0 — Acak)**")
            df_awal = pd.DataFrame([format_kromosom_detail(k) for k in results["populasi_awal"]])
            st.dataframe(
                df_awal[["Kode", "Dosen", "Mata Kuliah", "Hari", "Waktu", "Ruangan", "Fitness", "Konflik"]],
                width="stretch",
                hide_index=True,
            )
        with c_akhir:
            st.markdown(f"**✨ Populasi Akhir (Generasi {results['total_generations']} — Teroptimasi)**")
            df_akhir = pd.DataFrame([format_kromosom_detail(k) for k in results["populasi_akhir"]])
            st.dataframe(
                df_akhir[["Kode", "Dosen", "Mata Kuliah", "Hari", "Waktu", "Ruangan", "Fitness", "Konflik"]],
                width="stretch",
                hide_index=True,
            )

    st.markdown("---")
    r_col1, r_col2 = st.columns([3, 1], vertical_alignment="center")
    with r_col1:
        st.markdown(
            """
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 12px 16px; border-radius: 10px; font-size: 0.90rem; line-height: 1.5;">
                ➡️ <strong>Langkah Berikutnya:</strong><br>
                Buka halaman <strong>Results</strong> untuk melihat Kalender Mingguan, Filter Jadwal, dan Unduh Excel/CSV.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r_col2:
        st.markdown('<div class="gs-mobile-spacer"></div>', unsafe_allow_html=True)
        if st.button("📈 Buka Analisis Lengkap (Results)", type="primary", width="stretch"):
            st.switch_page("pages/3_📈_results.py")

render_footer("Run Algorithm")