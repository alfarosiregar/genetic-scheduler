"""Mesin optimasi jadwal kuliah berbasis Algoritma Genetika (GA)."""

import random

# Indeks atribut dalam array data kromosom: [dosen, matkul, prodi, sks, hari, waktu, ruangan]
IDX_DOSEN = 0
IDX_MATKUL = 1
IDX_PRODI = 2
IDX_SKS = 3
IDX_HARI = 4
IDX_WAKTU = 5
IDX_RUANGAN = 6

# Pemetaan indeks gen yang diacak/dimutasi ke kunci database (hanya hari, waktu, dan ruangan)
GENE_MAP = {
    IDX_HARI: 'hari',
    IDX_WAKTU: 'waktu',
    IDX_RUANGAN: 'ruangan',
}

_WAKTU_CACHE = {}


def get_sks_for_matkul(matkul_name, databases, default_sks=2):
    """Mendapatkan nilai SKS konsisten untuk suatu mata kuliah."""
    if databases and isinstance(databases, dict) and "matkul_sks" in databases:
        return databases["matkul_sks"].get(matkul_name, default_sks)
    return default_sks


def parse_waktu(slot_waktu):
    """Mengubah string rentang waktu ('HH.MM-HH.MM') menjadi tuple menit (mulai, selesai)."""
    if slot_waktu in _WAKTU_CACHE:
        return _WAKTU_CACHE[slot_waktu]

    hasil = None
    try:
        kiri, kanan = str(slot_waktu).replace('\u2013', '-').split('-', 1)
        h1, m1 = kiri.strip().replace(':', '.').split('.', 1)
        h2, m2 = kanan.strip().replace(':', '.').split('.', 1)
        start = int(h1) * 60 + int(m1)
        end = int(h2) * 60 + int(m2)
        if end > start:
            hasil = (start, end)
    except (ValueError, IndexError, AttributeError):
        hasil = None

    _WAKTU_CACHE[slot_waktu] = hasil
    return hasil


def waktu_bentrok(slot_a, slot_b):
    """Mengecek apakah dua rentang waktu saling tumpang tindih (overlap)."""
    if slot_a == slot_b:
        return True
    ia, ib = parse_waktu(slot_a), parse_waktu(slot_b)
    if ia is None or ib is None:
        return False
    return ia[0] < ib[1] and ib[0] < ia[1]


def _acak_penjadwalan(databases):
    """Mengambil nilai acak untuk gen penjadwalan (hari, waktu, ruangan)."""
    return {
        IDX_HARI: random.choice(databases['hari']),
        IDX_WAKTU: random.choice(databases['waktu']),
        IDX_RUANGAN: random.choice(databases['ruangan']),
    }


def buat_populasi_list(populasi_dict, databases):
    """Membangun populasi awal dengan atribut penjadwalan acak dan SKS konsisten."""
    populasi_list = []
    for kode, data in populasi_dict.items():
        acak = _acak_penjadwalan(databases)
        sks = data[3] if len(data) >= 4 else get_sks_for_matkul(data[1], databases)
        kromosom = {
            "kode": kode,
            "data": [
                data[0],
                data[1],
                data[2],
                sks,
                acak[IDX_HARI],
                acak[IDX_WAKTU],
                acak[IDX_RUANGAN],
            ],
            "generation": 0,
        }
        populasi_list.append(kromosom)
    return populasi_list


def evaluasi_populasi(populasi):
    """Menghitung jumlah konflik (ruangan, dosen, & prodi) dan nilai fitness tiap kromosom."""
    n = len(populasi)

    for krom in populasi:
        krom["konflik"] = 0

    for i in range(n):
        a = populasi[i]
        for j in range(i + 1, n):
            b = populasi[j]
            if a["data"][IDX_HARI] != b["data"][IDX_HARI]:
                continue
            if not waktu_bentrok(a["data"][IDX_WAKTU], b["data"][IDX_WAKTU]):
                continue
            if a["data"][IDX_RUANGAN] == b["data"][IDX_RUANGAN]:
                a["konflik"] += 1
                b["konflik"] += 1
            if a["data"][IDX_DOSEN] == b["data"][IDX_DOSEN]:
                a["konflik"] += 1
                b["konflik"] += 1
            if a["data"][IDX_PRODI] == b["data"][IDX_PRODI]:
                a["konflik"] += 1
                b["konflik"] += 1

    for krom in populasi:
        krom["fitness"] = round(1 / (1 + krom["konflik"]), 4)

    return populasi


def seleksi_tournament(populasi, tournament_size=3):
    """Memilih kromosom terbaik dari sampel acak berukuran tournament_size."""
    tournament_size = min(tournament_size, len(populasi))
    tournament = random.sample(populasi, tournament_size)
    return max(tournament, key=lambda x: x['fitness'])


def crossover(parent1, parent2, gen_number, crossover_rate=0.8):
    """Melakukan one-cut-point crossover pada gen penjadwalan [4:7] (Hari, Waktu, Ruangan)."""
    if random.random() > crossover_rate:
        anak1 = {
            "kode": f"G{gen_number}_C{random.randint(100, 999)}",
            "data": list(parent1["data"]),
            "generation": gen_number,
        }
        anak2 = {
            "kode": f"G{gen_number}_C{random.randint(100, 999)}",
            "data": list(parent2["data"]),
            "generation": gen_number,
        }
        return [anak1, anak2]

    cut_point = random.randint(5, 6)
    anak1 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent1["data"][:cut_point] + parent2["data"][cut_point:],
        "generation": gen_number,
    }
    anak2 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent2["data"][:cut_point] + parent1["data"][cut_point:],
        "generation": gen_number,
    }
    return [anak1, anak2]


def mutasi(kromosom, mutation_rate, databases):
    """Memutasi gen penjadwalan [4:7] (Hari, Waktu, Ruangan) berdasarkan probabilitas mutation_rate."""
    for gene_idx, key in GENE_MAP.items():
        if random.random() < mutation_rate:
            kromosom['data'][gene_idx] = random.choice(databases[key])
    return kromosom


def hitung_konflik_individu(kromosom, populasi, abaikan_idx=None):
    """Menghitung konflik satu kromosom terhadap anggota populasi lainnya."""
    hari = kromosom["data"][IDX_HARI]
    waktu = kromosom["data"][IDX_WAKTU]
    ruangan = kromosom["data"][IDX_RUANGAN]
    dosen = kromosom["data"][IDX_DOSEN]
    prodi = kromosom["data"][IDX_PRODI]
    konflik = 0

    for idx, other in enumerate(populasi):
        if idx == abaikan_idx or other is kromosom:
            continue
        if hari != other["data"][IDX_HARI]:
            continue
        if not waktu_bentrok(waktu, other["data"][IDX_WAKTU]):
            continue
        if ruangan == other["data"][IDX_RUANGAN]:
            konflik += 1
        if dosen == other["data"][IDX_DOSEN]:
            konflik += 1
        if prodi == other["data"][IDX_PRODI]:
            konflik += 1

    return konflik


def per_signature_replacement(old_pop, offspring, populasi_data, databases):
    """Mengganti generasi dengan mempertahankan jadwal terbaik pada tiap penugasan (elitism)."""
    kandidat_per_sig = {}
    for child in offspring:
        sig = (child['data'][IDX_DOSEN], child['data'][IDX_MATKUL], child['data'][IDX_PRODI])
        kandidat_per_sig.setdefault(sig, []).append(child)

    old_by_sig = {}
    for krom in old_pop:
        sig = (krom['data'][IDX_DOSEN], krom['data'][IDX_MATKUL], krom['data'][IDX_PRODI])
        if sig not in old_by_sig or krom.get('fitness', 0) > old_by_sig[sig].get('fitness', 0):
            old_by_sig[sig] = krom

    populasi_baru = []
    for key, data in populasi_data.items():
        sig = (data[0], data[1], data[2])
        if sig in old_by_sig:
            populasi_baru.append(old_by_sig[sig])
        else:
            acak = _acak_penjadwalan(databases)
            sks = data[3] if len(data) >= 4 else get_sks_for_matkul(data[1], databases)
            populasi_baru.append({
                'kode': key,
                'data': [data[0], data[1], data[2],
                         sks, acak[IDX_HARI], acak[IDX_WAKTU], acak[IDX_RUANGAN]],
                'generation': 0
            })

    # Perbarui hanya jadwal yang masih memiliki konflik jika kandidat anak lebih baik
    for idx, cur in enumerate(populasi_baru):
        c_lama = hitung_konflik_individu(cur, populasi_baru, abaikan_idx=idx)
        if c_lama == 0:
            continue

        sig = (cur['data'][IDX_DOSEN], cur['data'][IDX_MATKUL], cur['data'][IDX_PRODI])
        best_cand = cur
        best_c = c_lama

        cands = list(kandidat_per_sig.get(sig, []))
        for _ in range(3):
            rand_data = list(cur['data'])
            rand_data[IDX_HARI] = random.choice(databases['hari'])
            rand_data[IDX_WAKTU] = random.choice(databases['waktu'])
            rand_data[IDX_RUANGAN] = random.choice(databases['ruangan'])
            cands.append({'kode': cur['kode'], 'data': rand_data, 'generation': cur.get('generation', 0)})

        for cand in cands:
            c_baru = hitung_konflik_individu(cand, populasi_baru, abaikan_idx=idx)
            if c_baru < best_c:
                best_cand = cand
                best_c = c_baru
                if best_c == 0:
                    break

        populasi_baru[idx] = best_cand

    return evaluasi_populasi(populasi_baru)


def run_genetic_algorithm(populasi_data, databases,
                          generations=10,
                          mutation_rate=0.15,
                          crossover_rate=0.8,
                          early_stopping=False,
                          patience=8,
                          seed=None,
                          progress_callback=None):
    """Menjalankan siklus evolusi Algoritma Genetika dan mengembalikan hasil optimasi."""
    if seed is not None:
        random.seed(seed)

    target_size = len(populasi_data)
    if target_size < 2:
        raise ValueError("Minimal 2 kromosom diperlukan untuk menjalankan GA.")

    populasi = evaluasi_populasi(buat_populasi_list(populasi_data, databases))
    populasi_awal = [dict(k, data=list(k['data'])) for k in populasi]

    history = {
        'best_fitness': [], 'avg_fitness': [], 'worst_fitness': [],
        'best_konflik': [], 'total_konflik': [], 'generations': []
    }

    def _catat_history(pop, gen_idx):
        fitness_vals = [k['fitness'] for k in pop]
        konflik_vals = [k['konflik'] for k in pop]
        history['best_fitness'].append(round(max(fitness_vals), 4))
        history['avg_fitness'].append(round(sum(fitness_vals) / len(fitness_vals), 4))
        history['worst_fitness'].append(round(min(fitness_vals), 4))
        history['best_konflik'].append(min(konflik_vals))
        history['total_konflik'].append(sum(konflik_vals))
        history['generations'].append(gen_idx)

    _catat_history(populasi_awal, 0)

    best_total_so_far = history['total_konflik'][0]
    stagnant = 0
    gen = 0

    for gen in range(1, generations + 1):
        if progress_callback is not None:
            progress_callback(gen, generations)

        offspring = []
        for parent1 in populasi:
            kandidat_mate = [k for k in populasi if k is not parent1] or populasi
            parent2 = seleksi_tournament(kandidat_mate, tournament_size=3)
            anak_pair = crossover(parent1, parent2, gen, crossover_rate)

            for child in anak_pair:
                mutasi(child, mutation_rate, databases)
                offspring.append(child)

        populasi = per_signature_replacement(populasi, offspring, populasi_data, databases)
        _catat_history(populasi, gen)
        total_konflik = history['total_konflik'][-1]

        if total_konflik < best_total_so_far:
            best_total_so_far = total_konflik
            stagnant = 0
        else:
            stagnant += 1

        if early_stopping:
            if total_konflik == 0 or (gen >= 10 and stagnant >= patience):
                break

    best_solution = max(populasi, key=lambda x: x['fitness'])
    best_initial = max(populasi_awal, key=lambda x: x['fitness'])
    total_konflik_awal = history['total_konflik'][0]
    total_konflik_akhir = history['total_konflik'][-1]
    avg_fitness_awal = history['avg_fitness'][0]
    avg_fitness_akhir = history['avg_fitness'][-1]

    improvement = {
        'fitness_improvement': round(avg_fitness_akhir - avg_fitness_awal, 4),
        'konflik_reduction': total_konflik_awal - total_konflik_akhir,
        'improvement_percentage': round(
            ((avg_fitness_akhir - avg_fitness_awal) / avg_fitness_awal) * 100, 2
        ) if avg_fitness_awal > 0 else 0
    }

    return {
        'populasi_awal': populasi_awal,
        'populasi_akhir': populasi,
        'best_solution': best_solution,
        'best_initial': best_initial,
        'improvement': improvement,
        'history': history,
        'total_generations': gen,
        'parameters': {
            'generations': generations,
            'mutation_rate': mutation_rate,
            'crossover_rate': crossover_rate,
            'population_size': target_size,
            'early_stopping': early_stopping,
            'patience': patience,
            'seed': seed
        }
    }


def get_summary_stats(results):
    """Mengambil ringkasan metrik performa awal dan akhir evolusi."""
    history = results['history']
    initial_best = history['best_fitness'][0]
    final_best = history['best_fitness'][-1]
    initial_avg = history['avg_fitness'][0]
    final_avg = history['avg_fitness'][-1]
    return {
        'initial_best_fitness': initial_best,
        'final_best_fitness': final_best,
        'initial_avg_fitness': initial_avg,
        'final_avg_fitness': final_avg,
        'initial_konflik': history['total_konflik'][0],
        'final_konflik': history['total_konflik'][-1],
        'total_generations': results['total_generations'],
        'fitness_improvement': round(final_avg - initial_avg, 4),
        'reached_optimal': history['total_konflik'][-1] == 0
    }


def format_kromosom_detail(kromosom):
    """Mengubah struktur kromosom menjadi dictionary siap tampil di tabel UI."""
    return {
        'Kode': kromosom['kode'],
        'Dosen': kromosom['data'][IDX_DOSEN],
        'Mata Kuliah': kromosom['data'][IDX_MATKUL],
        'Prodi': kromosom['data'][IDX_PRODI],
        'SKS': kromosom['data'][IDX_SKS],
        'Hari': kromosom['data'][IDX_HARI],
        'Waktu': kromosom['data'][IDX_WAKTU],
        'Ruangan': kromosom['data'][IDX_RUANGAN],
        'Fitness': kromosom['fitness'],
        'Konflik': kromosom['konflik'],
        'Generasi': kromosom.get('generation', 0)
    }


def buat_tabel_rekomendasi_jadwal(results):
    """Menyusun populasi akhir menjadi daftar jadwal terurut berdasarkan dosen dan mata kuliah."""
    populasi_akhir = results['populasi_akhir']
    populasi_sorted = sorted(
        populasi_akhir,
        key=lambda x: (x['data'][IDX_DOSEN], x['data'][IDX_MATKUL])
    )

    tabel_rekomendasi = []
    for idx, krom in enumerate(populasi_sorted, 1):
        tabel_rekomendasi.append({
            'No': idx,
            'Dosen': krom['data'][IDX_DOSEN],
            'Mata Kuliah': krom['data'][IDX_MATKUL],
            'Prodi': krom['data'][IDX_PRODI],
            'SKS': krom['data'][IDX_SKS],
            'Hari': krom['data'][IDX_HARI],
            'Waktu': krom['data'][IDX_WAKTU],
            'Ruangan': krom['data'][IDX_RUANGAN],
            'Fitness': krom['fitness'],
            'Konflik': krom['konflik']
        })

    return tabel_rekomendasi