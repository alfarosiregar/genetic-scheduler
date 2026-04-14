"""
Genetic Algorithm untuk Penjadwalan
"""

import random
import copy
import csv
from collections import defaultdict


# ========== CORE GA FUNCTIONS ==========

def buat_populasi_list(populasi_dict, databases):
    populasi_list = []
    for kode, data in populasi_dict.items():
        kromosom = {
            "kode": kode,
            "data": [
                data[0],  # dosen
                data[1],  # matkul
                data[2],  # prodi
                random.choice(databases['sks']),
                random.choice(databases['hari']),
                random.choice(databases['waktu']),
                random.choice(databases['ruangan'])
            ],
            "generation": 0
        }
        populasi_list.append(kromosom)
    return populasi_list


def hitung_konflik(krom, populasi):
    """
    Index: [dosen, matkul, prodi, sks, hari, waktu, ruangan]
           [0,     1,      2,     3,   4,    5,     6]
    """
    konflik = 0
    for other in populasi:
        if krom["kode"] == other["kode"]:
            continue
        same_hari = krom["data"][4] == other["data"][4]
        same_waktu = krom["data"][5] == other["data"][5]
        if same_hari and same_waktu:
            if krom["data"][6] == other["data"][6]:
                konflik += 1
            if krom["data"][0] == other["data"][0]:
                konflik += 1
    return konflik


def fitness(konflik):
    return round(1 / (1 + konflik), 4)


def evaluasi_populasi(populasi):
    for krom in populasi:
        konflik = hitung_konflik(krom, populasi)
        krom["konflik"] = konflik
        krom["fitness"] = fitness(konflik)
    return populasi


def seleksi_tournament(populasi, tournament_size=3):
    tournament_size = min(tournament_size, len(populasi))
    tournament = random.sample(populasi, tournament_size)
    return max(tournament, key=lambda x: x['fitness'])


def crossover(parent1, parent2, gen_number):
    cut_point = 3
    offspring1 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent1["data"][:cut_point] + parent2["data"][cut_point:],
        "generation": gen_number
    }
    offspring2 = {
        "kode": f"G{gen_number}_C{random.randint(100, 999)}",
        "data": parent2["data"][:cut_point] + parent1["data"][cut_point:],
        "generation": gen_number
    }
    return [offspring1, offspring2]


def mutasi(kromosom, mutation_rate, databases):
    if random.random() < mutation_rate:
        gene_map = {3: 'sks', 4: 'hari', 5: 'waktu', 6: 'ruangan'}
        gene_idx = random.choice([3, 4, 5, 6])
        kromosom['data'][gene_idx] = random.choice(databases[gene_map[gene_idx]])
    return kromosom


def mutasi_kuat(kromosom, databases):
    kromosom['data'][3] = random.choice(databases['sks'])
    kromosom['data'][4] = random.choice(databases['hari'])
    kromosom['data'][5] = random.choice(databases['waktu'])
    kromosom['data'][6] = random.choice(databases['ruangan'])
    return kromosom


def elitism_replacement(old_pop, new_pop, elite_size):
    sorted_old = sorted(old_pop, key=lambda x: x['fitness'], reverse=True)
    elites = sorted_old[:elite_size]
    combined = elites + new_pop
    combined_sorted = sorted(combined, key=lambda x: x['fitness'], reverse=True)
    return combined_sorted[:len(old_pop)]


def create_immigrant(gen_number, populasi_data, databases):
    keys = list(populasi_data.keys())
    key = random.choice(keys)
    base = populasi_data[key]
    immigrant = {
        'kode': f"G{gen_number}_IMM{random.randint(100, 999)}",
        'data': [
            base[0], base[1], base[2],
            random.choice(databases['sks']),
            random.choice(databases['hari']),
            random.choice(databases['waktu']),
            random.choice(databases['ruangan'])
        ],
        'generation': gen_number
    }
    return mutasi_kuat(immigrant, databases)


def remove_duplicates(populasi):
    """
    FIX: Hapus duplikat berdasarkan (Dosen, Matkul, Prodi),
    pertahankan yang fitness-nya tertinggi.
    """
    unique_dict = {}
    for krom in populasi:
        sig = (krom['data'][0], krom['data'][1], krom['data'][2])
        # Simpan yang fitness-nya lebih tinggi
        if sig not in unique_dict or krom['fitness'] > unique_dict[sig]['fitness']:
            unique_dict[sig] = krom
    return list(unique_dict.values())


def fill_missing(populasi, populasi_data, databases, gen):
    """
    FIX: Isi kembali kromosom yang hilang agar ukuran populasi
    selalu sama dengan jumlah input.
    """
    target_size = len(populasi_data)
    existing_sigs = {(k['data'][0], k['data'][1], k['data'][2]) for k in populasi}
    all_sigs = {(v[0], v[1], v[2]): k for k, v in populasi_data.items()}

    for sig, key in all_sigs.items():
        if sig not in existing_sigs:
            data = populasi_data[key]
            filler = {
                'kode': f"G{gen}_FILL{random.randint(100, 999)}",
                'data': [
                    data[0], data[1], data[2],
                    random.choice(databases['sks']),
                    random.choice(databases['hari']),
                    random.choice(databases['waktu']),
                    random.choice(databases['ruangan'])
                ],
                'generation': gen
            }
            populasi.append(filler)
            existing_sigs.add(sig)

    return populasi[:target_size]


# ========== MAIN GA FUNCTION ==========

def run_genetic_algorithm(populasi_data, databases,
                          generations=10,
                          mutation_rate=0.15,
                          elite_size=2,
                          early_stopping=False):

    # ========== INITIALIZATION ==========
    populasi = buat_populasi_list(populasi_data, databases)
    populasi = evaluasi_populasi(populasi)
    populasi_awal = copy.deepcopy(populasi)

    history = {
        'best_fitness': [],
        'avg_fitness': [],
        'worst_fitness': [],
        'best_konflik': [],
        'generations': []
    }

    # ========== EVOLUTION ==========
    for gen in range(1, generations + 1):
        target_size = len(populasi_data)  # FIX: selalu pakai ukuran input, bukan len(populasi)
        offspring = []

        # ===== CROSSOVER =====
        while len(offspring) < target_size:
            parent1 = seleksi_tournament(populasi, tournament_size=3)
            parent2 = seleksi_tournament(populasi, tournament_size=3)
            children = crossover(parent1, parent2, gen)
            for child in children:
                offspring.append(child)
                if len(offspring) >= target_size:
                    break

        offspring = offspring[:target_size]

        # ===== MUTATION =====
        current_rate = mutation_rate * (1.5 if gen <= 3 else 1.0)
        for child in offspring:
            mutasi(child, current_rate, databases)

        # ===== EVALUATION =====
        offspring = evaluasi_populasi(offspring)

        # ===== REMOVE DUPLICATES =====
        # FIX: hapus duplikat, pertahankan yang terbaik per (dosen,matkul,prodi)
        offspring = remove_duplicates(offspring)

        # ===== FILL MISSING =====
        # FIX: isi yang hilang agar kembali ke target_size
        offspring = fill_missing(offspring, populasi_data, databases, gen)
        offspring = evaluasi_populasi(offspring)

        # ===== ELITISM REPLACEMENT =====
        populasi = elitism_replacement(populasi, offspring, elite_size)

        # FIX: setelah elitism, hapus duplikat lagi (elite bisa bawa duplikat)
        # dan fill kembali ke target_size
        populasi = remove_duplicates(populasi)
        populasi = fill_missing(populasi, populasi_data, databases, gen)
        populasi = evaluasi_populasi(populasi)

        # ===== TRACKING =====
        fitness_values = [k['fitness'] for k in populasi]
        konflik_values = [k['konflik'] for k in populasi]

        best_fitness = max(fitness_values)
        avg_fitness = sum(fitness_values) / len(fitness_values)
        worst_fitness = min(fitness_values)
        best_konflik = min(konflik_values)

        history['best_fitness'].append(round(best_fitness, 4))
        history['avg_fitness'].append(round(avg_fitness, 4))
        history['worst_fitness'].append(round(worst_fitness, 4))
        history['best_konflik'].append(best_konflik)
        history['generations'].append(gen)

        print(f"Gen {gen}: Best Fitness={best_fitness:.4f}, Avg Fitness={avg_fitness:.4f}, Konflik={best_konflik}, Size={len(populasi)}")

        # ===== EARLY STOPPING =====
        if early_stopping:
            MIN_GENERATIONS = 5
            if gen >= MIN_GENERATIONS and best_fitness >= 0.99 and best_konflik == 0:
                print(f"✓ Optimal solution found at generation {gen} (early stopping)!")
                break

    # ========== FINALIZATION ==========
    best_solution = max(populasi, key=lambda x: x['fitness'])
    best_initial = max(populasi_awal, key=lambda x: x['fitness'])

    improvement = {
        'fitness_improvement': round(best_solution['fitness'] - best_initial['fitness'], 4),
        'konflik_reduction': best_initial['konflik'] - best_solution['konflik'],
        'improvement_percentage': round(
            ((best_solution['fitness'] - best_initial['fitness']) / best_initial['fitness']) * 100, 2
        ) if best_initial['fitness'] > 0 else 0
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
            'elite_size': elite_size,
            'population_size': len(populasi),
            'early_stopping': early_stopping
        }
    }


# ========== HELPER FUNCTIONS ==========

def get_summary_stats(results):
    history = results['history']
    return {
        'initial_best_fitness': history['best_fitness'][0],
        'final_best_fitness': history['best_fitness'][-1],
        'initial_avg_fitness': history['avg_fitness'][0],
        'final_avg_fitness': history['avg_fitness'][-1],
        'initial_konflik': history['best_konflik'][0],
        'final_konflik': history['best_konflik'][-1],
        'total_generations': results['total_generations'],
        'fitness_improvement': round(
            history['best_fitness'][-1] - history['best_fitness'][0], 4
        ),
        'reached_optimal': history['best_konflik'][-1] == 0
    }


def format_kromosom_detail(kromosom):
    return {
        'Kode': kromosom['kode'],
        'Dosen': kromosom['data'][0],
        'Mata Kuliah': kromosom['data'][1],
        'Prodi': kromosom['data'][2],
        'SKS': kromosom['data'][3],
        'Hari': kromosom['data'][4],
        'Waktu': kromosom['data'][5],
        'Ruangan': kromosom['data'][6],
        'Fitness': kromosom['fitness'],
        'Konflik': kromosom['konflik'],
        'Generasi': kromosom.get('generation', 0)
    }


def filter_unique_dosen_matkul_prodi(populasi):
    unique_dict = {}
    for krom in populasi:
        key = (krom['data'][0], krom['data'][1], krom['data'][2])
        if key not in unique_dict or krom['fitness'] > unique_dict[key]['fitness']:
            unique_dict[key] = krom
    return list(unique_dict.values())


def buat_tabel_rekomendasi_jadwal(results):
    """
    FIX: Langsung pakai populasi_akhir tanpa filter tambahan.
    Populasi akhir sudah dijamin = jumlah input dari dalam GA.
    """
    populasi_akhir = results['populasi_akhir']
    populasi_sorted = sorted(populasi_akhir, key=lambda x: (x['data'][0], x['data'][1]))

    tabel_rekomendasi = []
    for idx, krom in enumerate(populasi_sorted, 1):
        rekomendasi = {
            'No': idx,
            'Dosen': krom['data'][0],
            'Mata Kuliah': krom['data'][1],
            'Prodi': krom['data'][2],
            'SKS': krom['data'][3],
            'Hari': krom['data'][4],
            'Waktu': krom['data'][5],
            'Ruangan': krom['data'][6],
            'Fitness': krom['fitness'],
            'Konflik': krom['konflik']
        }
        tabel_rekomendasi.append(rekomendasi)

    return tabel_rekomendasi


def export_hasil_ga_ke_csv(results, output_file, filter_duplicates=True):
    populasi_akhir = results['populasi_akhir']
    if filter_duplicates:
        populasi_filtered = filter_unique_dosen_matkul_prodi(populasi_akhir)
    else:
        populasi_filtered = populasi_akhir
    populasi_sorted = sorted(populasi_filtered, key=lambda x: x['data'][0])

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Kode', 'Dosen', 'Mata Kuliah', 'Prodi', 'SKS',
                      'Hari', 'Waktu', 'Ruangan', 'Fitness', 'Konflik', 'Generasi']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for krom in populasi_sorted:
            writer.writerow({
                'Kode': krom['kode'],
                'Dosen': krom['data'][0],
                'Mata Kuliah': krom['data'][1],
                'Prodi': krom['data'][2],
                'SKS': krom['data'][3],
                'Hari': krom['data'][4],
                'Waktu': krom['data'][5],
                'Ruangan': krom['data'][6],
                'Fitness': krom['fitness'],
                'Konflik': krom['konflik'],
                'Generasi': krom.get('generation', 0)
            })

    print(f"\n✓ Results exported to: {output_file}")
    print(f"  → Total schedules: {len(populasi_sorted)}")
    return populasi_filtered


# ========== PARSE INPUT ==========

def parse_csv_input(csv_file):
    populasi_dict = {}
    databases = {
        'sks': ['2', '3', '4'],
        'hari': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'],
        'waktu': ['07:00-09:00', '09:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00'],
        'ruangan': ['R101', 'R102', 'R103', 'R201', 'R202', 'R203', 'Lab1', 'Lab2']
    }
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            kode = f"C{idx+1}"
            populasi_dict[kode] = [
                row['Dosen'].strip(),
                row['Mata Kuliah'].strip(),
                row['Prodi'].strip()
            ]
    return populasi_dict, databases