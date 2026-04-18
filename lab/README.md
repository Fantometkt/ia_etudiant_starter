# LAB — Auto-amélioration contrôlée

## Objectif
Construire une boucle d’auto-amélioration continue pour l’IA académique, sans modifier directement la version stable.

## Principe
Le labo ne remplace jamais la version stable directement.

Il fonctionne en 5 étapes :
1. Générer un candidat
2. Enregistrer le candidat
3. Évaluer le candidat
4. Comparer le candidat à la baseline
5. Rejeter, conserver ou promouvoir

## Niveaux de boucle
- Boucle courte : micro-tests rapides
- Boucle moyenne : comparaison de candidats survivants
- Boucle longue : benchmark lourd + validation humaine

## Règle fondamentale
L’IA peut proposer en boucle.
Seuls les candidats validés peuvent être promus.

## Dossiers
- `state/` : état courant du labo
- `candidates/` : candidats sauvegardés
- `reports/` : rapports d’évaluation
- `snapshots/` : copies de références stables