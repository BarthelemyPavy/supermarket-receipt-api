# Supermarket Receipt API — starter J1

Une petite enseigne veut livrer une nouvelle version de son moteur de caisse. L'API et les calculs existent déjà, mais l'équipe ne dispose que de quelques tests d'exemple. Votre mission : déterminer quels comportements méritent d'être sécurisés, apporter des preuves et préparer une modification livrable.

## Démarrer

Python 3.13 et `uv` doivent être disponibles. Ouvrez un terminal dans ce dossier :

```bash
uv sync --locked
uv run pytest tests/unit
```

`pyproject.toml` déclare les dépendances et le package local ; `uv.lock` fixe leur résolution. `uv sync` installe aussi le package depuis `src/` en mode éditable : les modifications du code sont prises en compte sans réinstallation. N'ajoutez pas de `requirements.txt` ni d'installation manuelle avec `pip`.

Les tests fournis passent : ils montrent comment démarrer, pas que tous les comportements sont corrects. Lisez [le contrat métier](docs/contrat.md), puis explorez le catalogue `CATALOG` et les fonctions dans `src/supermarket_receipt_api/services/checkout.py`, ainsi que `tests/unit/`.

## Se repérer dans le projet

```text
.
├── src/
│   └── supermarket_receipt_api/
│       ├── __init__.py           Création de l'application et enregistrement des routes
│       ├── __main__.py           Lancement local avec python -m
│       ├── routes/               Adaptateurs HTTP : health, catalog et checkout
│       ├── schemas/checkout.py   Modèles Pydantic des requêtes et réponses
│       └── services/checkout.py  Catalogue et fonctions métier à examiner en J1
└── tests/
    └── unit/                    Six cas de départ, à compléter
```

Une requête passe par une **route**, utilise les **schémas** pour valider ses données et appelle les **fonctions métier** du service. Les tests unitaires appellent directement ces fonctions, sans démarrer de serveur. Il n'y a ni base de données ni couche d'accès aux données à configurer.

Pour les séances consacrées à HTTP, l'API se lance avec :

```bash
uv run python -m supermarket_receipt_api
# Ou, avec rechargement automatique pendant le développement :
uv run uvicorn supermarket_receipt_api:app --reload
```

La documentation HTTP est alors disponible sur `http://127.0.0.1:8000/docs`.

## Votre mission

Vous êtes responsables de la confiance que l'équipe peut accorder au ticket de caisse. Construisez une stratégie de tests unitaires à partir du contrat : cas courants, limites pertinentes et erreurs d'entrée. Décidez ce qu'il faut vérifier, dans quel ordre et pourquoi.

Lorsqu'un résultat vous semble incorrect, isolez-le avec un test qui échoue et expliquez ce qu'il démontre avant de corriger le code. Ne modifiez pas une règle métier pour faire passer un test. Si le contrat vous paraît ambigu, posez la question à l'enseignant.

Votre restitution doit permettre à un autre groupe de comprendre :

- Quels comportements vos tests protègent, et lesquels restent à explorer.
- Pourquoi les résultats attendus sont justes, avec un calcul indépendant du code.
- Quelle modification a été faite et quelle régression un test permet d'éviter.
- Comment un autre développeur peut reproduire vos vérifications.

Nous organiserons des points d'échange pendant la séance. À la demande de l'enseignant, un autre groupe introduira une petite modification du code : vos tests devront aider à décider si elle respecte toujours le contrat.

## Git et première CI

Ce dépôt est le **point de départ de la journée 1**. Utilisez « Use this template » pour créer votre propre dépôt **privé**, puis clonez votre copie. Ne copiez pas toutes les branches. Partagez son accès uniquement avec votre binôme et l'enseignant si nécessaire. Un simple clone du dépôt enseignant ne vous donne pas votre propre pipeline GitHub Actions.

La configuration GitHub Actions est à construire pendant la séance. Le premier objectif est de rejouer automatiquement le lint et les tests unitaires **à chaque push sur une branche**, sur un runner GitHub, avec les mêmes dépendances qu'en local. Aucun runner local n'est nécessaire aujourd'hui.

Les jours suivants, vous ajouterez les tests d'intégration HTTP et l'image Docker. La cible de fin de module est un déploiement automatique dans un conteneur local après fusion d'une pull request vers `main`, uniquement si les tests et le build réussissent. Un push direct sur `main` ne doit pas déployer. Seul ce futur job de déploiement utilisera un runner sur votre PC.

## Ce qui n'est pas demandé aujourd'hui

Pas de développement complet d'API, de base de données, de Docker, de Kubernetes ni de tests d'intégration HTTP. Ces derniers seront abordés explicitement en journée 2. Il n'est pas nécessaire de démarrer un serveur pour tester les fonctions métier.

Si l'enseignant autorise un assistant pendant le TD, il intervient uniquement en **mode tuteur** : questions, indices progressifs et relecture de vos essais, sans solution complète ni modification des fichiers. Vous écrivez le code et lancez les commandes vous-mêmes. La présence de cette configuration ne remplace pas la consigne de séance.

Le cadre est défini dans [AGENTS.md](AGENTS.md) et [CLAUDE.md](CLAUDE.md). Les hooks pour Codex et Claude Code sont fournis avec le dépôt ; ils nécessitent un client compatible et leur activation doit être vérifiée. Consulter [le fonctionnement et l'activation du mode tuteur](docs/tutorat.md). Ils ne résolvent pas le TD et n'ajoutent pas de tests métier au starter.

## Origine et ressources

Le scénario s'inspire du [Supermarket Receipt Refactoring Kata d'Emily Bache](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata). Notre API et les règles explicites de ce kit constituent une adaptation pédagogique, pas une reproduction exacte du kata.

Pour la progression CI/CD : [UPenn — CI/CD with GitHub Actions](https://www.cis1912.org/labs/11-13-cicd/) et [Helsinki — DevOps with Docker, Deployment pipelines](https://github.com/docker-hy/docker-hy.github.io/blob/master/docs/part-3/section-2.md).
