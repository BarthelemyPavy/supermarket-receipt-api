"""Contrats JSON du panier et du ticket, indépendants des adaptateurs HTTP."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class CartItem(BaseModel):
    """Valider une entrée JSON du panier sans coercition ni champ supplémentaire.

    Paramètres : product_id, chaîne ; quantity, entier > 0 hors booléen.
    Retour : modèle validé. Aucun effet de bord ; l'unité vient uniquement du catalogue.
    La présence de product_id dans le catalogue est vérifiée par le moteur métier.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    product_id: str
    quantity: Annotated[int, Field(gt=0)]


class CheckoutRequest(BaseModel):
    """Valider le corps obligatoire de POST /checkout.

    Paramètre : items, liste de CartItem, éventuellement vide. Retour : modèle validé.
    Aucun effet de bord ; les champs inconnus et les types invalides sont refusés.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    items: list[CartItem]


class ReceiptLine(BaseModel):
    """Décrire une ligne de ticket agrégée, avec ses montants en centimes.

    Paramètres : product_id/name, chaînes ; unit, piece ou gram ; quantity et prix/montants,
    entiers. Retour : modèle de ligne sérialisable en JSON. Aucun effet de bord.
    unit_price_cents est un prix par pièce ou kilogramme selon l'unité.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    product_id: str
    name: str
    quantity: int
    unit: Literal["piece", "gram"]
    unit_price_cents: int
    subtotal_cents: int
    discount_cents: int
    total_cents: int


class ReceiptResponse(BaseModel):
    """Décrire le ticket complet et la somme de ses montants.

    Paramètres : lines, liste de ReceiptLine ; subtotal_cents, discount_cents et total_cents,
    entiers en centimes. Retour : modèle JSON du ticket. Aucun effet de bord ni stockage.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    lines: list[ReceiptLine]
    subtotal_cents: int
    discount_cents: int
    total_cents: int
