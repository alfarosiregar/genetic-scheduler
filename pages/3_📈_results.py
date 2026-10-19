"""Halaman Hasil Optimasi, Kalender Mingguan, Grafik Evolusi, dan Ekspor Laporan."""
import importlib
from io import BytesIO
import altair as alt
import pandas as pd
import streamlit as st
from config.settings import RESULT_IMAGE_PATH
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from utils.genetic_algorithm import (
    get_summary_stats,
    format_kromosom_detail,
    buat_tabel_rekomendasi_jadwal,
    parse_waktu,
)
from utils.pdf_generator import generate_weekly_calendar_pdf
from utils.storage import init_session_state

st.set_page_config(
    page_title="Results - Genetic Scheduler",
    page_icon="📈",
    layout="wide",
)

init_session_state()

render_page_hero(
    title="Hasil Optimasi & Kalender Jadwal Perkuliahan",
    subtitle=(
        "Eksplorasi jadwal hasil optimasi Algoritma Genetika dalam bentuk Tabel Rekomendasi Interaktif, "
        "Matriks Kalender Mingguan (Senin–Jumat), Grafik Konvergensi, dan Unduh Laporan Excel/CSV."
    ),
    badge="📈 Tahap 3 · Analitik & Jadwal Final",
    image_path=RESULT_IMAGE_PATH,
    active_step=3,
)

if "ga_results" not in st.session_state or st.session_state.ga_results is None:
    st.markdown(
        """
        <div style="background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 9px 14px; border-radius: 10px; font-size: 0.82rem; margin-bottom: 10px;">
            ⚠️ Belum ada hasil optimasi Algoritma Genetika yang tersimpan.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([3.2, 1])
    with c1:
        st.markdown(
            """
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 9px 14px; border-radius: 10px; font-size: 0.82rem;">
                💡 Silakan jalankan proses optimasi di halaman <strong>Run Algorithm</strong> terlebih dahulu.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="gs-mobile-spacer"></div>', unsafe_allow_html=True)
        if st.button("🧬 Buka Run Algorithm", type="primary", width="stretch"):
            st.switch_page("pages/2_🧬_run_algorithm.py")
    render_footer("Results")
    st.stop()

results = st.session_state.ga_results
stats = get_summary_stats(results)
tabel_rekomendasi = buat_tabel_rekomendasi_jadwal(results)
df_rekomendasi = pd.DataFrame(tabel_rekomendasi)

# Ringkasan eksekutif hasil optimasi
if stats["reached_optimal"]:
    st.markdown(
        """
        <div class="gs-banner-success" style="font-size: 0.88rem; padding: 14px 20px; gap: 12px;">
            <span>🎉 SEMPURNA! Seluruh jadwal perkuliahan telah OPTIMAL (0 Konflik · Fitness 1.0000) dan siap digunakan!</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="gs-banner-warn" style="font-size: 0.88rem; padding: 14px 20px; gap: 12px;">
            <span>⚠️ Jadwal Suboptimal: Masih terdapat {stats['final_konflik']} konflik yang perlu ditinjau atau dioptimasi ulang.</span>
            <span style="flex-shrink: 0;">⚠️ PERLU EVALUASI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="gs-section-title">🎯 Ringkasan Eksekutif</div>', unsafe_allow_html=True)

fitness_improvement = float(stats["fitness_improvement"])
initial_konflik = int(stats["initial_konflik"])
final_konflik = int(stats["final_konflik"])
konf_diff = initial_konflik - final_konflik
konf_delta_str = f"-{konf_diff} Konflik" if konf_diff > 0 else "0 Perubahan"
improvement_pct = float(results["improvement"]["improvement_percentage"])
jadwal_optimal = int((df_rekomendasi["Konflik"] == 0).sum())
total_jadwal = len(df_rekomendasi)

st.markdown(
    f"""
    <div class="gs-grid-5">
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">🔄 Generasi Dijalankan</div>
            <div class="gs-kpi-value" style="font-size: 1.35rem;">{results['total_generations']} Generasi</div>
            <div class="gs-kpi-sub">Siklus Evolusi</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">🏆 Rata-Rata Fitness</div>
            <div class="gs-kpi-value" style="font-size: 1.35rem;">{stats['final_best_fitness']:.4f}</div>
            <div class="gs-kpi-sub" style="font-weight: 600; color: #059669;">▲ +{fitness_improvement:.4f}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">⚡ Total Konflik Akhir</div>
            <div class="gs-kpi-value" style="font-size: 1.35rem;">{final_konflik}</div>
            <div class="gs-kpi-sub" style="font-weight: 600; color: #059669;">▼ {konf_delta_str}</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">📈 Peningkatan Kualitas</div>
            <div class="gs-kpi-value" style="font-size: 1.35rem;">+{improvement_pct}%</div>
            <div class="gs-kpi-sub">Dari Populasi Awal</div>
        </div>
        <div class="gs-card gs-kpi-card">
            <div class="gs-kpi-label">✅ Kelas Bebas Bentrok</div>
            <div class="gs-kpi-value" style="font-size: 1.35rem;">{jadwal_optimal}/{total_jadwal}</div>
            <div class="gs-kpi-sub">Jadwal Teroptimasi</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

progress_data = []
for i, gen in enumerate(results["history"]["generations"]):
    progress_data.append(
        {
            "Generasi": gen,
            "Best Fitness": results["history"]["best_fitness"][i],
            "Avg Fitness": results["history"]["avg_fitness"][i],
            "Worst Fitness": results["history"]["worst_fitness"][i],
            "Total Konflik": results["history"]["total_konflik"][i],
            "Improvement": round(results["history"]["avg_fitness"][i] - results["history"]["avg_fitness"][0], 4)
            if i > 0
            else 0.0,
        }
    )
df_progress = pd.DataFrame(progress_data)

# Tab eksplorasi jadwal, kalender, grafik, dan riwayat generasi
tab_table, tab_calendar, tab_charts, tab_history = st.tabs(
    [
        "📋 Tabel Rekomendasi Jadwal",
        "🗓️ Kalender Mingguan (Per Hari)",
        "📈 Grafik Evolusi & Distribusi",
        "🔍 Riwayat Generasi & Detail",
    ]
)

with tab_table:
    f1, f2, f3, f4 = st.columns([1.4, 1.1, 1.1, 1.2])
    with f1:
        q_search = st.text_input(
            "🔍 Cari Dosen / Mata Kuliah / Ruangan",
            placeholder="Ketik kata kunci pencarian...",
        )
    with f2:
        hari_order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
        hari_avail = sorted(
            df_rekomendasi["Hari"].unique().tolist(),
            key=lambda h: hari_order.index(h) if h in hari_order else 99,
        )
        f_hari = st.multiselect("📅 Filter Hari", options=hari_avail, default=[])
    with f3:
        f_prodi = st.multiselect(
            "🎓 Filter Prodi",
            options=sorted(df_rekomendasi["Prodi"].unique().tolist()),
            default=[],
        )
    with f4:
        f_status = st.selectbox(
            "🚦 Status Konflik",
            options=["Semua Jadwal", "Hanya Optimal (0 Konflik)", "Hanya Berkonflik (> 0)"],
        )

    df_filtered = df_rekomendasi.copy()
    if q_search.strip():
        q = q_search.strip().lower()
        df_filtered = df_filtered[
            df_filtered["Dosen"].str.lower().str.contains(q)
            | df_filtered["Mata Kuliah"].str.lower().str.contains(q)
            | df_filtered["Ruangan"].astype(str).str.lower().str.contains(q)
        ]
    if f_hari:
        df_filtered = df_filtered[df_filtered["Hari"].isin(f_hari)]
    if f_prodi:
        df_filtered = df_filtered[df_filtered["Prodi"].isin(f_prodi)]
    if f_status == "Hanya Optimal (0 Konflik)":
        df_filtered = df_filtered[df_filtered["Konflik"] == 0]
    elif f_status == "Hanya Berkonflik (> 0)":
        df_filtered = df_filtered[df_filtered["Konflik"] > 0]

    def highlight_konflik(row):
        if row["Konflik"] > 0:
            return ["background-color: #FEE2E2; color: #991B1B; font-weight: 600;"] * len(row)
        elif row["Fitness"] >= 0.99:
            return ["background-color: #ECFDF5; color: #065F46;"] * len(row)
        return [""] * len(row)

    st.caption(f"Menampilkan **{len(df_filtered)}** dari total **{len(df_rekomendasi)}** jadwal perkuliahan.")
    st.dataframe(
        df_filtered.style.apply(highlight_konflik, axis=1).format({"Fitness": "{:.4f}"}),
        width="stretch",
        height=420,
        hide_index=True,
    )

    leg1, leg2 = st.columns(2)
    with leg1:
        st.markdown("🟢 **Hijau:** Jadwal optimal bebas bentrok (`Konflik = 0`, `Fitness = 1.0000`)")
    with leg2:
        st.markdown("🔴 **Merah:** Jadwal memiliki bentrok waktu pada ruangan, dosen, atau prodi yang sama")

with tab_calendar:
    st.markdown(
        "Visualisasi papan jadwal perkuliahan mingguan yang diurutkan secara kronologis berdasarkan **Hari** dan **Jam Mulai**."
    )
    col_filter, col_dl_pdf = st.columns([2.5, 1.2], vertical_alignment="bottom")
    with col_filter:
        cal_prodi = st.selectbox(
            "🎓 Filter Kalender Berdasarkan Program Studi (Opsional):",
            options=["Semua Program Studi"] + sorted(df_rekomendasi["Prodi"].unique().tolist()),
        )

    df_cal = df_rekomendasi.copy()
    if cal_prodi != "Semua Program Studi":
        df_cal = df_cal[df_cal["Prodi"] == cal_prodi]

    with col_dl_pdf:
        cal_pdf_bytes = generate_weekly_calendar_pdf(df_cal, prodi_filter=cal_prodi, stats=stats)
        file_suffix = cal_prodi.lower().replace(" ", "_") if cal_prodi != "Semua Program Studi" else "semua_prodi"
        st.download_button(
            label="📄 Unduh Kalender PDF (Landscape)",
            data=cal_pdf_bytes,
            file_name=f"kalender_mingguan_{file_suffix}.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
        )

    df_cal["_sort_menit"] = df_cal["Waktu"].apply(lambda w: (parse_waktu(w) or (9999, 9999))[0])
    hari_cols_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    extra_days = [h for h in df_cal["Hari"].unique() if h not in hari_cols_list]
    all_days = hari_cols_list + extra_days

    day_columns = st.columns(len(all_days))
    for idx_d, nama_hari in enumerate(all_days):
        with day_columns[idx_d]:
            df_hari = df_cal[df_cal["Hari"] == nama_hari].sort_values("_sort_menit")
            st.markdown(f"#### 📅 {nama_hari} ({len(df_hari)})")
            if len(df_hari) == 0:
                st.caption("Tidak ada kelas terjadwal.")
            else:
                for _, r in df_hari.iterrows():
                    konflik_cls = "conflict" if r["Konflik"] > 0 else ""
                    badge_konf = f" · ⚠️ {r['Konflik']} Konflik" if r["Konflik"] > 0 else ""
                    st.markdown(
                        f"""
                        <div class="gs-slot-card {konflik_cls}">
                            <div class="gs-slot-time">⏰ {r['Waktu']}{badge_konf}</div>
                            <div class="gs-slot-course">{r['Mata Kuliah']}</div>
                            <div class="gs-slot-meta">
                                👨‍🏫 {r['Dosen']}<br>
                                🏢 Ruang <strong>{r['Ruangan']}</strong> · 🎓 {r['Prodi']} ({r['SKS']} SKS)
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

with tab_charts:
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        chart_data = pd.DataFrame(
            {
                "Generasi": results["history"]["generations"],
                "Best Fitness": results["history"]["best_fitness"],
                "Average Fitness": results["history"]["avg_fitness"],
                "Worst Fitness": results["history"]["worst_fitness"],
            }
        )
        line_chart = (
            alt.Chart(chart_data.melt("Generasi", var_name="Tipe", value_name="Fitness"))
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("Generasi:Q", title="Generasi", axis=alt.Axis(tickMinStep=1, format="d")),
                y=alt.Y("Fitness:Q", title="Skor Fitness", scale=alt.Scale(domain=[0, 1.05])),
                color=alt.Color(
                    "Tipe:N",
                    legend=alt.Legend(title="Metrik Fitness"),
                    scale=alt.Scale(
                        domain=["Best Fitness", "Average Fitness", "Worst Fitness"],
                        range=["#4F46E5", "#10B981", "#F59E0B"],
                    ),
                ),
                tooltip=["Generasi:Q", "Tipe:N", alt.Tooltip("Fitness:Q", format=".4f")],
            )
            .properties(height=340, title="Evolusi Fitness (Best, Average, Worst)")
            .interactive()
        )
        st.altair_chart(line_chart, width="stretch")

    with g_col2:
        konflik_data = pd.DataFrame(
            {
                "Generasi": results["history"]["generations"],
                "Jumlah Konflik": results["history"]["total_konflik"],
            }
        )
        konflik_chart = (
            alt.Chart(konflik_data)
            .mark_area(
                line={"color": "#DC2626", "strokeWidth": 3},
                point={"color": "#B91C1C", "size": 60},
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
                y=alt.Y("Jumlah Konflik:Q", title="Total Konflik Populasi"),
                tooltip=["Generasi:Q", "Jumlah Konflik:Q"],
            )
            .properties(height=340, title="Penurunan Total Konflik per Generasi")
            .interactive()
        )
        st.altair_chart(konflik_chart, width="stretch")

    st.markdown("---")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        dist_hari = df_rekomendasi.groupby("Hari", as_index=False).size().rename(columns={"size": "Jumlah Kelas"})
        bar_hari = (
            alt.Chart(dist_hari)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#4F46E5")
            .encode(
                x=alt.X("Hari:N", sort=["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], title="Hari Perkuliahan"),
                y=alt.Y("Jumlah Kelas:Q", title="Jumlah Kelas Terjadwal"),
                tooltip=["Hari:N", "Jumlah Kelas:Q"],
            )
            .properties(height=280, title="Distribusi Kepadatan Kelas per Hari")
        )
        st.altair_chart(bar_hari, width="stretch")

    with d_col2:
        dist_prodi = df_rekomendasi.groupby("Prodi", as_index=False).size().rename(columns={"size": "Jumlah Kelas"})
        bar_prodi = (
            alt.Chart(dist_prodi)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#10B981")
            .encode(
                x=alt.X("Prodi:N", sort="-y", title="Program Studi"),
                y=alt.Y("Jumlah Kelas:Q", title="Jumlah Kelas"),
                tooltip=["Prodi:N", "Jumlah Kelas:Q"],
            )
            .properties(height=280, title="Distribusi Jadwal per Program Studi")
        )
        st.altair_chart(bar_prodi, width="stretch")

with tab_history:
    st.markdown("#### 📋 Tabel Progres Evolusi per Generasi")

    def highlight_best(row):
        if row["Avg Fitness"] == df_progress["Avg Fitness"].max():
            return ["background-color: #DCFCE7; color: #065F46; font-weight: 600;"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_progress.style.apply(highlight_best, axis=1).format(
            {
                "Best Fitness": "{:.4f}",
                "Avg Fitness": "{:.4f}",
                "Worst Fitness": "{:.4f}",
                "Improvement": "{:+.4f}",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("#### 🔄 Perbandingan Populasi Awal (Generasi 0) vs Populasi Akhir")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("**🔴 Populasi Awal (Generasi 0 — Sebelum Optimasi)**")
        df_awal = pd.DataFrame([format_kromosom_detail(k) for k in results["populasi_awal"]])
        st.dataframe(
            df_awal[["Kode", "Dosen", "Mata Kuliah", "Hari", "Waktu", "Ruangan", "Fitness", "Konflik"]],
            width="stretch",
            height=300,
            hide_index=True,
        )
    with col_p2:
        st.markdown(f"**🟢 Populasi Akhir (Generasi {results['total_generations']} — Sesudah Optimasi)**")
        df_akhir = pd.DataFrame([format_kromosom_detail(k) for k in results["populasi_akhir"]])
        st.dataframe(
            df_akhir[["Kode", "Dosen", "Mata Kuliah", "Hari", "Waktu", "Ruangan", "Fitness", "Konflik"]],
            width="stretch",
            height=300,
            hide_index=True,
        )

# Bagian unduhan laporan Excel, PDF, dan CSV
st.markdown("---")
st.markdown('<div class="gs-section-title">💾 Pusat Unduhan Laporan (Excel, PDF & CSV)</div>', unsafe_allow_html=True)

dl_col1, dl_col2, dl_col3, dl_col4 = st.columns(4)

with dl_col1:
    excel_buf = BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_rekomendasi.to_excel(writer, index=False, sheet_name="Jadwal_Rekomendasi")
        df_progress.to_excel(writer, index=False, sheet_name="Riwayat_Evolusi")
    st.download_button(
        label="📗 Laporan Lengkap (.xlsx)",
        data=excel_buf.getvalue(),
        file_name="rekomendasi_jadwal_kuliah.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        width="stretch",
    )

with dl_col2:
    full_pdf_bytes = generate_weekly_calendar_pdf(df_rekomendasi, prodi_filter="Semua Program Studi", stats=stats)
    st.download_button(
        label="📄 Kalender PDF (Landscape)",
        data=full_pdf_bytes,
        file_name="kalender_jadwal_kuliah_landscape.pdf",
        mime="application/pdf",
        type="primary",
        width="stretch",
    )

with dl_col3:
    tabel_csv = df_rekomendasi.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Rekomendasi (.csv)",
        data=tabel_csv,
        file_name="rekomendasi_jadwal_kuliah.csv",
        mime="text/csv",
        width="stretch",
    )

with dl_col4:
    progress_csv = df_progress.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📊 Riwayat Evolusi (.csv)",
        data=progress_csv,
        file_name="evolution_progress.csv",
        mime="text/csv",
        width="stretch",
    )

render_footer("Results")