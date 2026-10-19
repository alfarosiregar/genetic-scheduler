"""Modul persistensi sesi otomatis (Auto-Persistence) agar data tidak hilang saat browser di-refresh."""
import json
import os
import streamlit as st
from config.settings import BASE_DIR

SESSION_CACHE_PATH = str(BASE_DIR / "mnt" / "db" / "session_cache.json")

DEFAULT_GA_CONFIG = {
    "generations": 20,
    "mutation_rate": 0.15,
    "crossover_rate": 0.80,
    "early_stopping": True,
    "patience": 5,
    "use_seed": False,
    "seed_value": 42,
}


def load_session_cache():
    """Membaca data sesi yang tersimpan dari disk secara aman."""
    if not os.path.exists(SESSION_CACHE_PATH):
        return None
    try:
        with open(SESSION_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_session_cache():
    """Menyimpan data populasi, konfigurasi GA, dan hasil GA dari session state ke disk."""
    try:
        cache_data = {
            "populasi_data": st.session_state.get("populasi_data", {}),
            "ga_config": st.session_state.get("ga_config", DEFAULT_GA_CONFIG),
            "ga_results": st.session_state.get("ga_results", None),
        }
        temp_path = f"{SESSION_CACHE_PATH}.tmp"
        os.makedirs(os.path.dirname(SESSION_CACHE_PATH), exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, SESSION_CACHE_PATH)
        return True
    except Exception:
        return False


def clear_session_cache():
    """Menghapus file cache sesi di disk dan membersihkan session state aktif."""
    try:
        if os.path.exists(SESSION_CACHE_PATH):
            os.remove(SESSION_CACHE_PATH)
    except Exception:
        pass
    temp_path = f"{SESSION_CACHE_PATH}.tmp"
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass


def init_session_state():
    """Inisialisasi session state dengan auto-restore dari disk jika sesi baru atau browser di-refresh."""
    if "populasi_data" not in st.session_state:
        cached = load_session_cache()
        if cached and isinstance(cached, dict):
            st.session_state.populasi_data = cached.get("populasi_data", {})
            st.session_state.ga_config = cached.get("ga_config", dict(DEFAULT_GA_CONFIG))
            if cached.get("ga_results") is not None:
                st.session_state.ga_results = cached["ga_results"]
        else:
            st.session_state.populasi_data = {}
            if "ga_config" not in st.session_state:
                st.session_state.ga_config = dict(DEFAULT_GA_CONFIG)
