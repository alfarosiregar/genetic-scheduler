"""Konfigurasi global path file, pemetaan kolom database, dan pengaturan halaman."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Lokasi file database dan aset gambar
DATABASE_PATH = str(BASE_DIR / 'mnt' / 'db' / 'Databases.xlsx')
KROMOSOM_PATH = str(BASE_DIR / 'mnt' / 'db' / 'Kromosom.xlsx')
APP_IMAGE_PATH = str(BASE_DIR / 'mnt' / 'img' / 'schedule_image.jpg')
INPUT_IMAGE_PATH = str(BASE_DIR / 'mnt' / 'img' / 'input_page_image.jpg')
RUN_IMAGE_PATH = str(BASE_DIR / 'mnt' / 'img' / 'run_page_image.jpg')
RESULT_IMAGE_PATH = str(BASE_DIR / 'mnt' / 'img' / 'result_page_image.jpg')
SETTING_IMAGE_PATH = str(BASE_DIR / 'mnt' / 'img' / 'settings_page_image.jpg')
SESSION_CACHE_PATH = str(BASE_DIR / 'mnt' / 'db' / 'session_cache.json')

# Indeks kolom pada Databases.xlsx (0-indexed)
COLUMN_MAPPING = {
    'dosen': 1,
    'matkul': 4,
    'sks': 16,
    'prodi': 7,
    'kelas': 10,
    'hari': 13,
    'waktu': 19,
    'ruangan': 22,
    'blok': 25
}

PAGE_TITLE = "Genetic Scheduler"
PAGE_ICON = "🧬"
LAYOUT = "wide"