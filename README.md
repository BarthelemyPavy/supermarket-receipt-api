# Supermarket Receipt API — starter J1

Une petite enseigne veut livrer une nouvelle version de son moteur de caisse. L'API et les calculs existent déjà, accompagnés de 100 cas de test qui passent. À vous de déterminer ce que cette suite permet d'affirmer, de choisir les comportements à sécuriser et de préparer une modification livrable.

## Organisation

Le travail est **individuel** : chacun conserve son dépôt privé, ses tests et sa CI. Deux revues ponctuelles se font en binôme : après les tests du socle de J1, puis après la première CI. Un partage d'écran suffit ; il n'est pas nécessaire de partager un accès en écriture. Chacun effectue ses propres modifications après l'échange.

Le TD comprend **deux parties**, chacune après le cours correspondant : tests unitaires et qualité, puis GitHub Actions. Préparez votre poste avant la séance à l'aide du guide de prérequis. La copie du projet et son premier lancement se font seulement au début de la partie 1, pas à l'ouverture de la journée.

## Partie 1 — Tests unitaires, après le cours tests et qualité

Réutilisez les notions de choix des cas, assertions, lint, formatage, types, coverage et pre-commit.

### Démarrer

Clonez la branche `main` du [dépôt starter Supermarket Receipt API](https://github.com/BarthelemyPavy/supermarket-receipt-api), puis entrez dans le dossier :

```bash
git clone --branch main --single-branch https://github.com/BarthelemyPavy/supermarket-receipt-api.git
cd supermarket-receipt-api
```

Sur GitHub, créez dans **votre compte** un dépôt **privé et vide** nommé `supermarket-receipt-api`, sans ajouter de README, de `.gitignore` ni de licence.

Dans les commandes suivantes, remplacez `VOTRE_COMPTE` par votre identifiant GitHub. Faites pointer `origin` vers ce nouveau dépôt, puis poussez la branche `main` :

```bash
git remote set-url origin https://github.com/VOTRE_COMPTE/supermarket-receipt-api.git
git push -u origin main
```

Votre copie est maintenant sur votre compte GitHub. Partagez son accès avec l’enseignant selon les consignes de séance. Un simple clone sur votre poste ne suffit pas : le push crée la branche dans votre dépôt personnel, où votre CI pourra s’exécuter.

Python 3.13 et `uv` doivent être disponibles. Ouvrez un terminal à la racine de votre copie :

```bash
uv sync --locked
uv run pytest tests/unit -v
```

`pyproject.toml` déclare les dépendances et le package local ; `uv.lock` fixe leur résolution. `uv sync` installe aussi le package depuis `src/` en mode éditable : les modifications du code sont prises en compte sans réinstallation. N'ajoutez pas de `requirements.txt` ni d'installation manuelle avec `pip`.

Repérez [le contrat métier](docs/contrat.md), le catalogue `CATALOG` et les fonctions dans `src/supermarket_receipt_api/checkout.py`, ainsi que `tests/unit/`.

### Première observation : 100 tests verts

Au premier lancement, la suite affiche **100 cas réussis** (`100 passed`). Que permet ce résultat d'affirmer sur le moteur de caisse ? Préparez votre réponse, puis **attendez la démonstration collective avant de modifier le code ou les tests**.

Sur `percentage_discount_cents`, une fonction déjà testée, nous examinerons un cas annoncé en séance :

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

### Fonctions à tester en J1

Les fonctions ciblées se trouvent dans `src/supermarket_receipt_api/checkout.py`. La démonstration collective porte sur `percentage_discount_cents`, qui calcule une remise en pourcentage et possède déjà des tests. Reproduisez le test de régression et la correction expliqués en séance, puis conservez-les dans votre branche.

Pendant les **40 minutes de travail individuel, reproduction comprise**, construisez vos tests sur ce socle, dans cet ordre :

| Ordre | Fonction | Rôle métier |
| --- | --- | --- |
| 1 | `validate_quantity` | Valider la quantité d'un article. |
| 2 | `three_for_two_discount_cents` | Calculer la remise de la promotion « trois pour le prix de deux ». |
| 3 | `line_subtotal_cents` | Calculer le montant d'une ligne avant remise, pour un article à la pièce ou au poids. Complétez les tests déjà présents. |

Pour chaque fonction, choisissez les comportements à vérifier, les entrées, les résultats attendus et les assertions à partir du contrat et des quatre axes ci-dessous. Le moteur contient **deux défauts**. Le premier est trouvé ensemble pendant la démonstration ; le second se trouve dans l'une des trois fonctions ci-dessous. Pour chaque fonction, écrivez **au moins un cas normal et un cas limite**. Conservez les tests fournis ; aucun objectif de couverture n'est fixé.

**Si vous avez terminé le socle et relancé les contrôles**, vous pouvez poursuivre avec `aggregate_items`, qui prépare le panier en regroupant ses lignes. Ce prolongement est facultatif et ne conditionne pas la revue en binôme. Les autres fonctions du module ne font pas partie du travail obligatoire de J1.

### Choisir des tests utiles

Vous êtes responsables de la confiance que l'équipe peut accorder au ticket de caisse. Construisez une stratégie de tests unitaires à partir du contrat, autour de quatre axes :

| Axe | Question à se poser |
| --- | --- |
| **Fonctionnement normal** | Quel comportement attend-on dans une situation courante et valide ? |
| **Valeurs aux bornes** | Où le comportement change-t-il, et que se passe-t-il à la limite et de part et d'autre ? |
| **Edge cases** | Quelles situations particulières restent valides selon le contrat ? |
| **Failures / erreurs attendues** | Quelles entrées faut-il refuser, et comment ? |

Ces axes peuvent se recouper. Vous n'êtes pas obligé d'écrire quatre tests par fonction : le minimum est un cas normal et un cas limite. Ajoutez les autres axes quand ils vérifient un risque distinct, sans multiplier les valeurs qui vérifient le même comportement.

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

### Méthode, pour chaque fonction

1. Lisez la docstring de la fonction et la règle correspondante dans `docs/contrat.md`.
2. Remplissez une ligne du tableau par cas : au moins un cas normal et un cas limite.
3. Écrivez les tests dans `tests/unit/`, puis lancez `uv run pytest tests/unit -q`.
4. Si un test échoue, vérifiez d'abord l'attendu dans le contrat. S'il est juste, corrigez le code, jamais l'attendu.
5. Relancez toute la suite, puis les contrôles de lint, de format et de couverture.

### Compléter les tests : lint, types et coverage

Après la démonstration collective et votre première recherche de cas, lancez ces contrôles depuis la racine du dépôt :

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/unit --cov=supermarket_receipt_api.checkout --cov-report=term-missing
```

Le **linter** Ruff repère des problèmes de code sans exécuter l'application ; son **formatter** vérifie une mise en forme commune. Ce sont deux contrôles distincts, pas des tests du contrat métier.

`pytest-cov`, déjà installé par `uv sync --locked`, exécute les tests unitaires et mesure la couverture du code métier dans `checkout.py`. Il n'est pas nécessaire de relancer les mêmes tests une seconde fois pour produire le rapport. La colonne `Missing` indique les lignes non exécutées ; le périmètre mesuré n'est pas toute l'API.

Dans les fonctions du socle, expliquez ce qu'une zone non exécutée, s'il en reste, vous invite à vérifier. Puis revenez à la démonstration : une ligne exécutée par les tests pouvait-elle produire un résultat faux ? La couverture ne valide ni les assertions ni tous les comportements. **Aucun seuil de couverture n'est imposé, en J1 comme dans la suite du module.**

Le **type checker**, présenté avec mypy en cours, détecte certaines incompatibilités avec les annotations : une chaîne à la place d'un entier, par exemple. Il ne garantit pas qu'une valeur du bon type respecte le métier. `mypy` n'est pas installé dans le starter et son exécution n'est pas demandée en J1.

### Rappel : pre-commit, un retour local avant le commit

Un hook Git `pre-commit` lance un contrôle avant le commit et peut empêcher sa création en cas d'échec. Le framework **pre-commit** permet de partager une configuration de contrôles, par exemple lint et formatage. Même si cette configuration est versionnée, les hooks doivent être installés sur chaque poste après le clone ; ils ne sont pas activés automatiquement.

Ces contrôles rapides complètent la CI, sans la remplacer : un hook local peut manquer ou être contourné. Ils sont distincts des hooks des assistants IA décrits plus bas. Leur usage a été présenté en cours ; aucune installation de hook pre-commit n'est obligatoire dans ce TD.

### Comment savoir que la partie 1 est terminée

- [ ] Chaque fonction du socle a au moins un cas normal et un cas limite, avec un attendu tiré du contrat.
- [ ] Le second défaut est trouvé : un test l'a montré en rouge, et il passe après la correction du code.
- [ ] `uv run ruff check .` et `uv run ruff format --check .` ne signalent rien.
- [ ] Vous savez dire quelles lignes de `checkout.py` restent non exécutées dans le rapport de couverture.
- [ ] Tout est commité sur votre branche de travail.

### Revue en binôme 1 — comparer les tests du socle

Après le travail sur `validate_quantity`, `three_for_two_discount_cents` et `line_subtotal_cents`, présentez chacun un cas, même si certains points restent à approfondir : comportement visé, axe, entrée et résultat attendu à partir du contrat. Comparez les comportements protégés, les choix redondants et les angles morts, pas le nombre de tests. Notez ce que vous souhaitez approfondir sans fusionner vos suites : chacun garde ses choix et complète son propre travail. Conservez les tests fournis. Cette revue termine la partie 1 ; la partie 2 commencera après le cours GitHub Actions.

## Partie 2 — Première CI, après le cours GitHub Actions

Ce dépôt est le **point de départ de la journée 1**. Travaillez dans la copie privée créée au démarrage, et conservez les tests fournis : identifier une redondance ne justifie pas de supprimer ou d'affaiblir une assertion.

Le fichier [`.github/workflows/ci.yml`](.github/workflows/ci.yml) est fourni : à chaque push, un job démarre sur un runner Ubuntu hébergé par GitHub et récupère le code avec `actions/checkout`. **Un run vert à ce stade signifie seulement que le checkout a réussi : aucun test n'a été exécuté.**

Complétez ce workflow pendant la séance pour rejouer automatiquement le lint, la vérification du formatage et les tests unitaires avec couverture **à chaque push sur une branche**. Les commandes tournent **directement sur le runner**, dans l'environnement virtuel géré par `uv` : préparation de Python et de `uv`, puis `uv sync --locked` et vérifications. Il n'y a ni build Docker ni conteneur dans cette première CI.

### Étapes

Partez du `ci.yml` fourni. Après chaque étape : commit, push, puis ouvrez le run dans l'onglet **Actions** avant de continuer.

1. **Python et uv** : ajoutez l'action `astral-sh/setup-uv@v10.2.0` avec `python-version: "3.13"` et `enable-cache: false`.
2. **Dépendances** : ajoutez une step qui installe les dépendances de `uv.lock` sans les modifier. Son log liste les paquets installés.
3. **Lint et format** : ajoutez une step par contrôle, avec les commandes de la partie 1. La vérification du formatage ne doit pas modifier les fichiers.
4. **Tests et couverture** : ajoutez la commande de tests de la partie 1. Le log affiche le nombre de tests passés et le tableau de couverture, sans seuil bloquant.
5. **Un run rouge, puis vert** : sur une branche temporaire, remplacez un résultat attendu par une valeur fausse, puis poussez. Dans le run rouge, retrouvez le job, la step, le nom du test, la valeur obtenue et la valeur attendue. Restaurez l'attendu correct et poussez : le run redevient vert. Une erreur de YAML ne compte pas : il faut un vrai test en échec. Cette manipulation vérifie le signal de la CI, pas la pertinence des tests ; elle est distincte du bonus de mutation.

### Comment savoir que la partie 2 est terminée

- [ ] Le run montre les steps de préparation, de lint, de format et de tests, toutes vertes.
- [ ] Le log de pytest affiche le tableau de couverture de `checkout.py`.
- [ ] Vous avez le lien d'un run rouge dû à un vrai test, et celui du run vert qui suit.
- [ ] Vous savez expliquer l'échec : quelle step, quel test, quelle valeur attendue.

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

<!-- Essai J2 temporaire : PR qui ne modifie que ce fichier. -->
