"""Algoritma Genetika untuk penjadwalan"""
import random


def buat_populasi_list(populasi_dict):
    """Konversi dictionary populasi ke list"""
    return [{"kode": k, "data": v} for k, v in populasi_dict.items()]


def hitung_konflik(krom, populasi):
    """Hitung jumlah konflik untuk kromosom"""
    konflik = 0
    for other in populasi:
        if krom["kode"] == other["kode"]:
            continue
        
        # Konflik ruang & waktu
        if (krom["data"][6] == other["data"][6] and 
            krom["data"][4] == other["data"][4] and 
            krom["data"][5] == other["data"][5]):
            konflik += 1
        
        # Konflik dosen & waktu
        if (krom["data"][0] == other["data"][0] and 
            krom["data"][4] == other["data"][4] and 
            krom["data"][5] == other["data"][5]):
            konflik += 1
    
    return konflik


def fitness(konflik):
    """Hitung nilai fitness"""
    return round(1 / (1 + konflik), 2)


def evaluasi_populasi(populasi):
    """Evaluasi fitness untuk semua kromosom"""
    for krom in populasi:
        konflik = hitung_konflik(krom, populasi)
        krom["konflik"] = konflik
        krom["fitness"] = fitness(konflik)
    return populasi


def seleksi_parent(populasi):
    """Pilih 2 parent terbaik"""
    return sorted(populasi, key=lambda x: x["fitness"], reverse=True)[:2]


def crossover(parent1, parent2):
    """Lakukan crossover untuk menghasilkan anak"""
    anak1 = {
        "kode": "A1",
        "data": parent1["data"][:4] + parent2["data"][4:]
    }
    anak2 = {
        "kode": "A2",
        "data": parent2["data"][:4] + parent1["data"][4:]
    }
    return [anak1, anak2]


def run_genetic_algorithm(populasi_data):
    """Jalankan algoritma genetika lengkap"""
    # Acak populasi awal
    items = list(populasi_data.items())
    random.shuffle(items)
    populasi_dict = dict(items)
    
    # Evaluasi populasi
    populasi = buat_populasi_list(populasi_dict)
    populasi = evaluasi_populasi(populasi)
    
    # Seleksi parent
    parent1, parent2 = seleksi_parent(populasi)
    
    # Crossover
    anak_list = crossover(parent1, parent2)
    anak_list = evaluasi_populasi(anak_list)
    
    return {
        'populasi': populasi,
        'parent1': parent1,
        'parent2': parent2,
        'anak_list': anak_list
    }