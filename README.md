# Supermarket Receipt API — starter J1

Une petite enseigne veut livrer une nouvelle version de son moteur de caisse. L'API et les calculs existent déjà, mais l'équipe ne dispose que de quelques tests d'exemple. Votre mission : déterminer quels comportements méritent d'être sécurisés, apporter des preuves et préparer une modification livrable.

## Démarrer

Python 3.13 et `uv` doivent être disponibles. Ouvrez un terminal dans ce dossier :

```bash
uv sync --locked
uv run pytest tests/unit
```

`pyproject.toml` déclare les dépendances et `uv.lock` fixe leur résolution. N'ajoutez pas de `requirements.txt` ni d'installation manuelle avec `pip`.

Les tests fournis passent : ils montrent comment démarrer, pas que tous les comportements sont corrects. Lisez [le contrat métier](docs/contrat.md), puis explorez le catalogue `CATALOG` et les fonctions dans `app/checkout.py`, ainsi que `tests/unit/`.

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

L'utilisation des assistants IA sera précisée par l'enseignant au début du TD ; aucune autorisation ou interdiction n'est présumée dans ce kit.

## Origine et ressources

Le scénario s'inspire du [Supermarket Receipt Refactoring Kata d'Emily Bache](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata). Notre API et les règles explicites de ce kit constituent une adaptation pédagogique, pas une reproduction exacte du kata.

Pour la progression CI/CD : [UPenn — CI/CD with GitHub Actions](https://www.cis1912.org/labs/11-13-cicd/) et [Helsinki — DevOps with Docker, Deployment pipelines](https://github.com/docker-hy/docker-hy.github.io/blob/master/docs/part-3/section-2.md).
