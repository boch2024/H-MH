import math
import random
from collections import deque
from matplotlib import pyplot as plt
from neo4j import GraphDatabase

INF = float("inf")

matrice_distances = [
    [0, 14, 15, INF, INF, INF, INF, 17],
    [14, 0, 13, 14, 20, INF, INF, 21],
    [15, 13, 0, 11, 21, 17, 9, 9],
    [INF, 14, 11, 0, 11, 10, 8, 20],
    [INF, 20, 21, 11, 0, 15, 18, INF],
    [INF, INF, 17, 10, 15, 0, 9, INF],
    [INF, INF, 9, 8, 18, 9, 0, 13],
    [17, 21, 9, 20, INF, INF, 13, 0]
]

solution_initiale = [0, 1, 2, 3, 4, 5, 6, 7]


def calculate_distance(solution, matrice_distances):
    distance_totale = 0
    n = len(solution)

    for i in range(n):
        u = solution[i]
        v = solution[(i + 1) % n]

        if matrice_distances[u][v] == INF:
            return INF

        distance_totale += matrice_distances[u][v]

    return distance_totale


def generer_voisins(solution, matrice_distances):
    voisins = []

    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            voisin = solution.copy()
            voisin[i], voisin[j] = voisin[j], voisin[i]

            if calculate_distance(voisin, matrice_distances) != INF:
                voisins.append(voisin)

    return voisins


def recherche_tabou(matrice_distances, max_iter=100, tabou_length=10):
    actuel = solution_initiale.copy()

    if calculate_distance(actuel, matrice_distances) == INF:
        raise ValueError("La solution initiale est invalide.")

    meilleure_solution = actuel.copy()
    meilleure_distance = calculate_distance(actuel, matrice_distances)
    tabou_list = deque(maxlen=tabou_length)

    for _ in range(max_iter):
        voisins = generer_voisins(actuel, matrice_distances)
        voisins = [v for v in voisins if v not in tabou_list]

        if not voisins:
            break

        meilleur_voisin = min(
            voisins,
            key=lambda v: calculate_distance(v, matrice_distances)
        )

        actuel = meilleur_voisin.copy()
        distance_actuelle = calculate_distance(actuel, matrice_distances)
        tabou_list.append(actuel.copy())

        if distance_actuelle < meilleure_distance:
            meilleure_solution = actuel.copy()
            meilleure_distance = distance_actuelle

    return meilleure_solution, meilleure_distance


def recuit_simule(
    matrice_distances,
    T_init=100.0,
    T_min=1,
    alpha=0.95,
    iter_par_palier=10
):
    actuel = solution_initiale.copy()

    if calculate_distance(actuel, matrice_distances) == INF:
        raise ValueError("La solution initiale est invalide.")

    cout_actuel = calculate_distance(actuel, matrice_distances)
    meilleure_solution = actuel.copy()
    meilleure_distance = cout_actuel
    T = T_init
    n = len(actuel)

    while T > T_min:
        for _ in range(iter_par_palier):
            voisin = actuel.copy()
            i, j = random.sample(range(n), 2)
            voisin[i], voisin[j] = voisin[j], voisin[i]

            cout_voisin = calculate_distance(voisin, matrice_distances)

            if cout_voisin == INF:
                continue

            delta = cout_voisin - cout_actuel

            if delta < 0 or random.random() < math.exp(-delta / T):
                actuel = voisin
                cout_actuel = cout_voisin

                if cout_actuel < meilleure_distance:
                    meilleure_solution = actuel.copy()
                    meilleure_distance = cout_actuel

        T *= alpha

    return meilleure_solution, meilleure_distance


def tracer_comparaison_tsp(
    sol_rt, dist_rt, sol_rs, dist_rs, matrice_distances
):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    n = len(matrice_distances)

    angles = [2 * math.pi * i / n for i in range(n)]
    positions = [(math.cos(a), math.sin(a)) for a in angles]

    solutions = [
        (sol_rt, dist_rt, "Recherche Tabou", "royalblue"),
        (sol_rs, dist_rs, "Recuit Simulé", "crimson")
    ]

    for ax, (solution, distance, titre, couleur) in zip(axes, solutions):
        for ville, (x, y) in enumerate(positions):
            ax.scatter(x, y, color="black", s=70, zorder=3)
            ax.text(
                x * 1.15, y * 1.15, f"Ville {ville + 1}",
                ha="center", va="center", fontsize=9
            )

        circuit = solution + [solution[0]]

        for i in range(len(circuit) - 1):
            u, v = circuit[i], circuit[i + 1]
            x1, y1 = positions[u]
            x2, y2 = positions[v]

            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    color=couleur,
                    linewidth=2
                )
            )

        ax.set_title(f"{titre}\nDistance totale : {distance:.2f}")
        ax.set_aspect("equal")
        ax.axis("off")

    plt.suptitle("Comparaison des algorithmes TSP")
    plt.tight_layout()
    plt.show()

def ingestion_neo4j(tx,solution,matrice_distances):
    for i in range(len(solution)):
        cur_index=solution[i]
        next_index=solution[(i+1)%len(solution)]
        ville=f"ville_{cur_index+1}"
        next_ville=f"ville_{next_index+1}"
        distance=matrice_distances[cur_index][next_index]
        tx.run(
            "MERGE (v1:Ville {nom: $ville}) "
            "MERGE (v2:Ville {nom: $next_ville}) "
            "MERGE (v1)-[:CHEMIN {distance: $distance}]->(v2)",
            ville=ville,
            next_ville=next_ville,
            distance=distance)  
def sauvegarder_dans_neo4j(solution,matrice_distances):
    driver=GraphDatabase.driver("neo4j://127.0.0.1:7687",auth=("neo4j","bech1234"))
    with driver.session()as session:
        session.execute_write(ingestion_neo4j,solution,matrice_distances)
    driver.close()
if __name__ == "__main__":
    random.seed(42)

    sol_rt, dist_rt = recherche_tabou(
        matrice_distances, max_iter=100, tabou_length=10
    )

    sol_rs, dist_rs = recuit_simule(
        matrice_distances,
        T_init=100.0,
        T_min=1,
        alpha=0.95,
        iter_par_palier=10
    )

    print("=" * 55)
    print("COMPARAISON DES ALGORITHMES TSP")
    print("=" * 55)

    print("\n1. RECHERCHE TABOUE")
    print("Meilleure solution :", [v + 1 for v in sol_rt] + [sol_rt[0] + 1])
    print(f"Distance minimale : {dist_rt:.2f}")

    print("\n2. RECUIT SIMULE")
    print("Meilleure solution :", [v + 1 for v in sol_rs] + [sol_rs[0] + 1])
    print(f"Distance minimale : {dist_rs:.2f}")

    if dist_rt < dist_rs:
        print("\nMeilleur résultat : Recherche Taboue")
    elif dist_rs < dist_rt:
        print("\nMeilleur résultat : Recuit Simulé")
    else:
        print("\nLes deux algorithmes ont trouvé la même distance.")

    sauvegarder_dans_neo4j(sol_rt, matrice_distances)

    tracer_comparaison_tsp(
        sol_rt, dist_rt, sol_rs, dist_rs, matrice_distances
    )
