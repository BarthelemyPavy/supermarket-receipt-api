"""Moteur de caisse pédagogique inspiré du Supermarket Receipt Kata d'Emily Bache.

Les contrats décrivent le comportement attendu, pas une garantie de correction du starter.
Voir docs/contrat.md et THIRD_PARTY_NOTICES.md. Aucun stockage ni appel réseau.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Product:
    """Décrire un produit immuable du catalogue fourni par l'enseignant.

    Paramètres : product_id et name, chaînes ; unit, piece ou gram ; unit_price_cents,
    entier en centimes par pièce ou kilogramme ; promotion, none, percentage ou
    three_for_two ; discount_percent, entier de 0 à 100. Retour : Product immuable.
    Aucun effet de bord. Ces valeurs internes ne sont jamais fournies par le client HTTP.
    """

    product_id: str
    name: str
    unit: str
    unit_price_cents: int
    promotion: str
    discount_percent: int = 0


CATALOG = {
    "toothbrush": Product("toothbrush", "Brosse à dents", "piece", 99, "three_for_two"),
    "apples": Product("apples", "Pommes", "gram", 199, "percentage", 20),
    "rice": Product("rice", "Sac de riz", "piece", 249, "percentage", 10),
    "milk": Product("milk", "Brique de lait", "piece", 100, "none"),
}


def validate_quantity(quantity: int) -> int:
    """Valider une quantité entière strictement positive, sans conversion.

    Paramètre : quantity, entier de pièces ou de grammes, hors booléen.
    Retour : la même quantité. TypeError si type invalide, ValueError si quantity <= 0.
    Aucun effet de bord ; une fraction de gramme ou de pièce n'est pas acceptée.
    """
    if type(quantity) is not int:
        raise TypeError("quantity doit être un entier de pièces ou grammes, hors booléen.")
    if quantity <= 0:
        raise ValueError("quantity doit être strictement supérieur à 0.")
    return quantity


def round_half_up(numerator: int, denominator: int) -> int:
    """Arrondir un rapport positif au plus proche, avec le demi vers le haut.

    Paramètres : numerator, entier >= 0 ; denominator, entier > 0 ; booléens refusés.
    Retour : entier arrondi, sans conversion flottante. TypeError si type invalide,
    ValueError si valeur hors contrat. Aucun effet de bord ni perte de précision.
    """
    if type(numerator) is not int:
        raise TypeError("numerator doit être un entier positif ou nul, hors booléen.")
    if type(denominator) is not int:
        raise TypeError("denominator doit être un entier strictement positif, hors booléen.")
    if numerator < 0:
        raise ValueError("numerator doit être supérieur ou égal à 0.")
    if denominator <= 0:
        raise ValueError("denominator doit être strictement supérieur à 0.")
    return (2 * numerator + denominator) // (2 * denominator)


def get_product(product_id: str) -> Product:
    """Chercher un produit par son identifiant exact, sans alias ni normalisation.

    Paramètre : product_id, chaîne parmi toothbrush, apples, rice ou milk.
    Retour : Product immuable. TypeError si type invalide ; ValueError si inconnu.
    Aucun effet de bord ; le catalogue n'est pas modifié.
    """
    if type(product_id) is not str:
        raise TypeError("product_id doit être une chaîne du catalogue.")
    if product_id not in CATALOG:
        raise ValueError(
            f"product_id inconnu : {product_id!r} ; attendu : toothbrush, apples, rice ou milk."
        )
    return CATALOG[product_id]


def aggregate_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """Valider puis regrouper les doublons en conservant l'ordre de première apparition.

    Paramètre : items, liste d'objets contenant exactement product_id (str du catalogue)
    et quantity (int > 0, hors booléen). Retour : nouvelle liste, une entrée par produit.
    Liste vide acceptée. TypeError si type invalide ; KeyError si champ manquant ;
    ValueError si champ supplémentaire, identifiant inconnu ou quantité invalide.
    Aucun effet de bord : ni la liste ni les dictionnaires d'entrée ne sont modifiés.
    """
    if type(items) is not list:
        raise TypeError("items doit être une liste d'objets product_id et quantity.")
    quantities: dict[str, int] = {}
    for item in items:
        if type(item) is not dict:
            raise TypeError("Chaque élément de items doit être un objet product_id et quantity.")
        for field in ("product_id", "quantity"):
            if field not in item:
                raise KeyError(f"items : champ obligatoire {field!r} manquant.")
        if set(item) != {"product_id", "quantity"}:
            raise ValueError("items : seuls les champs product_id et quantity sont attendus.")
        product = get_product(item["product_id"])
        quantity = validate_quantity(item["quantity"])
        quantities[product.product_id] = quantities.get(product.product_id, 0) + quantity
    return [
        {"product_id": product_id, "quantity": quantity}
        for product_id, quantity in quantities.items()
    ]


def line_subtotal_cents(unit_price_cents: int, quantity: int, unit: str) -> int:
    """Calculer le brut d'une ligne avant réduction, en centimes entiers.

    Paramètres : unit_price_cents, entier >= 0 ; quantity, entier > 0 ; unit, piece
    ou gram. Pour gram, le prix est par kilogramme et quantity est en grammes.
    Retour : brut arrondi au centime, demi vers le haut, après agrégation des quantités.
    TypeError si type invalide (dont booléen) ; ValueError si valeur hors contrat.
    Aucun effet de bord ; les autres unités sont refusées.
    """
    if type(unit_price_cents) is not int:
        raise TypeError("unit_price_cents doit être un entier en centimes, hors booléen.")
    if unit_price_cents < 0:
        raise ValueError("unit_price_cents doit être supérieur ou égal à 0.")
    validate_quantity(quantity)
    if type(unit) is not str:
        raise TypeError("unit doit être une chaîne : piece ou gram.")
    if unit not in {"piece", "gram"}:
        raise ValueError("unit doit être piece ou gram ; le prix au poids est par kilogramme.")
    denominator = 1000 if unit == "gram" else 1
    return round_half_up(unit_price_cents * quantity, denominator)


def three_for_two_discount_cents(unit_price_cents: int, quantity: int) -> int:
    """Calculer la réduction pour une pièce offerte par groupe complet de trois.

    Paramètres : unit_price_cents, entier >= 0 ; quantity, entier de pièces > 0.
    Retour : réduction en centimes ; les pièces restantes sont payées au prix normal.
    TypeError pour un type invalide, dont booléen ; ValueError pour une valeur négative
    ou une quantité nulle. Aucun effet de bord ; la promotion démarre dès trois pièces.
    """
    line_subtotal_cents(unit_price_cents, quantity, "piece")
    if quantity > 3:
        return (quantity // 3) * unit_price_cents
    return 0


def percentage_discount_cents(subtotal_cents: int, discount_percent: int) -> int:
    """Calculer la réduction, et non le montant net, pour un pourcentage entier.

    Paramètres : subtotal_cents, entier >= 0 ; discount_percent, entier de 0 à 100.
    Retour : réduction en centimes arrondie au plus proche, demi vers le haut.
    TypeError pour un type invalide, dont booléen ; ValueError si hors contrat.
    Aucun effet de bord. La réduction porte sur le brut de ligne déjà arrondi.
    """
    if type(subtotal_cents) is not int:
        raise TypeError("subtotal_cents doit être un entier en centimes, hors booléen.")
    if type(discount_percent) is not int:
        raise TypeError("discount_percent doit être un entier, hors booléen.")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents doit être supérieur ou égal à 0.")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent doit être compris entre 0 et 100 inclus.")
    return round(Fraction(subtotal_cents * discount_percent, 100))


def line_discount_cents(product_id: str, quantity: int) -> int:
    """Choisir la seule promotion configurée pour un produit du catalogue.

    Paramètres : product_id, identifiant exact (str) ; quantity, entier > 0 en pièces
    ou grammes selon le produit. Retour : réduction entière en centimes, zéro sans promo.
    TypeError/ValueError selon les contrats de get_product et line_subtotal_cents.
    Aucun effet de bord ; les promotions ne se cumulent pas.
    """
    product = get_product(product_id)
    subtotal = line_subtotal_cents(product.unit_price_cents, quantity, product.unit)
    if product.promotion == "three_for_two":
        return three_for_two_discount_cents(product.unit_price_cents, quantity)
    if product.promotion == "percentage":
        return percentage_discount_cents(subtotal, product.discount_percent)
    if product.promotion == "none":
        return 0
    raise ValueError("promotion doit être none, percentage ou three_for_two.")


def build_receipt_line(product_id: str, quantity: int) -> dict[str, object]:
    """Construire une ligne de ticket pour une quantité déjà agrégée.

    Paramètres : product_id, identifiant exact (str) ; quantity, entier > 0 selon l'unité.
    Retour : dictionnaire d'identité, quantité, unité, prix et montants brut/réduction/net.
    TypeError/ValueError si entrée invalide. Aucun effet de bord ; total = brut - réduction,
    sans nouvel arrondi. Le prix est par pièce ou par kilogramme, jamais par gramme.
    """
    product = get_product(product_id)
    subtotal = line_subtotal_cents(product.unit_price_cents, quantity, product.unit)
    discount = line_discount_cents(product_id, quantity)
    return {
        "product_id": product.product_id,
        "name": product.name,
        "quantity": quantity,
        "unit": product.unit,
        "unit_price_cents": product.unit_price_cents,
        "subtotal_cents": subtotal,
        "discount_cents": discount,
        "total_cents": subtotal - discount,
    }


def checkout(items: list[dict[str, object]]) -> dict[str, object]:
    """Produire le ticket complet, après validation et agrégation du panier.

    Paramètre : items, liste exacte d'objets product_id/quantity décrite par aggregate_items.
    Retour : dictionnaire lines, subtotal_cents, discount_cents et total_cents ; panier vide
    accepté, avec liste vide et trois zéros. TypeError/KeyError/ValueError si entrée invalide.
    Aucun effet de bord ; totaux obtenus par somme des lignes, sans arrondi supplémentaire.
    """
    lines = [
        build_receipt_line(item["product_id"], item["quantity"]) for item in aggregate_items(items)
    ]
    return {
        "lines": lines,
        "subtotal_cents": sum(line["subtotal_cents"] for line in lines),
        "discount_cents": sum(line["discount_cents"] for line in lines),
        "total_cents": sum(line["total_cents"] for line in lines),
    }
