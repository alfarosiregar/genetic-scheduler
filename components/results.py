"""Komponen tabel dan kartu untuk menampilkan hasil evaluasi Algoritma Genetika."""
import streamlit as st
import pandas as pd


def display_populasi_awal(populasi_data):
    """Menampilkan tabel populasi awal."""
    st.markdown("### 📌 Populasi Awal")
    if len(populasi_data) == 0:
        st.info("Belum ada data. Silakan tambahkan dari sidebar.")
    else:
        df_pop = pd.DataFrame.from_dict(
            populasi_data, orient="index",
            columns=["Dosen", "Mata Kuliah", "SKS", "Prodi", "Hari", "Waktu", "Ruangan", "Blok"]
        )
        st.dataframe(df_pop, width='stretch')


def display_evaluasi(populasi):
    """Menampilkan tabel evaluasi konflik dan nilai fitness populasi."""
    st.markdown("### 🔍 Evaluasi Populasi (Konflik & Fitness)")
    df_eval = pd.DataFrame([{
        "Kode": p["kode"],
        "Dosen": p["data"][0],
        "Matkul": p["data"][1],
        "Prodi": p["data"][2],
        "Hari": p["data"][4],
        "Waktu": p["data"][5],
        "Ruangan": p["data"][6],
        "Konflik": p["konflik"],
        "Fitness": p["fitness"]
    } for p in populasi])
    st.dataframe(df_eval, width='stretch')


def display_parents(parent1, parent2):
    """Menampilkan pasangan kromosom induk terpilih."""
    st.markdown("### 🧬 Parent Terpilih")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔵 Parent 1**")
        st.write(f"• **Kode:** {parent1['kode']}")
        st.write(f"• **Dosen:** {parent1['data'][0]}")
        st.write(f"• **Matkul:** {parent1['data'][1]}")
        st.write(f"• **Prodi:** {parent1['data'][2]}")
        st.write(f"• **Fitness:** {parent1['fitness']}")

    with col2:
        st.markdown("**🟢 Parent 2**")
        st.write(f"• **Kode:** {parent2['kode']}")
        st.write(f"• **Dosen:** {parent2['data'][0]}")
        st.write(f"• **Matkul:** {parent2['data'][1]}")
        st.write(f"• **Prodi:** {parent2['data'][2]}")
        st.write(f"• **Fitness:** {parent2['fitness']}")


def display_offspring(anak_list):
    """Menampilkan tabel individu anak hasil crossover."""
    st.markdown("### 🧫 Anak Setelah Crossover")
    df_anak = pd.DataFrame([{
        "Kode": a["kode"],
        "Dosen": a["data"][0],
        "Matkul": a["data"][1],
        "Prodi": a["data"][2],
        "Hari": a["data"][4],
        "Waktu": a["data"][5],
        "Ruangan": a["data"][6],
        "Konflik": a["konflik"],
        "Fitness": a["fitness"]
    } for a in anak_list])
    st.dataframe(df_anak, width='stretch')