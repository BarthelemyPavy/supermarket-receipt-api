# Instructions du starter J1

Ce dépôt est un exercice pédagogique, pas le corrigé du module.

- Respecter le contrat dans `docs/contrat.md`. Les tests fournis montrent comment commencer et ne couvrent pas toutes les règles. Ne modifier le comportement métier qu'en réponse à une demande explicite, avec un test de régression.
- Ne pas ajouter d'emblée le pipeline final, Docker, les tests HTTP ou le déploiement. Les étudiants les construisent progressivement selon les consignes de séance.
- Utiliser des chaînes entre guillemets doubles et documenter chaque fonction, méthode et classe, avec paramètres, retour, erreurs et effets de bord éventuels.
- Refuser explicitement les entrées invalides. Ne pas accepter d'alias implicites de champs ni de conversion silencieuse.
- Gérer les dépendances avec `uv`, `pyproject.toml` et `uv.lock`. Ne pas créer de `requirements.txt` parallèle.
- Après modification, exécuter `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` et `uv run pytest -q`.
- Ne pas installer de runner ni lancer de déploiement sans demande explicite. Le dépôt de travail de l'étudiant reste privé.
- Ne pas publier de corrigé, de notes enseignant, de token, de clé ou de fichier de configuration du runner.
- Ne pas utiliser le skill `context-driven-development` pour ce projet.
