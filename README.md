# Supermarket Receipt API — starter J1

Une petite enseigne veut livrer une nouvelle version de son moteur de caisse. L'API et les calculs existent déjà, accompagnés de 100 cas de test qui passent. Votre mission : déterminer ce que cette suite permet d'affirmer, choisir les comportements à sécuriser et préparer une modification livrable.

## Organisation

Le travail est **individuel** : chacun conserve son dépôt privé, ses tests et sa CI. Deux revues ponctuelles se font en binôme : après les tests des autres fonctions, puis après la première CI. Un partage d'écran suffit ; il n'est pas nécessaire de partager un accès en écriture. Chacun effectue ses propres modifications après l'échange.

Le TD comprend **deux parties**, chacune après le cours correspondant : tests unitaires et qualité, puis GitHub Actions. Préparez votre poste avant la séance à l'aide du guide de prérequis. La copie du projet et son premier lancement se font seulement au début de la partie 1, pas à l'ouverture de la journée.

## Partie 1 — Tests unitaires, après le cours tests et qualité

Réutilisez les notions de choix des cas, assertions, lint, formatage, types, coverage et pre-commit.

### Démarrer

Utilisez **Use this template** pour créer votre propre dépôt **privé**, puis clonez votre copie. Ne copiez pas toutes les branches. Partagez son accès avec l'enseignant selon les consignes de séance. Un simple clone du dépôt enseignant ne crée pas votre propre pipeline GitHub Actions.

Python 3.13 et `uv` doivent être disponibles. Ouvrez un terminal à la racine de votre copie :

```bash
uv sync --locked
uv run pytest tests/unit -v
```

`pyproject.toml` déclare les dépendances et le package local ; `uv.lock` fixe leur résolution. `uv sync` installe aussi le package depuis `src/` en mode éditable : les modifications du code sont prises en compte sans réinstallation. N'ajoutez pas de `requirements.txt` ni d'installation manuelle avec `pip`.

Repérez [le contrat métier](docs/contrat.md), le catalogue `CATALOG` et les fonctions dans `src/supermarket_receipt_api/checkout.py`, ainsi que `tests/unit/`.

### Première observation : 100 tests verts

Au premier lancement, la suite affiche **100 cas réussis** (`100 passed`). Que permet ce résultat d'affirmer sur le moteur de caisse ? Préparez votre réponse, puis **attendez la démonstration collective avant de modifier le code ou les tests**.

Sur une fonction déjà testée, nous examinerons un cas annoncé en séance :

1. Déterminer le résultat attendu à partir du contrat, indépendamment du code actuel.
2. Ajouter ce cas à la suite et observer le résultat.
3. En cas d'échec, comprendre s'il vient du test ou de l'implémentation, puis justifier la correction.
4. Relancer toute la suite et expliquer ce que le nouveau test protège.

Les 100 cas sont le point de départ, **pas un quota à atteindre**. Après cette démonstration, à vous de rechercher d'autres comportements : une valeur différente n'apporte pas nécessairement une information nouvelle.

### Se repérer dans le projet

```text
.
├── src/
│   └── supermarket_receipt_api/
│       ├── __init__.py    Identification du package Python
│       ├── __main__.py    Lancement local avec python -m
│       ├── main.py        Application FastAPI et endpoints HTTP
│       ├── schemas.py     Modèles Pydantic des requêtes et réponses
│       └── checkout.py    Catalogue et fonctions métier à examiner en J1
└── tests/
    └── unit/                    100 cas de départ ; une stratégie à enrichir
```

`main.py` reçoit les requêtes HTTP, `schemas.py` décrit les données acceptées et `checkout.py` calcule les tickets. Les tests unitaires appellent directement ces fonctions, sans démarrer de serveur. Il n'y a ni base de données ni couche d'accès aux données à configurer.

Pour les séances consacrées à HTTP, l'API se lance avec :

```bash
uv run python -m supermarket_receipt_api
# Ou, avec rechargement automatique pendant le développement :
uv run uvicorn supermarket_receipt_api.main:app --reload
```

La documentation HTTP est alors disponible sur `http://127.0.0.1:8000/docs`.

### Votre mission

Vous êtes responsables de la confiance que l'équipe peut accorder au ticket de caisse. Construisez une stratégie de tests unitaires à partir du contrat, autour de quatre axes :

| Axe | Question à se poser |
| --- | --- |
| **Fonctionnement normal** | Quel comportement attend-on dans une situation courante et valide ? |
| **Valeurs aux bornes** | Où le comportement change-t-il, et que se passe-t-il à la limite et de part et d'autre ? |
| **Edge cases** | Quelles situations particulières restent valides selon le contrat ? |
| **Failures / erreurs attendues** | Quelles entrées faut-il refuser, et comment ? |

Ces axes peuvent se recouper. Ce ne sont ni un quota de tests ni une obligation d'écrire quatre tests pour chaque fonction. Le but est de choisir des cas utiles, pas de multiplier les valeurs qui vérifient le même comportement.

Avant d'écrire chaque test, complétez votre tableau de travail :

| Comportement à vérifier | Axe | Entrée choisie | Résultat ou erreur attendu | Justification du choix |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |

Déterminez les résultats attendus à partir du contrat, indépendamment du code actuel. Choisissez une valeur représentative lorsque plusieurs entrées exercent le même comportement. Si vous en retenez plusieurs, expliquez ce que chacune apporte en plus. Décidez de vos priorités et identifiez aussi les risques encore non couverts.

Pour justifier un ajout, demandez-vous : **« Quelle erreur les tests existants pourraient-ils laisser passer ? »**

Lorsqu'un résultat vous semble incorrect, isolez-le avec un test qui échoue et expliquez ce qu'il démontre avant de corriger le code. Ne modifiez pas une règle métier pour faire passer un test. Si le contrat vous paraît ambigu, posez la question à l'enseignant.

`pytest.mark.parametrize` aide à organiser les cas choisis ; il ne remplace pas leur justification. `pytest.raises` permet de vérifier une erreur attendue : le test passe lorsque l'exception prévue est levée.

Lors de la revue, votre présentation doit permettre de comprendre :

- Quels comportements vos tests protègent, et lesquels restent à explorer.
- Pourquoi les résultats attendus sont justes, avec un calcul indépendant du code.
- Pourquoi les entrées choisies sont pertinentes et quels choix seraient redondants, sans supprimer ni affaiblir les tests fournis.
- Quelle modification a été faite et quelle régression un test permet d'éviter.
- Comment un autre développeur peut reproduire vos vérifications.

### Compléter les tests : lint, types et coverage

Après la démonstration collective et votre première recherche de cas, lancez ces contrôles depuis la racine du dépôt :

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/unit --cov=supermarket_receipt_api.checkout --cov-report=term-missing
```

Le **linter** Ruff repère des problèmes de code sans exécuter l'application ; son **formatter** vérifie une mise en forme commune. Ce sont deux contrôles distincts, pas des tests du contrat métier.

`pytest-cov`, déjà installé par `uv sync --locked`, exécute les tests unitaires et mesure la couverture du code métier dans `checkout.py`. Il n'est pas nécessaire de relancer les mêmes tests une seconde fois pour produire le rapport. La colonne `Missing` indique les lignes non exécutées ; le périmètre mesuré n'est pas toute l'API.

Expliquez ce qu'une zone non exécutée vous invite à vérifier. Puis revenez à la démonstration : une ligne exécutée par les tests pouvait-elle produire un résultat faux ? La couverture ne valide ni les assertions ni tous les comportements. **Aucun seuil de couverture n'est imposé, en J1 comme dans la suite du module.**

Le **type checker**, présenté avec mypy en cours, détecte certaines incompatibilités avec les annotations : une chaîne à la place d'un entier, par exemple. Il ne garantit pas qu'une valeur du bon type respecte le métier. `mypy` n'est pas installé dans le starter et son exécution n'est pas demandée en J1.

### Rappel : pre-commit, un retour local avant le commit

Un hook Git `pre-commit` lance un contrôle avant le commit et peut empêcher sa création en cas d'échec. Le framework **pre-commit** permet de partager une configuration de contrôles, par exemple lint et formatage. Même si cette configuration est versionnée, les hooks doivent être installés sur chaque poste après le clone ; ils ne sont pas activés automatiquement.

Ces contrôles rapides complètent la CI, sans la remplacer : un hook local peut manquer ou être contourné. Ils sont distincts des hooks des assistants IA décrits plus bas. Leur usage a été présenté en cours ; aucune installation de hook pre-commit n'est obligatoire dans ce TD.

### Revue en binôme 1 — comparer les tests des autres fonctions

Après votre recherche individuelle, présentez chacun un cas : comportement visé, axe, entrée et résultat attendu à partir du contrat. Comparez les comportements protégés, les choix redondants et les angles morts, pas le nombre de tests. Notez ce que vous souhaitez approfondir sans fusionner vos suites : chacun garde ses choix et complète son propre travail. Conservez les tests fournis. Cette revue termine la partie 1 ; la partie 2 commencera après le cours GitHub Actions.

## Partie 2 — Première CI, après le cours GitHub Actions

Ce dépôt est le **point de départ de la journée 1**. Travaillez dans la copie privée créée au démarrage, et conservez les tests fournis : identifier une redondance ne justifie pas de supprimer ou d'affaiblir une assertion.

La configuration GitHub Actions est à construire pendant la séance. Le premier objectif est de rejouer automatiquement le lint, la vérification du formatage et les tests unitaires avec couverture **à chaque push sur une branche**. Les commandes tournent **directement sur un runner Ubuntu hébergé par GitHub**, dans l'environnement virtuel géré par `uv` : récupération du code, préparation de Python et de `uv`, puis `uv sync --locked` et vérifications. Il n'y a ni build Docker ni conteneur dans cette première CI.

Réutilisez les commandes ci-dessus : le rapport textuel apparaît dans les logs, sans seuil bloquant. Aucun runner local n'est nécessaire aujourd'hui. Montrez une CI rouge à cause d'un véritable échec de test, puis verte après correction, pas simplement une erreur de YAML. Il n'est pas nécessaire de découvrir un nouveau bug métier.

Si tous les tests passent, modifiez temporairement une attente pour la rendre volontairement incorrecte sur une branche dédiée, en annonçant que vous vérifiez le pipeline. Restaurez immédiatement l'attente correcte après avoir constaté le rouge, puis vérifiez le retour au vert. Cette manipulation valide le signal de CI, pas la pertinence des tests ; elle ne constitue pas le bonus de mutation ci-dessous.

### Revue en binôme 2 — expliquer la première CI

Présentez chacun votre workflow : déclencheur, runner, rôle des étapes et installation des dépendances. Retrouvez dans les logs un test en échec, expliquez pourquoi la CI échoue, puis montrez le retour au vert et le rapport de couverture. Relisez le travail de l'autre à l'écran ; chacun conserve sa CI et réalise lui-même ses modifications.

### Bonus facultatif — mettre les tests à l'épreuve

Si le temps le permet, introduisez un comportement incorrect en modifiant uniquement le code métier sur une branche temporaire de votre propre dépôt, sans casser la syntaxe et sans modifier les tests. Vous pouvez échanger une idée avec un voisin, mais chacun fait son expérience.

Lancez les tests : la suite devient-elle rouge ? Expliquez ce qui a été détecté, puis annulez la mutation. Si elle reste verte, analysez le comportement non vérifié ; un nouveau test justifié peut ensuite être ajouté pour détecter cette mutation. Revenez finalement au code correct, sans changer une attente correcte pour l'adapter au défaut. Ce bonus est facultatif, sans score ni production commune.

## Progression après J1

Les tests d'intégration HTTP arrivent en J2. En J3, le pipeline évoluera vers Docker : construction d'une image de test, exécution des tests dans cet environnement et préparation de l'image à déployer. La cible de J4 est un déploiement automatique dans un conteneur local après fusion d'une pull request vers `main`, uniquement si les tests et le build réussissent. Un push direct sur `main` ne doit pas déployer. Seul ce futur job de déploiement utilisera un runner sur votre PC.

## Ce qui n'est pas demandé aujourd'hui

Pas de développement complet d'API, de base de données, de Docker, de Kubernetes ni de tests d'intégration HTTP. Ces derniers seront abordés explicitement en journée 2. Il n'est pas nécessaire de démarrer un serveur pour tester les fonctions métier.

## Assistants IA : autorisés, avec compréhension

Les assistants IA sont autorisés pendant le TD, en **mode tuteur** : questions, indices progressifs et relecture de vos essais, sans solution complète ni modification des fichiers. Vous écrivez le code et lancez les commandes vous-mêmes. Leur utilisation reste facultative.

Avant de demander de l'aide, formulez votre hypothèse ou votre choix de test. Vérifiez ensuite les propositions à partir du contrat et de vos exécutions : une réponse de l'assistant n'est pas une preuve.

Chaque étudiant doit pouvoir **expliquer ses choix et adapter son travail sans assistant**. Pendant les échanges, l'enseignant pourra vous demander de justifier un résultat attendu, d'expliquer un échec ou d'adapter un test à une petite variation annoncée. Ces courts temps sans assistant servent à vérifier la compréhension, pas à ajouter une note au TD. Si une explication vous manque, reprenez le raisonnement avec l'enseignant avant de poursuivre.

Le cadre est défini dans [AGENTS.md](AGENTS.md) et [CLAUDE.md](CLAUDE.md). La configuration des hooks est déjà fournie : aucun fichier à recopier ni skill à installer. Au premier lancement depuis la racine du dépôt, acceptez la confiance du dossier après lecture des fichiers ; avec Codex, approuvez aussi les hooks dans `/hooks`. Une fois ces validations faites, les hooks s'exécutent automatiquement dans un client compatible, tant qu'ils restent actifs. Une définition de hook modifiée demande une nouvelle approbation dans Codex. Consulter [le fonctionnement et la vérification au premier lancement](docs/tutorat.md). Ces garde-fous ne résolvent pas le TD et n'ajoutent pas de tests métier au starter.

## Origine et ressources

Le scénario s'inspire du [Supermarket Receipt Refactoring Kata d'Emily Bache](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata). Notre API et les règles explicites de ce kit constituent une adaptation pédagogique, pas une reproduction exacte du kata.

Pour la progression CI/CD : [UPenn — CI/CD with GitHub Actions](https://www.cis1912.org/labs/11-13-cicd/) et [Helsinki — DevOps with Docker, Deployment pipelines](https://github.com/docker-hy/docker-hy.github.io/blob/master/docs/part-3/section-2.md).
