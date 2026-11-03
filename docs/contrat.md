# Contrat métier — Supermarket Receipt

Ce document est la référence fonctionnelle de l’exercice. La version de fin de J2 corrige les
défauts étudiés en J1 et ajoute des tests unitaires et HTTP. On travaille sur une caisse
simplifiée, pas sur une application de paiement ou une réglementation de facturation.

## Catalogue

| `product_id` | `name` | `unit` | `unit_price_cents` | Promotion |
| --- | --- | --- | --- | --- |
| `toothbrush` | Brosse à dents | `piece` | 99 | 3 pour le prix de 2 |
| `apples` | Pommes | `gram` | 199 **par kilogramme** | 20 % de réduction |
| `rice` | Sac de riz | `piece` | 249 | 10 % de réduction |
| `milk` | Brique de lait | `piece` | 100 | Aucune |

Le catalogue est fixe pour l’exercice. Un client ne peut ni choisir un prix, ni fournir un pourcentage,
ni changer une unité. Les identifiants sont exacts et sensibles à la casse : pas d’alias ou de conversion.
Dans `GET /catalog`, chaque produit expose aussi `promotion` (`none`, `percentage`, `three_for_two`)
et `discount_percent` (0 pour les promotions autres qu’un pourcentage).

## Panier et calcul

1. Un panier est une liste d’objets contenant exactement `product_id` et `quantity`.
2. `quantity` est un entier strictement positif, hors booléen. Pour `piece`, c’est un nombre de pièces ;
   pour `gram`, c’est un nombre de grammes. Les fractions, chaînes numériques, quantités nulles et
   quantités négatives sont refusées. Un panier vide est accepté.
3. On regroupe les entrées du même produit en additionnant leurs quantités **avant tout calcul**.
   L’ordre des lignes du ticket suit la première apparition de chaque produit dans le panier.
   Le panier d’origine n’est jamais modifié.
4. Le brut de ligne vaut prix × quantité pour les pièces, prix au kilogramme × grammes / 1000 pour
   les produits au poids. Il est arrondi au centime le plus proche ; un demi-centime va vers le haut.
5. Une seule promotion s’applique à chaque ligne. « 3 pour 2 » offre une pièce par groupe complet
   de trois, dès le premier groupe ; les pièces restantes sont au prix normal. La promotion en
   pourcentage est calculée sur le **brut de ligne déjà arrondi**, puis la réduction est elle-même
   arrondie au centime, demi vers le haut.
6. Le net de ligne vaut brut moins réduction. Il n’est pas arrondi une nouvelle fois. Le brut,
   la réduction et le net du ticket sont les sommes des montants correspondants des lignes.
7. Les montants sont tous des entiers en centimes, sans flottants. Les fonctions génériques de
   calcul acceptent un prix nul et un pourcentage entier entre 0 et 100 inclus.

Exemple de lecture des unités : `{"product_id": "apples", "quantity": 500}` représente 500 g.
Les frais de livraison, TVA, paiements, stocks, fidélité, persistance et cumul de promotions sont
hors périmètre. Une nouvelle règle éventuelle sera annoncée explicitement en séance.

## Contrat HTTP

`POST /checkout` reçoit un objet JSON avec le seul champ obligatoire `items`.

```json
{"items": [{"product_id": "milk", "quantity": 2}]}
```

En cas de succès, le statut HTTP est `200` et la réponse contient exactement :

```json
{
  "lines": [{
    "product_id": "milk",
    "name": "Brique de lait",
    "quantity": 2,
    "unit": "piece",
    "unit_price_cents": 100,
    "subtotal_cents": 200,
    "discount_cents": 0,
    "total_cents": 200
  }],
  "subtotal_cents": 200,
  "discount_cents": 0,
  "total_cents": 200
}
```

Un panier vide renvoie `lines: []` et trois totaux égaux à zéro. Champs manquants, supplémentaires,
types invalides ou produit inconnu donnent **HTTP 422**, avec un champ `detail` décrivant l’erreur.
Les erreurs de schéma sont une liste d’erreurs FastAPI ; un produit inconnu donne un message métier
dans `detail`. Il n’y a ni remplacement silencieux d’un produit ni conversion de type.

`GET /catalog` renvoie `{"products": [...]}` avec les quatre produits ci-dessus. `GET /health`
renvoie `{"status": "ok"}` ; `GET /version` renvoie `{"version": "dev"}` en local ou la valeur de
`APP_VERSION` embarquée au build. Ces deux sondes ne valident pas l’exactitude d’un ticket.

## Code à examiner

Les dix fonctions de `src/supermarket_receipt_api/checkout.py` sont indépendantes de FastAPI : validation de quantité,
arrondi, recherche produit, agrégation, brut de ligne, réduction 3 pour 2, réduction en pourcentage,
choix de promotion, construction de ligne et construction du ticket. Leurs docstrings précisent
les paramètres, retours et exceptions (`TypeError`, `KeyError`, `ValueError`).

Les 100 cas de `tests/unit/test_checkout.py` sont conservés comme point de départ sur deux
fonctions. `tests/unit/test_j1.py` complète les comportements vérifiés en J1. Les tests
d’intégration de `tests/integration/test_api.py` appellent route, validation, vrai moteur et
sérialisation ensemble, en mémoire et sans serveur réseau ni conteneur.
