"""Konfigurasi aplikasi"""

# Path files
DATABASE_PATH = 'mnt/db/Databases.xlsx'
KROMOSOM_PATH = 'mnt/db/Kromosom.xlsx'
IMAGE_PATH = 'mnt/img/schedule_image.jpg'

# Kolom mapping untuk Databases.xlsx
COLUMN_MAPPING = {
    'dosen': 1,      # Kolom B
    'matkul': 4,     # Kolom E
    'sks': 16,       # Kolom Q
    'prodi': 7,      # Kolom H
    'kelas': 10,     # Kolom K
    'hari': 13,      # Kolom N
    'waktu': 19,     # Kolom T
    'ruangan': 22,   # Kolom W
    'blok': 25       # Kolom Z
}

# Page config
PAGE_TITLE = "Genetic Scheduler"
PAGE_ICON = "🧬"
LAYOUT = "wide"