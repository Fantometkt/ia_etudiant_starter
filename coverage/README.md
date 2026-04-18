# Coverage Benchmark

## Objectif
Mesurer la couverture réelle de l'IA étudiante sur l'ensemble des grandes familles de matières du collège au master.

## Logique
On ne teste pas seulement la robustesse interne.
On teste aussi l'étendue disciplinaire.

## Structure
- `coverage_matrix.py` : définition des familles de matières, niveaux et tests de couverture
- `selftest_coverage.py` : exécution du benchmark coverage
- `run_selftest_coverage.py` : point de lancement terminal

## Finalité
Identifier :
- les familles déjà solides
- les familles moyennes
- les familles faibles
- les trous de couverture