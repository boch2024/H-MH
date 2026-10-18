1. **td2_exercie2.py** — Problème de Transport (Recherche Tabou)

Ce script résout un problème d'optimisation de coût de transport entre plusieurs dépôts et magasins.

- **Problème :** Minimiser le coût total de transport pour acheminer des quantités données de marchandises depuis des dépôts vers des magasins.
- **Méthode :** Recherche Tabou (`recherche_tabou_transport`).
- **Fonctionnalités clés :**
  * Modélisation de la matrice des livraisons et de la matrice des coûts.
  * Génération de voisinage par permutation/répartition de flux entre dépôts et magasins (`gener_voisins`).
  * Gestion d'une liste tabou avec `collections.deque` pour éviter les cycles.

<img width="550" height="400" alt="image" src="https://github.com/user-attachments/assets/a85e9f7b-7e00-461c-84c7-a65308374abf" />

2. **metaheuristique.py** — Problème du Voyageur de Commerce (TSP)

- **Problème :** Déterminer le circuit fermé le plus court passant par 8 villes, en visitant chaque ville exactement une fois.
- **Métaheuristiques Implémentées :**
  * **Recherche Tabou** (`recherche_tabou`) : Recherche locale guidée par l'historique des solutions récemment explorées.
  * **Recuit Simulé** (`recuit_simule`) : Approche stochastique qui accepte temporairement des solutions moins bonnes selon la probabilité de Boltzmann ($e^{-\Delta / T}$) pour sortir des minima locaux.
- **Visualisation Graphique :**
  * Utilisation de **Matplotlib** (`tracer_comparaison_tsp`) pour afficher côte à côte les circuits trouvés par les deux méthodes sous forme de graphes circulaires orientés, avec les distances totales minimales.

<img width="550" height="400" alt="TSP Visualisation" src="https://github.com/user-attachments/assets/85c0f28f-32c4-475a-99a6-0d7e505e3adb" />

