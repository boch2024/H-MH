
from collections import deque

solution_init = [
    [4, 4, 0],
    [0, 1, 8]
]

cout = [
    [5, 3, 4],
    [6, 7, 2]
]


def calculer_cout_total(solution, cout):
    total = 0

    for i in range(len(solution)):
        for j in range(len(solution[i])):
            total += solution[i][j] * cout[i][j]

    return total

def gener_voisins(solution_init):
    voisins = []
    nb_depots = len(solution_init)
    nb_magasins = len(solution_init[0])

    for i1 in range(nb_depots):
        for i2 in range(nb_depots):
            if i1 == i2:
                continue

            for j1 in range(nb_magasins):
                for j2 in range(nb_magasins):
                    if j1 == j2:
                        continue

                    if solution_init[i1][j1] < 1 or solution_init[i2][j2] < 1:
                        continue

                    voisin = [ligne.copy() for ligne in solution_init]

                    voisin[i1][j1] -= 1
                    voisin[i1][j2] += 1
                    voisin[i2][j1] += 1
                    voisin[i2][j2] -= 1

                    if voisin not in voisins:
                        voisins.append(voisin)

    return voisins

def recherche_tabou_transport(
    couts,
    solution_initiale,
    nombre_iterations,
    taille_tabu
):
    solution_actuelle = [ligne.copy() for ligne in solution_initiale]

    meilleure_solution = [ligne.copy() for ligne in solution_actuelle]
    meilleur_cout = calculer_cout_total(solution_actuelle, couts)

    tabu_list = deque(maxlen=taille_tabu)

    for _ in range(nombre_iterations):
        voisins = gener_voisins(solution_actuelle)
        voisins = [v for v in voisins if v not in tabu_list]

        if not voisins:
            break

        solution_actuelle = min(
            voisins,
            key=lambda x: calculer_cout_total(x, couts)
        )

        cout_actuel = calculer_cout_total(solution_actuelle, couts)

        tabu_list.append([ligne.copy() for ligne in solution_actuelle])

        if cout_actuel < meilleur_cout:
            meilleure_solution = [
                ligne.copy() for ligne in solution_actuelle
            ]
            meilleur_cout = cout_actuel

    return meilleure_solution, meilleur_cout


nombre_iterations = 1000
taille_tabu = 10

meilleure_solution, meilleur_cout = recherche_tabou_transport(
    cout,
    solution_init,
    nombre_iterations,
    taille_tabu
)

print("--- Recherche Taboue : Problème de Transport ---")
print("Matrice des livraisons optimale (Dépôts x Magasins) :")

for i, ligne in enumerate(meilleure_solution):
    print(f"Dépôt D{i + 1} : {ligne}")

print("Coût total minimal de transport :", meilleur_cout)
print("Solution initiale :", solution_init)
print("Coût initial :", calculer_cout_total(solution_init, cout))
print("Voisins :", len(gener_voisins(solution_init)))
for v in gener_voisins(solution_init):
    print(v, calculer_cout_total(v, cout))
