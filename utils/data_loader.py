"""Utilitas pemuatan data jadwal dan referensi dari file Excel."""
import streamlit as st
import pandas as pd
from config.settings import DATABASE_PATH, KROMOSOM_PATH, COLUMN_MAPPING


@st.cache_data
def load_kromosom_data():
    """Memuat tabel kromosom dari Kromosom.xlsx."""
    try:
        return pd.read_excel(KROMOSOM_PATH)
    except FileNotFoundError:
        st.error("❌ File 'Kromosom.xlsx' tidak ditemukan!")
        return None
    except Exception as e:
        st.error(f"❌ Error membaca Kromosom.xlsx: {e}")
        return None


@st.cache_data
def load_databases():
    """Memuat daftar unik atribut penjadwalan dari Databases.xlsx."""
    try:
        df_databases = pd.read_excel(DATABASE_PATH)

        data = {}
        for key, col_index in COLUMN_MAPPING.items():
            if len(df_databases.columns) > col_index:
                unique_values = df_databases.iloc[:, col_index].dropna().unique().tolist()
                data[key] = [str(val).strip() for val in unique_values]
            else:
                data[key] = ['Data kosong']

        data['blok'] = [''] + data.get('blok', [])

        # Pemetaan SKS per mata kuliah dari dataset referensi
        matkul_sks = {}
        try:
            df_kr = pd.read_excel(KROMOSOM_PATH)
            id_to_nama = {
                int(r['Kode.1']): str(r['Nama Mata Kuliah']).strip()
                for _, r in df_databases[['Kode.1', 'Nama Mata Kuliah']].dropna().iterrows()
                if str(r['Kode.1']).isdigit()
            }
            for m_id, grp in df_kr.groupby('Mata Kuliah'):
                if int(m_id) in id_to_nama:
                    matkul_sks[id_to_nama[int(m_id)]] = int(grp['SKS'].mode()[0])
        except Exception:
            pass
        data['matkul_sks'] = matkul_sks

        return data
    except FileNotFoundError as e:
        st.sidebar.error(f"❌ File tidak ditemukan: {e}")
        return None
    except Exception as e:
        st.sidebar.error(f"❌ Error membaca file: {e}")
        return None