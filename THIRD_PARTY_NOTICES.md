# Références et attribution

## Supermarket Receipt Refactoring Kata

Le domaine pédagogique et les exemples de promotions sont adaptés du
[Supermarket Receipt Refactoring Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata)
d’Emily Bache, lui-même présenté comme une variation de
[CodeKata — Supermarket Pricing](http://codekata.com/kata/kata01-supermarket-pricing/).
Sources consultées le 8 octobre 2026 : README, `python_pytest/src/shopping_cart.py`,
`python_pytest/src/teller.py` et `license.txt` de la branche `main`.

L’amont est sous licence MIT, copyright (c) 2018 Emily Bache. Son texte est conservé dans
[LICENSES/SupermarketReceipt-MIT.txt](LICENSES/SupermarketReceipt-MIT.txt).

Notre version est une adaptation pédagogique réécrite : fonctions Python courtes, montants en
centimes entiers, quantités en grammes ou pièces, catalogue limité, arrondi explicite, API FastAPI,
gestion uv/pyproject et progression CI/CD. Elle ne reproduit ni l’architecture de classes ni toutes
les promotions de l’amont. Les défauts du starter et ses règles d’arrondi sont propres à notre TD :
ils ne doivent pas être attribués au projet original. Aucun corrigé enseignant n’est publié ici.

## Progression CI/CD

Ces ressources servent de références pédagogiques, pas de workflows copiés à l’identique :

- [UPenn CIS 1912 — CI/CD with GitHub Actions](https://www.cis1912.org/labs/11-13-cicd/) :
  progression FastAPI, pytest, PR et image Docker.
- [University of Helsinki — DevOps with Docker, Deployment pipelines](https://devopswithdocker.com/part-3/section-2/) :
  construction d’image par CI et livraison vers un environnement local.

Notre déploiement Minikube est spécifique au cours. Seul son job de déploiement est self-hosted ;
tests et builds s’exécutent sur des runners GitHub-hosted.
