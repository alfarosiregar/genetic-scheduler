"""
Genetic Algorithm untuk Penjadwalan - FULLY OPTIMIZED VERSION
- Configurable early stopping
- No aggressive filtering
- Full generation execution
"""

import random
import copy
import csv
from collections import defaultdict


# ========== CORE GA FUNCTIONS ==========

def buat_populasi_list(populasi_dict, databases):
    """
    Konversi dictionary populasi ke list dengan random generation
    
    Args:
        populasi_dict: Dictionary {kode: [dosen, matkul, prodi]}
        databases: Dictionary berisi pilihan valid
    
    Returns:
        List kromosom lengkap
    """
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
    Hitung konflik untuk kromosom
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
            # Konflik ruangan (ruangan, hari, waktu sama)
            if krom["data"][6] == other["data"][6]:
                konflik += 1
            
            # Konflik dosen (dosen, hari, waktu sama)
            if krom["data"][0] == other["data"][0]:
                konflik += 1
    
    return konflik


def fitness(konflik):
    """
    Hitung fitness HANYA dari konflik
    Formula: 1 / (1 + konflik)
    
    Args:
        konflik: Jumlah konflik
    
    Returns:
        Fitness score (0.0 - 1.0)
    """
    return round(1 / (1 + konflik), 4)


def evaluasi_populasi(populasi):
    """Evaluasi fitness untuk semua kromosom"""
    for krom in populasi:
        konflik = hitung_konflik(krom, populasi)
        krom["konflik"] = konflik
        krom["fitness"] = fitness(konflik)
    
    return populasi


def seleksi_tournament(populasi, tournament_size=3):
    """
    Tournament Selection untuk memilih parent
    
    Args:
        populasi: List kromosom
        tournament_size: Ukuran tournament
    
    Returns:
        1 parent terpilih
    """
    tournament_size = min(tournament_size, len(populasi))
    tournament = random.sample(populasi, tournament_size)
    return max(tournament, key=lambda x: x['fitness'])


def crossover(parent1, parent2, gen_number):
    """
    Single-point crossover setelah prodi (index 2)
    Bagian tetap: dosen, matkul, prodi (0-2)
    Bagian crossover: sks, hari, waktu, ruangan (3-6)
    
    Args:
        parent1, parent2: Parent kromosom
        gen_number: Nomor generasi
    
    Returns:
        2 offspring
    """
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
    """
    Mutasi gen (sks, hari, waktu, ruangan)
    
    Args:
        kromosom: Kromosom yang akan dimutasi
        mutation_rate: Probabilitas mutasi
        databases: Dictionary berisi data valid
    
    Returns:
        Kromosom yang sudah dimutasi
    """
    if random.random() < mutation_rate:
        # Pilih gen mana yang dimutasi (index 3-6)
        gene_map = {
            3: 'sks',
            4: 'hari',
            5: 'waktu',
            6: 'ruangan'
        }
        
        gene_idx = random.choice([3, 4, 5, 6])
        kromosom['data'][gene_idx] = random.choice(databases[gene_map[gene_idx]])
    
    return kromosom


def mutasi_kuat(kromosom, databases):
    """
    Mutasi kuat untuk diversity (ubah semua gen mutable)
    
    Args:
        kromosom: Kromosom yang akan dimutasi
        databases: Dictionary berisi data valid
    
    Returns:
        Kromosom yang sudah dimutasi kuat
    """
    kromosom['data'][3] = random.choice(databases['sks'])
    kromosom['data'][4] = random.choice(databases['hari'])
    kromosom['data'][5] = random.choice(databases['waktu'])
    kromosom['data'][6] = random.choice(databases['ruangan'])
    
    return kromosom


def elitism_replacement(old_pop, new_pop, elite_size):
    """
    Replacement dengan elitism
    
    Args:
        old_pop: Populasi lama
        new_pop: Populasi baru
        elite_size: Jumlah elite
    
    Returns:
        Populasi baru dengan elite
    """
    # Sort dan ambil elite
    sorted_old = sorted(old_pop, key=lambda x: x['fitness'], reverse=True)
    elites = sorted_old[:elite_size]
    
    # Gabung dan sort
    combined = elites + new_pop
    combined_sorted = sorted(combined, key=lambda x: x['fitness'], reverse=True)
    
    return combined_sorted[:len(old_pop)]


def create_immigrant(gen_number, populasi_data, databases):
    """
    Buat immigrant untuk diversity
    
    Args:
        gen_number: Nomor generasi
        populasi_data: Data populasi awal
        databases: Database untuk mutasi
    
    Returns:
        Kromosom immigrant baru
    """
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
    Hapus duplikat berdasarkan (Dosen, Matkul, Prodi)
    Setiap kombinasi hanya boleh muncul 1x dalam populasi
    
    Args:
        populasi: List kromosom
    
    Returns:
        List kromosom tanpa duplikat (dosen, matkul, prodi)
    """
    seen = set()
    unique = []
    
    for krom in populasi:
        # Signature: (dosen, matkul, prodi)
        signature = (krom['data'][0], krom['data'][1], krom['data'][2])
        
        if signature not in seen:
            seen.add(signature)
            unique.append(krom)
    
    return unique


# ========== MAIN GA FUNCTION ==========

def run_genetic_algorithm(populasi_data, databases, 
                          generations=10, 
                          mutation_rate=0.15,
                          elite_size=2,
                          early_stopping=False):  # ✅ TAMBAH PARAMETER
    """
    Algoritma Genetika OPTIMIZED untuk penjadwalan
    
    Args:
        populasi_data: Dictionary {kode: [dosen, matkul, prodi]}
        databases: Dictionary pilihan valid
        generations: Jumlah generasi (default: 10)
        mutation_rate: Probabilitas mutasi (default: 0.15)
        elite_size: Jumlah elite (default: 2)
        early_stopping: Stop jika optimal (default: False) ✅ BARU
    
    Returns:
        Dictionary hasil GA lengkap
    """
    
    # ========== INITIALIZATION ==========
    populasi = buat_populasi_list(populasi_data, databases)
    populasi = evaluasi_populasi(populasi)
    populasi_awal = copy.deepcopy(populasi)
    
    # History tracking
    history = {
        'best_fitness': [],
        'avg_fitness': [],
        'worst_fitness': [],
        'best_konflik': [],
        'generations': []
    }
    
    # ========== EVOLUTION ==========
    for gen in range(1, generations + 1):
        offspring = []
        target_size = len(populasi)
        
        # ===== CROSSOVER =====
        while len(offspring) < target_size:
            parent1 = seleksi_tournament(populasi, tournament_size=3)
            parent2 = seleksi_tournament(populasi, tournament_size=3)
            
            children = crossover(parent1, parent2, gen)
            
            for child in children:
                offspring.append(child)
                if len(offspring) >= target_size:
                    break
        
        # Trim to size
        offspring = offspring[:target_size]
        
        # ===== MUTATION =====
        # Adaptive mutation: higher in early generations
        current_rate = mutation_rate * (1.5 if gen <= 3 else 1.0)
        
        for child in offspring:
            mutasi(child, current_rate, databases)
        
        # ===== IMMIGRATION (every 3 generations) =====
        # Disabled to maintain population integrity
        # Immigration can cause duplicate signatures which reduces population size
        # if gen % 3 == 0:
        #     num_immigrants = min(2, len(offspring) // 10)
        #     for i in range(num_immigrants):
        #         immigrant = create_immigrant(gen, populasi_data, databases)
        #         offspring[i] = immigrant
        
        # ===== EVALUATION =====
        offspring = evaluasi_populasi(offspring)
        
        # ===== REMOVE DUPLICATES =====
        offspring = remove_duplicates(offspring)
        
        # ===== FILL MISSING (DETERMINISTIC) =====
        # Ensure all input signatures are present
        while len(offspring) < target_size:
            # Get existing signatures
            existing_sigs = {(k['data'][0], k['data'][1], k['data'][2]) for k in offspring}
            
            # Get all input signatures
            all_sigs = {(populasi_data[key][0], populasi_data[key][1], populasi_data[key][2]) 
                       for key in populasi_data.keys()}
            
            # Find missing
            missing_sigs = all_sigs - existing_sigs
            
            if missing_sigs:
                # Pick first missing signature
                missing_sig = list(missing_sigs)[0]
                
                # Find the key for this signature
                for key, data in populasi_data.items():
                    if (data[0], data[1], data[2]) == missing_sig:
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
                        offspring.append(filler)
                        break
            else:
                # All signatures present, break
                break
        
        # Trim to exact size
        offspring = offspring[:target_size]
        
        # Re-evaluate after filling
        offspring = evaluasi_populasi(offspring)
        
        # ===== ELITISM REPLACEMENT =====
        populasi = elitism_replacement(populasi, offspring, elite_size)
        
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
        
        print(f"Gen {gen}: Best Fitness={best_fitness:.4f}, Avg Fitness={avg_fitness:.4f}, Konflik={best_konflik}")
        
        # ===== EARLY STOPPING (OPTIONAL) =====
        if early_stopping:  # ✅ HANYA JIKA early_stopping=True
            MIN_GENERATIONS = 5
            if gen >= MIN_GENERATIONS and best_fitness >= 0.99 and best_konflik == 0:
                print(f"✓ Optimal solution found at generation {gen} (early stopping)!")
                break
    
    # ========== VALIDATION: ENSURE COMPLETE POPULATION ==========
    # Make sure populasi has all input signatures
    expected_size = len(populasi_data)
    actual_size = len(populasi)
    
    if actual_size < expected_size:
        print(f"[INFO] Filling missing chromosomes ({actual_size}/{expected_size})...")
        
        # Get existing signatures
        existing_sigs = {(k['data'][0], k['data'][1], k['data'][2]) for k in populasi}
        
        # Find and fill missing
        for key, data in populasi_data.items():
            sig = (data[0], data[1], data[2])
            if sig not in existing_sigs:
                filler = {
                    'kode': f"FINAL_{key}",
                    'data': [
                        data[0], data[1], data[2],
                        random.choice(databases['sks']),
                        random.choice(databases['hari']),
                        random.choice(databases['waktu']),
                        random.choice(databases['ruangan'])
                    ],
                    'generation': gen,
                    'konflik': 0,
                    'fitness': 0.0
                }
                populasi.append(filler)
                existing_sigs.add(sig)
        
        # Re-evaluate after filling
        populasi = evaluasi_populasi(populasi)
        print(f"[INFO] Population size after validation: {len(populasi)}/{expected_size}")
    
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
            'early_stopping': early_stopping  # ✅ TRACK PARAMETER
        }
    }


# ========== HELPER FUNCTIONS ==========

def get_summary_stats(results):
    """Get statistik ringkasan dari hasil GA"""
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
    """
    Format detail kromosom untuk display
    Struktur: [dosen, matkul, prodi, sks, hari, waktu, ruangan]
    """
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
    """
    Filter: 1 jadwal terbaik per kombinasi (dosen, matkul, prodi)
    
    Args:
        populasi: List kromosom
    
    Returns:
        List kromosom tanpa duplikasi (dosen, matkul, prodi)
    """
    unique_dict = {}
    
    for krom in populasi:
        key = (krom['data'][0], krom['data'][1], krom['data'][2])
        
        if key not in unique_dict or krom['fitness'] > unique_dict[key]['fitness']:
            unique_dict[key] = krom
    
    return list(unique_dict.values())


def buat_tabel_rekomendasi_jadwal(results, filter_duplicates=True):  # ✅ TAMBAH PARAMETER
    """
    Buat tabel rekomendasi jadwal
    
    Args:
        results: Dictionary hasil dari run_genetic_algorithm
        filter_duplicates: Filter duplikat (dosen, matkul, prodi) atau tidak (default: True)
    
    Returns:
        List of dict untuk tabel rekomendasi
    """
    populasi_akhir = results['populasi_akhir']
    
    # ✅ OPTIONAL FILTERING
    if filter_duplicates:
        populasi_filtered = filter_unique_dosen_matkul_prodi(populasi_akhir)
    else:
        populasi_filtered = populasi_akhir  # TAMPILKAN SEMUA
    
    populasi_sorted = sorted(populasi_filtered, key=lambda x: (x['data'][0], x['data'][1]))
    
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
    """
    Export hasil GA ke CSV
    
    Args:
        results: Dictionary hasil dari run_genetic_algorithm
        output_file: Path ke file output CSV
        filter_duplicates: Filter duplikat atau tidak (default: True)
    """
    populasi_akhir = results['populasi_akhir']
    
    if filter_duplicates:
        populasi_filtered = filter_unique_dosen_matkul_prodi(populasi_akhir)
    else:
        populasi_filtered = populasi_akhir
    
    populasi_sorted = sorted(populasi_filtered, key=lambda x: x['data'][0])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Kode', 'Dosen', 'Mata Kuliah', 'Prodi', 'SKS',
            'Hari', 'Waktu', 'Ruangan', 'Fitness', 'Konflik', 'Generasi'
        ]
        
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
    """
    Parse CSV input: Dosen, Mata Kuliah, Prodi
    
    Args:
        csv_file: Path ke file CSV
    
    Returns:
        Tuple: (populasi_dict, databases)
    """
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
            dosen = row['Dosen'].strip()
            matkul = row['Mata Kuliah'].strip()
            prodi = row['Prodi'].strip()
            
            populasi_dict[kode] = [dosen, matkul, prodi]
    
    return populasi_dict, databases


# ========== PRINT FUNCTIONS ==========

def print_tabel_rekomendasi(tabel_rekomendasi):
    """Print tabel rekomendasi jadwal"""
    print("\n" + "="*120)
    print(" " * 40 + "TABEL REKOMENDASI JADWAL")
    print("="*120)
    
    print(f"{'No':<4} {'Dosen':<25} {'Mata Kuliah':<25} {'Prodi':<20} "
          f"{'SKS':<5} {'Hari':<10} {'Waktu':<15} {'Ruangan':<10} {'Fit':<6} {'Konf':<5}")
    print("="*120)
    
    for row in tabel_rekomendasi:
        print(f"{row['No']:<4} {row['Dosen']:<25} {row['Mata Kuliah']:<25} {row['Prodi']:<20} "
              f"{row['SKS']:<5} {row['Hari']:<10} {row['Waktu']:<15} {row['Ruangan']:<10} "
              f"{row['Fitness']:<6.4f} {row['Konflik']:<5}")
    
    print("="*120)
    print(f"\n📊 Total Schedules: {len(tabel_rekomendasi)}")
    
    total_konflik = sum(row['Konflik'] for row in tabel_rekomendasi)
    print(f"⚠️  Total Conflicts: {total_konflik}")
    
    if total_konflik == 0:
        print("✓ OPTIMAL SCHEDULE! No conflicts.")
    else:
        print(f"⚠️  {total_konflik} conflicts need to be resolved.")
    
    print("="*120 + "\n")


def print_summary(results):
    """Print summary hasil GA"""
    populasi_filtered = filter_unique_dosen_matkul_prodi(results['populasi_akhir'])
    
    print("\n" + "="*70)
    print("GENETIC ALGORITHM RESULTS SUMMARY")
    print("="*70)
    
    print(f"\n📊 STATISTICS:")
    print(f"  • Total Generations: {results['total_generations']}")
    print(f"  • Population Size: {results['parameters']['population_size']}")
    print(f"  • Mutation Rate: {results['parameters']['mutation_rate']}")
    print(f"  • Elite Size: {results['parameters']['elite_size']}")
    print(f"  • Early Stopping: {results['parameters']['early_stopping']}")
    
    history = results['history']
    print(f"\n📈 EVOLUTION PROGRESS:")
    print(f"  • Initial Fitness: {history['best_fitness'][0]:.4f}")
    print(f"  • Final Fitness: {history['best_fitness'][-1]:.4f}")
    print(f"  • Fitness Improvement: {results['improvement']['fitness_improvement']:.4f}")
    print(f"  • Initial Conflicts: {history['best_konflik'][0]}")
    print(f"  • Final Conflicts: {history['best_konflik'][-1]}")
    print(f"  • Conflict Reduction: {results['improvement']['konflik_reduction']}")
    
    print(f"\n✅ FINAL RESULTS:")
    print(f"  • Total Unique Schedules: {len(populasi_filtered)}")
    
    if history['best_konflik'][-1] == 0:
        print(f"  • Status: ✓ OPTIMAL (No conflicts)")
    else:
        print(f"  • Status: ⚠️  SUBOPTIMAL ({history['best_konflik'][-1]} conflicts)")
    
    print("\n" + "="*70 + "\n")