"""Halaman Input Data untuk menambah, mengimpor, dan mengelola daftar penugasan jadwal kuliah."""
import importlib
import pandas as pd
import streamlit as st
from config.settings import INPUT_IMAGE_PATH
from utils.data_loader import load_databases
from utils.storage import init_session_state, save_session_cache, clear_session_cache
import components.header as _hdr
import components.sidebar as _sb

if getattr(_hdr, "_HEADER_REV", 0) < 22 or getattr(_sb, "_SIDEBAR_REV", 0) < 22:
    importlib.reload(_hdr)
    importlib.reload(_sb)
from components.header import render_page_hero, render_footer
from components.sidebar import render_input_sidebar

st.set_page_config(
    page_title="Input Data - Genetic Scheduler",
    page_icon="📊",
    layout="wide",
)

init_session_state()

render_page_hero(
    title="Input Data Penugasan Kuliah",
    subtitle=(
        "Kelola daftar penugasan (Dosen, Mata Kuliah, Program Studi) yang akan dijadwalkan. "
        "Anda dapat menambahkan data secara manual, mengunggah file Excel, atau memuat dataset sampel."
    ),
    badge="📊 Tahap 1 · Persiapan Data",
    image_path=INPUT_IMAGE_PATH,
    active_step=1,
)

databases = load_databases()

submitted_sidebar = render_input_sidebar(databases)
if submitted_sidebar:
    st.rerun()


def _tambah_penugasan(dosen, matkul, prodi):
    """Menambahkan satu penugasan unik (dosen, mata kuliah, prodi) ke dalam state populasi."""
    for existing in st.session_state.populasi_data.values():
        if existing[0] == dosen and existing[1] == matkul and existing[2] == prodi:
            return False, None
    next_idx = len(st.session_state.populasi_data) + 1
    kode = f"C{next_idx}"
    while kode in st.session_state.populasi_data:
        next_idx += 1
        kode = f"C{next_idx}"
    st.session_state.populasi_data[kode] = [dosen, matkul, prodi]
    save_session_cache()
    return True, kode


# Tab metode input jadwal
st.markdown('<div class="gs-section-title">📥 Metode Input Jadwal</div>', unsafe_allow_html=True)
tab_manual, tab_excel, tab_sample = st.tabs(
    [
        "✍️ Input Manual (Form Utama)",
        "📁 Upload dari File Excel (.xlsx)",
        "⚡ Muat Sampel Cepat (Database)",
    ]
)

with tab_manual:
    if databases is not None:
        with st.form("main_manual_input_form", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                dosen_in = st.selectbox("👨‍🏫 Pilih Nama Dosen", databases["dosen"])
            with c2:
                matkul_in = st.selectbox("📘 Pilih Mata Kuliah", databases["matkul"])
            with c3:
                prodi_in = st.selectbox("🎓 Pilih Program Studi", databases["prodi"])

            btn_add_inline = st.form_submit_button("➕ Tambahkan Jadwal ke Daftar", type="primary", width="stretch")
            if btn_add_inline:
                ok, kode_baru = _tambah_penugasan(dosen_in, matkul_in, prodi_in)
                if ok:
                    st.success(f"✅ Berhasil menambahkan jadwal **{kode_baru}** ({dosen_in} — {matkul_in} — {prodi_in})!")
                    st.rerun()
                else:
                    st.warning("⚠️ Kombinasi Dosen, Mata Kuliah, dan Program Studi tersebut sudah ada dalam daftar.")

with tab_excel:
    up_col1, up_col2 = st.columns([2, 1])
    with up_col1:
        uploaded_file = st.file_uploader(
            "Unggah file Excel (.xlsx / .xls) dengan kolom: **Dosen** (atau **Nama Dosen**), **Matkul** (atau **Mata Kuliah**), dan **Prodi**",
            type=["xlsx", "xls"],
        )
    with up_col2:
        st.markdown("**📄 Template Unggahan**")
        st.caption("Unduh contoh format tabel jika Anda ingin menyiapkan data di Excel terlebih dahulu.")
        template_df = pd.DataFrame(
            {
                "Dosen": databases["dosen"][:3] if databases else ["Dosen A"],
                "Matkul": databases["matkul"][:3] if databases else ["Matkul A"],
                "Prodi": databases["prodi"][:3] if databases else ["PSB"],
            }
        )
        st.download_button(
            label="📥 Unduh Template CSV",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="template_input_jadwal.csv",
            mime="text/csv",
            width="stretch",
        )

    if uploaded_file is not None:
        try:
            df_upload = pd.read_excel(uploaded_file)
            col_map = {}
            for c in df_upload.columns:
                c_clean = str(c).strip().lower()
                if c_clean in ("dosen", "nama dosen"):
                    col_map["Dosen"] = c
                elif c_clean in ("matkul", "mata kuliah", "nama mata kuliah"):
                    col_map["Matkul"] = c
                elif c_clean in ("prodi", "program studi"):
                    col_map["Prodi"] = c

            required_keys = ["Dosen", "Matkul", "Prodi"]
            if all(k in col_map for k in required_keys):
                st.caption(f"Pratinjau file unggahan ({len(df_upload)} baris terdeteksi):")
                st.dataframe(df_upload.head(5), width="stretch")

                if st.button("➕ Impor Semua Baris Valid ke Daftar Jadwal", type="primary", width="stretch"):
                    added_count = 0
                    skipped_count = 0
                    for _, row in df_upload.iterrows():
                        dosen = str(row[col_map["Dosen"]]).strip()
                        matkul = str(row[col_map["Matkul"]]).strip()
                        prodi = str(row[col_map["Prodi"]]).strip()

                        if (
                            not dosen
                            or not matkul
                            or not prodi
                            or dosen.lower() == "nan"
                            or matkul.lower() == "nan"
                            or prodi.lower() == "nan"
                        ):
                            skipped_count += 1
                            continue

                        ok, _ = _tambah_penugasan(dosen, matkul, prodi)
                        if ok:
                            added_count += 1
                        else:
                            skipped_count += 1

                    if added_count > 0:
                        st.success(
                            f"✅ Berhasil mengimpor **{added_count} jadwal baru**!"
                            + (f" ({skipped_count} baris dilewati karena kosong/duplikat)" if skipped_count else "")
                        )
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Tidak ada jadwal baru yang ditambahkan ({skipped_count} baris kosong/duplikat).")
            else:
                missing = [k for k in required_keys if k not in col_map]
                st.error(f"❌ Kolom wajib tidak ditemukan: **{', '.join(missing)}**. Pastikan terdapat kolom Dosen, Matkul, dan Prodi.")
        except Exception as e:
            st.error(f"❌ Gagal membaca file Excel: {e}")

with tab_sample:
    st.markdown(
        "Gunakan fitur ini untuk memuat sampel penugasan nyata langsung dari dataset referensi (`Databases.xlsx` / `Kromosom.xlsx`) "
        "agar Anda dapat segera menguji performa Algoritma Genetika."
    )
    sc1, sc2 = st.columns([2, 1], vertical_alignment="bottom")
    with sc1:
        sample_size = st.slider(
            "Jumlah Jadwal Sampel yang Ingin Dimuat",
            min_value=5,
            max_value=80,
            value=20,
            step=5,
            help="Pilih berapa banyak kombinasi penugasan unik yang akan ditambahkan otomatis",
        )
    with sc2:
        if st.button(f"⚡ Muat {sample_size} Jadwal Sampel", type="primary", width="stretch"):
            if databases is not None:
                import random as _rnd

                added = 0
                attempts = 0
                while added < sample_size and attempts < sample_size * 10:
                    attempts += 1
                    d = _rnd.choice(databases["dosen"])
                    m = _rnd.choice(databases["matkul"])
                    p = _rnd.choice(databases["prodi"])
                    ok, _ = _tambah_penugasan(d, m, p)
                    if ok:
                        added += 1
                st.success(f"✅ Berhasil memuat {added} jadwal sampel ke dalam daftar!")
                st.rerun()

# Tabel manajemen jadwal aktif
st.markdown("---")
st.markdown('<div class="gs-section-title">📌 Daftar Jadwal yang Akan Dioptimasi</div>', unsafe_allow_html=True)

if len(st.session_state.populasi_data) == 0:
    st.markdown(
        """
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; padding: 10px 16px; border-radius: 10px; font-size: 0.86rem;">
            💡 Daftar jadwal masih kosong. Silakan tambahkan data melalui salah satu tab di atas atau melalui form di Sidebar kiri.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    df = pd.DataFrame.from_dict(
        st.session_state.populasi_data,
        orient="index",
        columns=["Dosen", "Matkul", "Prodi"],
    )
    df.index.name = "Kode"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("📋 Total Jadwal", len(df))
    with k2:
        st.metric("👨‍🏫 Dosen Unik", df["Dosen"].nunique())
    with k3:
        st.metric("📘 Mata Kuliah Unik", df["Matkul"].nunique())
    with k4:
        st.metric("🎓 Prodi Unik", df["Prodi"].nunique())

    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_q = st.text_input(
            "🔍 Cari Dosen / Mata Kuliah / Kode",
            placeholder="Ketik nama dosen, mata kuliah, atau kode kromosom...",
        )
    with f_col2:
        filter_prodi = st.multiselect(
            "🎓 Filter Program Studi",
            options=sorted(df["Prodi"].unique().tolist()),
            default=[],
        )

    df_view = df.copy()
    if search_q.strip():
        q = search_q.strip().lower()
        mask = (
            df_view.index.astype(str).str.lower().str.contains(q)
            | df_view["Dosen"].str.lower().str.contains(q)
            | df_view["Matkul"].str.lower().str.contains(q)
            | df_view["Prodi"].str.lower().str.contains(q)
        )
        df_view = df_view[mask]
    if filter_prodi:
        df_view = df_view[df_view["Prodi"].isin(filter_prodi)]

    st.dataframe(df_view, width="stretch", height=320)

    act1, act2, act3 = st.columns([2, 1, 1])
    with act1:
        del_keys = st.multiselect(
            "Pilih kode jadwal untuk dihapus tertentu:",
            options=list(st.session_state.populasi_data.keys()),
            placeholder="Pilih kode (mis. C1, C2)...",
            label_visibility="collapsed",
        )
        if del_keys and st.button(f"🗑️ Hapus {len(del_keys)} Jadwal Terpilih", width="stretch"):
            for k in del_keys:
                st.session_state.populasi_data.pop(k, None)
            new_pop = {}
            for i, val in enumerate(st.session_state.populasi_data.values(), 1):
                new_pop[f"C{i}"] = val
            st.session_state.populasi_data = new_pop
            save_session_cache()
            st.rerun()

    with act2:
        csv_bytes = df.to_csv(index=True).encode("utf-8")
        st.download_button(
            label="💾 Download CSV",
            data=csv_bytes,
            file_name="jadwal_input_data.csv",
            mime="text/csv",
            width="stretch",
        )

    with act3:
        if st.button("🗑️ Hapus Semua Data", type="secondary", width="stretch"):
            clear_session_cache()
            st.session_state.populasi_data = {}
            st.session_state.pop("ga_results", None)
            st.rerun()

st.markdown("---")
cta_col1, cta_col2 = st.columns([3.2, 1], vertical_alignment="center")
with cta_col1:
    if len(st.session_state.populasi_data) >= 2:
        st.markdown(
            f"""
            <div style="background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; padding: 10px 16px; border-radius: 10px; font-size: 0.86rem; line-height: 1.45;">
                ✅ <strong>{len(st.session_state.populasi_data)} jadwal siap dioptimasi!</strong> Lanjutkan ke halaman <strong>Run Algorithm</strong> untuk menjalankan proses evolusi.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; padding: 10px 16px; border-radius: 10px; font-size: 0.86rem; line-height: 1.45;">
                ⚠️ Tambahkan minimal <strong>2 jadwal</strong> sebelum menjalankan Algoritma Genetika.
            </div>
            """,
            unsafe_allow_html=True,
        )
with cta_col2:
    st.markdown('<div class="gs-mobile-spacer"></div>', unsafe_allow_html=True)
    if st.button("🧬 Lanjut ke Run Algorithm", type="primary", width="stretch"):
        st.switch_page("pages/2_🧬_run_algorithm.py")

render_footer("Input Data")