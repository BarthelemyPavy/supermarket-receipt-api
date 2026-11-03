# Supermarket Receipt API — fin de J2

Cette version rassemble le travail réalisé pendant les journées 1 et 2 : corrections du
moteur de caisse, tests unitaires, tests de l'API et pipeline GitHub Actions. Elle sert de
point de reprise pour la suite du module Usine logicielle & CI/CD.

Le [starter et l'énoncé de J1](https://github.com/BarthelemyPavy/supermarket-receipt-api/tree/6fa850c)
restent disponibles dans l'historique. Sur `main`, les deux défauts étudiés en J1 sont
corrigés : l'arrondi des remises et la promotion « trois pour le prix de deux ».

## Installer et vérifier le projet

Prérequis : Python 3.13 et `uv`. Depuis la racine du dépôt :

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/unit tests/integration -v --cov=supermarket_receipt_api --cov-branch --cov-report=term-missing --cov-report=html:htmlcov
uv build
```

`pyproject.toml` déclare les dépendances ; `uv.lock` fixe leur résolution. Le package local
est installé depuis `src/` en mode éditable. Le rapport de couverture est généré dans
`htmlcov/index.html`, et les paquets Python dans `dist/`. Aucun seuil de couverture n'est
imposé : une ligne exécutée ne garantit pas que les assertions détectent tous les bugs.

Pour lancer l'API :

```bash
uv run python -m supermarket_receipt_api
# Pendant le développement, avec rechargement automatique :
uv run uvicorn supermarket_receipt_api.main:app --reload
```

La documentation HTTP est accessible sur `http://127.0.0.1:8000/docs`.

## Organisation du code

```text
src/supermarket_receipt_api/
  checkout.py       Catalogue et fonctions métier
  schemas.py        Modèles Pydantic des requêtes et réponses
  main.py           Application FastAPI et routes HTTP
tests/
  unit/             Tests des fonctions métier, dont les 100 cas de départ
  integration/      Routes, validation, vrai moteur et sérialisation ensemble
.github/
  actions/preparer/action.yml    Préparation commune aux jobs
  workflows/ci.yml               Pipeline de fin de J2
```

Le [contrat métier et HTTP](docs/contrat.md) est la référence pour les résultats attendus.
Les tests unitaires appellent les fonctions directement. Les tests de l'API utilisent
`TestClient` en mémoire : ils ne nécessitent ni serveur réseau, ni base de données, ni
conteneur. Docker sera abordé en J3.

## Ce que fait la CI

Le workflow [CI J2](.github/workflows/ci.yml) s'exécute à chaque mise à jour d'une pull
request, à chaque push sur `main` et sur déclenchement manuel.

1. La matrice `include` crée les jobs **CI (lint)**, **CI (format)** et **CI (tests)**.
   Chaque job a son runner, récupère le code et appelle l'action composite `preparer`
   pour installer Python, `uv` et les dépendances verrouillées, avec le cache `uv`.
2. Le job de tests exécute les suites unitaires et HTTP et conserve le rapport HTML dans
   l'artifact **couverture**, y compris si un test échoue après la génération du rapport.
3. Le job **build** attend la réussite des trois contrôles, lance `uv build` et conserve
   le wheel et l'archive source dans l'artifact **distribution**.
4. Sur une PR, le job **commenter** attend les contrôles et le build, puis publie le lien
   du run. Ce job seul demande la permission `pull-requests: write` ; il est skip sur un
   push sur `main`. Une PR issue d'un fork n'obtient généralement pas cette permission.

Les artifacts sont téléchargeables depuis la page du run pendant sept jours. Leur nom
est distinct du chemin local des fichiers : `couverture` contient `htmlcov/`, et
`distribution` contient `dist/`. Le cache accélère l'installation des dépendances.

Un nouveau commit sur une PR annule son ancien run encore en cours. Les runs sur `main`
ne sont pas annulés automatiquement. Les règles de fusion se configurent dans les
paramètres GitHub du dépôt ; elles ne sont pas activées par le YAML. Les quatre checks
présentés en cours sont `CI (lint)`, `CI (format)`, `CI (tests)` et `build`.

## Assistants IA et travail individuel

Les assistants IA sont autorisés en mode tuteur : questions, indices et relecture.
Chaque étudiant doit pouvoir expliquer ses choix et adapter son travail sans assistant.
Le cadre et les hooks fournis restent décrits dans [AGENTS.md](AGENTS.md),
[CLAUDE.md](CLAUDE.md) et [docs/tutorat.md](docs/tutorat.md).

## Origine et ressources

Le scénario est une adaptation pédagogique du
[Supermarket Receipt Refactoring Kata d'Emily Bache](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata).
Les règles de cette API sont celles du contrat fourni dans le dépôt.

La progression CI/CD s'inspire aussi de
[UPenn — CI/CD with GitHub Actions](https://www.cis1912.org/labs/11-13-cicd/) et de
[Helsinki — DevOps with Docker, Deployment pipelines](https://github.com/docker-hy/docker-hy.github.io/blob/master/docs/part-3/section-2.md).
