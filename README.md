# Assistant étudiant — V1

Prototype local et simple pour poser les bases de ton IA perso.

## Ce que fait cette V1
- interface web propre,
- 3 modes : expliquer / résumer / réviser,
- réponse locale gratuite par défaut,
- structure prête à accueillir une API de modèle plus tard.

## Installation

### 1. Ouvre un terminal dans ce dossier
### 2. Installe les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lance l'application
```bash
python app.py
```

Puis ouvre dans ton navigateur :
http://127.0.0.1:5000

## Étape suivante
Quand tu voudras brancher un vrai modèle :
- installe `openai`
- ajoute ta clé API dans les variables d'environnement
- dans `app.py`, remplace :
```python
answer = fake_local_response(message, mode)
```
par :
```python
answer = openai_like_response(message, mode)
```

## Améliorations futures
1. Ajouter une vraie mémoire utilisateur
2. Ajouter une recherche de sources fiables
3. Ajouter un filtre de citations
4. Ajouter un espace "fiche de révision"
5. Ajouter un profil étudiant personnalisé
