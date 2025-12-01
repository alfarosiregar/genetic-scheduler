"""Fungsi untuk load data dari Excel"""
import streamlit as st
import pandas as pd
from config.settings import DATABASE_PATH, KROMOSOM_PATH, COLUMN_MAPPING


@st.cache_data
def load_kromosom_data():
    """Load data dari Kromosom.xlsx"""
    try:
        df = pd.read_excel(KROMOSOM_PATH)
        return df
    except FileNotFoundError:
        st.error("❌ File 'Kromosom.xlsx' tidak ditemukan!")
        return None
    except Exception as e:
        st.error(f"❌ Error membaca Kromosom.xlsx: {e}")
        return None


@st.cache_data
def load_databases():
    """Load dan gabungkan data dari Kromosom.xlsx dan Databases.xlsx"""
    try:
        df_kromosom = pd.read_excel(KROMOSOM_PATH)
        df_databases = pd.read_excel(DATABASE_PATH)
        
        # Ambil data unik dari Databases.xlsx
        data = {}
        for key, col_index in COLUMN_MAPPING.items():
            if len(df_databases.columns) > col_index:
                unique_values = df_databases.iloc[:, col_index].dropna().unique().tolist()
                data[key] = [f"{i+1} - {str(val)}" for i, val in enumerate(unique_values)]
            else:
                data[key] = ['Data kosong']
        
        # Tambahkan opsi kosong untuk blok
        data['blok'] = [''] + data.get('blok', [])
        
        return data
    except FileNotFoundError as e:
        st.sidebar.error(f"❌ File tidak ditemukan: {e}")
        return None
    except Exception as e:
        st.sidebar.error(f"❌ Error membaca file: {e}")
        return None