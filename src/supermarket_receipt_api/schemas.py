"""Contrats JSON du panier et du ticket, indépendants des adaptateurs HTTP."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class CartItem(BaseModel):
    """Valider une entrée JSON du panier sans coercition ni champ supplémentaire.

    Aucun effet de bord ; l'unité vient uniquement du catalogue.
    La présence de product_id dans le catalogue est vérifiée par le moteur métier.

    Attributes:
        product_id (str): Identifiant du produit à rechercher dans le catalogue.
        quantity (int): Quantité strictement positive, hors booléen.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    product_id: str
    quantity: Annotated[int, Field(gt=0)]


class CheckoutRequest(BaseModel):
    """Valider le corps obligatoire de POST /checkout.

    Aucun effet de bord ; les champs inconnus et les types invalides sont refusés.

    Attributes:
        items (list[CartItem]): Liste des lignes du panier, éventuellement vide.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    items: list[CartItem]


class ReceiptLine(BaseModel):
    """Décrire une ligne de ticket agrégée, avec ses montants en centimes.

    Modèle sérialisable en JSON, sans effet de bord. Le prix unitaire est par pièce ou
    kilogramme selon l'unité.

    Attributes:
        product_id (str): Identifiant du produit.
        name (str): Nom du produit.
        quantity (int): Quantité agrégée de pièces ou de grammes.
        unit (Literal["piece", "gram"]): Unité de vente.
        unit_price_cents (int): Prix en centimes par pièce ou kilogramme.
        subtotal_cents (int): Montant brut de la ligne en centimes.
        discount_cents (int): Réduction de la ligne en centimes.
        total_cents (int): Montant net de la ligne en centimes.
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

    Modèle sérialisable en JSON, sans effet de bord ni stockage.

    Attributes:
        lines (list[ReceiptLine]): Lignes agrégées du ticket.
        subtotal_cents (int): Somme des montants bruts en centimes.
        discount_cents (int): Somme des réductions en centimes.
        total_cents (int): Somme des montants nets en centimes.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    lines: list[ReceiptLine]
    subtotal_cents: int
    discount_cents: int
    total_cents: int
