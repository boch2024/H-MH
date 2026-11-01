# Optimisation par Métaheuristiques & Graph Database

Ce dépôt regroupe deux problèmes d'optimisation combinatoire résolus par des métaheuristiques (Recherche Tabou, Recuit Simulé), ainsi que le stockage et l'interrogation de la solution du TSP dans une base de données orientée graphe (**Neo4j**).

## Sommaire
1. [Problème de Transport (Recherche Tabou)](#1-td2_exercie2py--problème-de-transport-recherche-tabou)
2. [Problème du Voyageur de Commerce (TSP)](#2-metaheuristiquepy--problème-du-voyageur-de-commerce-tsp)
3. [Stockage de la solution dans Neo4j (Graph Database)](#3-stockage-de-la-solution-dans-neo4j-graph-database)
4. [Technologies utilisées](#technologies-utilisées)

---

## 1. `td2_exercie2.py` — Problème de Transport (Recherche Tabou)

Ce script résout un problème d'optimisation de coût de transport entre plusieurs dépôts et magasins.

- **Problème :** minimiser le coût total de transport pour acheminer des quantités données de marchandises depuis des dépôts vers des magasins.
- **Méthode :** Recherche Tabou (`recherche_tabou_transport`).
- **Fonctionnalités clés :**
  - Modélisation de la matrice des livraisons et de la matrice des coûts.
  - Génération de voisinage par permutation/répartition de flux entre dépôts et magasins (`gener_voisins`).
  - Gestion d'une liste tabou avec `collections.deque` pour éviter les cycles.

<img width="550" height="400" alt="image" src="https://github.com/user-attachments/assets/a85e9f7b-7e00-461c-84c7-a65308374abf" />

---

## 2. `metaheuristique.py` — Problème du Voyageur de Commerce (TSP)

- **Problème :** déterminer le circuit fermé le plus court passant par 8 villes, en visitant chaque ville exactement une fois.
- **Métaheuristiques implémentées :**
  - **Recherche Tabou** (`recherche_tabou`) : recherche locale guidée par l'historique des solutions récemment explorées.
  - **Recuit Simulé** (`recuit_simule`) : approche stochastique qui accepte temporairement des solutions moins bonnes selon la probabilité de Boltzmann ($e^{-\Delta / T}$), afin de sortir des minima locaux.
- **Visualisation :** **Matplotlib** (`tracer_comparaison_tsp`) affiche côte à côte les circuits trouvés par les deux méthodes sous forme de graphes circulaires orientés, avec les distances totales minimales.

<img width="550" height="400" alt="TSP Visualisation" src="https://github.com/user-attachments/assets/85c0f28f-32c4-475a-99a6-0d7e505e3adb" />

---

## 3. Stockage de la solution dans Neo4j (Graph Database)

Le circuit optimal trouvé pour le TSP est stocké dans une base **Neo4j** afin de pouvoir l'interroger et l'explorer sous forme de graphe.

### Modèle de données

| Élément | Type | Propriétés |
|---|---|---|
| `(:Ville)` | Nœud | `nom` (ex. `"ville_1"`) |
| `[:CHEMIN]` | Relation orientée | `distance` (entier) |

Le graphe contient **8 nœuds** (villes) et **8 relations** `CHEMIN` qui forment le circuit fermé.

### Création du graphe

```cypher
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
```

### Requête de consultation

```cypher
MATCH (v:Ville)-[r:CHEMIN]->(u:Ville)
RETURN v.nom AS Depart, u.nom AS Arrivee, r.distance AS Distance
```

### Circuit obtenu

```
ville_8 → ville_1 → ville_2 → ville_4 → ville_5 → ville_6 → ville_7 → ville_3 → ville_8
```

### Visualisation

Neo4j Explore (Default Perspective, *Force-based layout*) montre le circuit sous forme de cycle orienté :

<img width="1241" height="850" alt="image" src="https://github.com/user-attachments/assets/19e2eae9-c2e2-4121-a576-b6eb8915225a" />

<img width="1272" height="857" alt="image" src="https://github.com/user-attachments/assets/0081eea8-6812-46e1-8dbd-fffa747ef57c" />


### Pourquoi une base orientée graphe ?
- Le circuit TSP est naturellement un graphe (villes = nœuds, routes = relations).
- Les requêtes Cypher permettent d'explorer la solution (voisins, sous-chemins, distance totale) sans jointures.
- La solution stockée peut servir de base de connaissances pour une approche **GraphRAG** : un LLM interroge le graphe pour répondre en langage naturel (ex. « Quelle ville visite-t-on après ville_4 ? »).

---

## Technologies utilisées
- Python (`collections.deque`, `random`, `math`)
- Matplotlib
- Neo4j + Cypher
