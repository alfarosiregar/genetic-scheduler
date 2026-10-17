"""
Genetic Algorithm untuk Penjadwalan
====================================
Representasi kromosom (index data):
    [0] dosen    [1] matkul   [2] prodi
    [3] sks      [4] hari     [5] waktu   [6] ruangan

Kaidah metode yang diterapkan:
    1. Seleksi turnamen - memilih pasangan induk terbaik dari k sampel acak.
    2. Crossover one-cut-point pada gen penjadwalan [3:7] dengan tetap menjaga
       gen kecocokan [0:3] (dosen, matkul, prodi) utuh dari masing-masing
       parent sehingga penugasan tetap koheren dan menghasilkan kombinasi
       baru antara (sks, hari, waktu, ruangan) dari kedua parent.
    3. Mutasi per-gen dengan probabilitas mutation_rate per gen (kaidah GA
       standar) pada gen penjadwalan [3:7]; gen kecocokan [0:3] tidak dimutasi.
    4. Evaluasi fitness komprehensif: setiap pasangan kromosom dibandingkan
       tepat satu kali (i vs j>i), mencakup konflik ruangan (ruangan sama saat
       waktu bentrok) dan konflik dosen (dosen sama mengajar bersamaan).
       Bentrok waktu dideteksi sebagai OVERLAP INTERVAL (HH.MM-HH.MM), bukan
       sekadar kesetaraan string slot, sehingga slot yang tumpang tindih
       parsial (mis. '08.00-11.20' vs '08.30-09.40') juga terdeteksi.
    5. Elitism kontekstual per penugasan (niche elitism): kandidat anak
       dievaluasi langsung terhadap konteks populasi jadwal saat ini sehingga
       setiap penugasan punya tepat satu jadwal dan total konflik dijamin
       monoton turun (tidak pernah memburuk).
    6. Early stopping berbasis stagnasi: berhenti bila total konflik jadwal
       tak membaik selama `patience` generasi, atau saat 0 konflik tercapai.
    7. Seed opsional untuk reproduksibilitas eksperimen.
"""

import random

# Index gene dalam kromosom
IDX_DOSEN = 0
IDX_MATKUL = 1
IDX_PRODI = 2
IDX_SKS = 3
IDX_HARI = 4
IDX_WAKTU = 5
IDX_RUANGAN = 6

# Gen "kecocokan" (penugasan) tidak diacak; gen [3:] adalah gen penjadwalan
GENE_MAP = {
    IDX_SKS: 'sks',
    IDX_HARI: 'hari',
    IDX_WAKTU: 'waktu',
    IDX_RUANGAN: 'ruangan',
}


# ========== PARSER WAKTU (INTERVAL) ==========

# Cache: string slot waktu -> (start_menit, end_menit) | None bila tak terparse
_WAKTU_CACHE = {}


def parse_waktu(slot_waktu):
    """
    Parse slot waktu "HH.MM-HH.MM" (juga menerima "HH:MM" dan en-dash "\u2013"
    sebagai pemisah) menjadi interval menit (start, end).

    Return None bila format tidak dikenali. Hasil di-cache karena jumlah slot
    waktu di database terbatas dan fungsi ini dipanggil berulang-ulang saat
    evaluasi populasi.
    """
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
    """
    True bila dua slot waktu BENTROK: interval waktunya tumpang tindih
    (termasuk overlap parsial, mis. '08.00-11.20' vs '08.30-09.40', atau
    nested). Slot yang bersentuhan di tepi (end == start, back-to-back)
    TIDAK dianggap bentrok.

    Bila salah satu slot tidak dapat di-parse, fallback ke kesetaraan string:
    slot identik tetap dianggap bentrok, slot berbeda dianggap tidak.
    """
    if slot_a == slot_b:
        return True  # slot identik pasti bentrok (juga saat tak terparse)
    ia, ib = parse_waktu(slot_a), parse_waktu(slot_b)
    if ia is None or ib is None:
        return False  # tak terparse & beda string: overlap tak bisa dipastikan
    return ia[0] < ib[1] and ib[0] < ia[1]


def _acak_penjadwalan(databases):
    """Acak seluruh gen penjadwalan (sks, hari, waktu, ruangan)."""
    return {
        IDX_SKS: random.choice(databases['sks']),
        IDX_HARI: random.choice(databases['hari']),
        IDX_WAKTU: random.choice(databases['waktu']),
        IDX_RUANGAN: random.choice(databases['ruangan']),
    }


# ========== CORE GA FUNCTIONS ==========

def buat_populasi_list(populasi_dict, databases):
    """
    Bangun populasi awal dari dict penugasan {kode: [dosen, matkul, prodi]}.
    Gen penjadwalan diinisialisasi acak - sesuai kaidah inisialisasi populasi GA.
    """
    populasi_list = []
    for kode, data in populasi_dict.items():
        acak = _acak_penjadwalan(databases)
        kromosom = {
            "kode": kode,
            "data": [
                data[0],          # dosen (kecocokan)
                data[1],          # matkul (kecocokan)
                data[2],          # prodi (kecocokan)
                acak[IDX_SKS],
                acak[IDX_HARI],
                acak[IDX_WAKTU],
                acak[IDX_RUANGAN],
            ],
            "generation": 0
        }
        populasi_list.append(kromosom)
    return populasi_list


def evaluasi_populasi(populasi):
    """
    Evaluasi fitness seluruh populasi secara komprehensif dan efisien.

    Konflik dihitung antar pasangan kromosom yang BERBENTROK WAKTU: berada
    pada hari yang sama DAN rentang waktunya tumpang tindih (overlap interval,
    tidak harus string slot yang identik):
      - Konflik ruangan: dua kelas menempati ruangan yang sama pada waktu
        yang tumpang tindih.
      - Konflik dosen  : dosen yang sama mengajar dua kelas yang waktunya
        tumpang tindih.

    Slot waktu yang tidak dapat di-parse (format bebas) diproses dengan
    fallback kesetaraan string, sehingga evaluasi tetap berjalan.

    Setiap pasangan hanya dihitung satu kali (i vs j > i), sehingga jumlah
    konflik tidak digandakan.
    """
    n = len(populasi)

    # Reset konflik
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
            # Waktu (hari + rentang) bentrok
            if a["data"][IDX_RUANGAN] == b["data"][IDX_RUANGAN]:
                a["konflik"] += 1
                b["konflik"] += 1
            if a["data"][IDX_DOSEN] == b["data"][IDX_DOSEN]:
                a["konflik"] += 1
                b["konflik"] += 1

    # Fitness = 1 / (1 + konflik)  ->  1.0 berarti bebas konflik
    for krom in populasi:
        krom["fitness"] = round(1 / (1 + krom["konflik"]), 4)

    return populasi


def seleksi_tournament(populasi, tournament_size=3):
    tournament_size = min(tournament_size, len(populasi))
    tournament = random.sample(populasi, tournament_size)
    return max(tournament, key=lambda x: x['fitness'])


def crossover(parent1, parent2, gen_number, crossover_rate=0.8):
    """
    Crossover one-cut-point pada gen penjadwalan [3:7]:
        - Gen kecocokan [0:3] (dosen, matkul, prodi) tetap diwarisi utuh dari
          masing-masing parent agar penugasan tidak tercampur.
        - Titik potong dipilih di dalam gen penjadwalan (indeks 4..6, yaitu di
          antara [sks, hari, waktu, ruangan]) sehingga menghasilkan kombinasi
          baru (misal hari+waktu dari P1 dengan ruangan dari P2, dan sebaliknya)
          tanpa menyalin mentah seluruh slot P2 yang berisiko langsung bentrok
          ruangan dengan P2 sendiri.
    """
    if random.random() > crossover_rate:
        anak1 = {"kode": f"G{gen_number}_C{random.randint(100, 999)}",
                 "data": list(parent1["data"]), "generation": gen_number}
        anak2 = {"kode": f"G{gen_number}_C{random.randint(100, 999)}",
                 "data": list(parent2["data"]), "generation": gen_number}
        return [anak1, anak2]

    cut_point = random.randint(4, 6)  # One-cut-point di dalam gen penjadwalan [3:7]
    anak1 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent1["data"][:3] + parent1["data"][3:cut_point] + parent2["data"][cut_point:],
        "generation": gen_number
    }
    anak2 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent2["data"][:3] + parent2["data"][3:cut_point] + parent1["data"][cut_point:],
        "generation": gen_number
    }
    return [anak1, anak2]


def mutasi(kromosom, mutation_rate, databases):
    """
    Mutasi per-gen (kaidah GA standar): setiap gen penjadwalan [3:7] diubah
    secara acak dengan probabilitas mutation_rate. Gen kecocokan [0:3] tidak
    disentuh agar penugasan (dosen-matkul-prodi) tetap terjaga.
    """
    for gene_idx, key in GENE_MAP.items():
        if random.random() < mutation_rate:
            kromosom['data'][gene_idx] = random.choice(databases[key])
    return kromosom


def hitung_konflik_individu(kromosom, populasi, abaikan_idx=None):
    """
    Hitung jumlah konflik satu kandidat kromosom terhadap seluruh anggota
    populasi lainnya (kecuali indeks `abaikan_idx` / dirinya sendiri).
    Digunakan untuk evaluasi kontekstual saat elitism replacement agar
    penggantian individu dijamin tidak menambah konflik jadwal secara keseluruhan.
    """
    hari = kromosom["data"][IDX_HARI]
    waktu = kromosom["data"][IDX_WAKTU]
    ruangan = kromosom["data"][IDX_RUANGAN]
    dosen = kromosom["data"][IDX_DOSEN]
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

    return konflik


def per_signature_replacement(old_pop, offspring, populasi_data, databases):
    """
    Penggantian generasi dengan elitism kontekstual per penugasan (niche elitism):
    untuk SETIAP penugasan input (dosen, matkul, prodi), kandidat anak dievaluasi
    langsung terhadap konteks populasi jadwal saat ini.

    Konsekuensinya:
      - setiap penugasan input selalu punya tepat satu jadwal di hasil akhir;
      - jadwal yang sudah bebas konflik (konflik == 0) dipertahankan;
      - jadwal yang masih berkonflik hanya diganti oleh kandidat anak yang
        menghasilkan konflik <= konflik saat ini terhadap sisa jadwal,
        sehingga total konflik populasi dijamin monoton turun (tidak pernah memburuk).
    """
    # Kelompokkan kandidat anak berdasarkan signature (dosen, matkul, prodi)
    kandidat_per_sig = {}
    for child in offspring:
        sig = (child['data'][IDX_DOSEN], child['data'][IDX_MATKUL], child['data'][IDX_PRODI])
        kandidat_per_sig.setdefault(sig, []).append(child)

    # Susun populasi dasar dari old_pop sesuai urutan populasi_data
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
            populasi_baru.append({
                'kode': key,
                'data': [data[0], data[1], data[2],
                         acak[IDX_SKS], acak[IDX_HARI], acak[IDX_WAKTU], acak[IDX_RUANGAN]],
                'generation': 0
            })

    # Evaluasi kontekstual: perbaiki kromosom yang masih memiliki konflik
    for idx, cur in enumerate(populasi_baru):
        c_lama = hitung_konflik_individu(cur, populasi_baru, abaikan_idx=idx)
        if c_lama == 0:
            continue  # Sudah bebas konflik di konteks jadwal saat ini

        sig = (cur['data'][IDX_DOSEN], cur['data'][IDX_MATKUL], cur['data'][IDX_PRODI])
        best_cand = cur
        best_c = c_lama

        for cand in kandidat_per_sig.get(sig, []):
            c_baru = hitung_konflik_individu(cand, populasi_baru, abaikan_idx=idx)
            if c_baru <= best_c:
                best_cand = cand
                best_c = c_baru
                if best_c == 0:
                    break

        populasi_baru[idx] = best_cand

    return evaluasi_populasi(populasi_baru)


# ========== MAIN GA FUNCTION ==========

def run_genetic_algorithm(populasi_data, databases,
                          generations=10,
                          mutation_rate=0.15,
                          crossover_rate=0.8,
                          early_stopping=False,
                          patience=5,
                          seed=None,
                          progress_callback=None):
    """
    Jalankan siklus lengkap algoritma genetika.

    Args:
        populasi_data     : dict {kode: [dosen, matkul, prodi]} penugasan input.
        databases         : dict nilai untuk gen sks/hari/waktu/ruangan.
        generations       : jumlah generasi maksimum.
        mutation_rate     : probabilitas mutasi per gen (0..1).
        crossover_rate    : probabilitas rekombinasi (0..1).
        early_stopping    : aktifkan penghentian dini.
        patience          : berhenti setelah N generasi tanpa perbaikan.
        seed              : seed RNG opsional untuk reproduksibilitas.
        progress_callback : fungsi fn(generasi, total) untuk update progress UI.

    Returns:
        dict hasil lengkap: populasi awal/akhir, solusi terbaik, history, dll.
    """
    if seed is not None:
        random.seed(seed)

    target_size = len(populasi_data)
    if target_size < 2:
        raise ValueError("Minimal 2 kromosom diperlukan untuk menjalankan GA.")

    # ========== INISIALISASI (GENERASI 0) ==========
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

    # Catat kondisi awal (Generasi 0) agar grafik & metrik awal akurat
    _catat_history(populasi_awal, 0)

    best_total_so_far = history['total_konflik'][0]
    stagnant = 0
    gen = 0

    # ========== EVOLUSI ==========
    for gen in range(1, generations + 1):
        if progress_callback is not None:
            progress_callback(gen, generations)

        # 1) Seleksi + Crossover + Mutasi
        # Setiap penugasan di populasi (parent1) dipasangkan dengan parent2
        # berbeda hasil seleksi turnamen, lalu direkombinasi (crossover_rate)
        # dan dimutasi per-gen sesuai mutation_rate pilihan pengguna.
        offspring = []
        for parent1 in populasi:
            kandidat_mate = [k for k in populasi if k is not parent1] or populasi
            parent2 = seleksi_tournament(kandidat_mate, tournament_size=3)
            anak_pair = crossover(parent1, parent2, gen, crossover_rate)

            for child in anak_pair:
                mutasi(child, mutation_rate, databases)
                offspring.append(child)

        # 2) Evaluasi & penggantian generasi kontekstual (elitism per penugasan)
        populasi = per_signature_replacement(populasi, offspring, populasi_data, databases)

        # 3) Catat statistik generasi
        _catat_history(populasi, gen)
        total_konflik = history['total_konflik'][-1]

        # 4) Early stopping berbasis total konflik jadwal
        if total_konflik < best_total_so_far:
            best_total_so_far = total_konflik
            stagnant = 0
        else:
            stagnant += 1

        if early_stopping:
            if total_konflik == 0:  # seluruh jadwal bebas konflik (optimal sejati)
                break
            if gen >= 5 and stagnant >= patience:
                break

    # ========== FINALISASI ==========
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


# ========== HELPER FUNCTIONS ==========

def get_summary_stats(results):
    history = results['history']
    initial_avg = history['avg_fitness'][0]
    final_avg = history['avg_fitness'][-1]
    return {
        'initial_best_fitness': initial_avg,
        'final_best_fitness': final_avg,
        'initial_avg_fitness': initial_avg,
        'final_avg_fitness': final_avg,
        'initial_konflik': history['total_konflik'][0],
        'final_konflik': history['total_konflik'][-1],
        'total_generations': results['total_generations'],
        'fitness_improvement': round(final_avg - initial_avg, 4),
        'reached_optimal': history['total_konflik'][-1] == 0
    }


def format_kromosom_detail(kromosom):
    """Bentuk satu kromosom menjadi dict siap-tabel untuk UI."""
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
    """Susun populasi akhir menjadi tabel rekomendasi jadwal terurut."""
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