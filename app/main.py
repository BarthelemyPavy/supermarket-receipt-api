"""Interface HTTP du moteur de caisse, sans base de données ni authentification."""

import os
from dataclasses import asdict
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.checkout import CATALOG, checkout


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


app = FastAPI(
    title="Supermarket Receipt API", description="Fil rouge du module Usine logicielle & CI/CD"
)


@app.get("/health")
def health() -> dict[str, str]:
    """Indiquer que le processus HTTP répond.

    Paramètres : aucun. Retour : dictionnaire contenant status égal à ok.
    Aucun effet de bord ; cette sonde ne vérifie aucune dépendance externe.
    """
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    """Exposer la version déclarée dans l'environnement du processus.

    Paramètres : aucun. Retour : APP_VERSION sous la clé version, ou dev si absente.
    Lit une variable d'environnement sans modifier le processus ni le système.
    """
    return {"version": os.environ.get("APP_VERSION", "dev")}


@app.get("/catalog")
def read_catalog() -> dict[str, list[dict[str, object]]]:
    """Renvoyer les quatre produits et les offres du catalogue pédagogique.

    Paramètres : aucun. Retour : products, liste de copies JSON des Product internes.
    Aucun effet de bord ; les appels suivants ne dépendent pas des réponses précédentes.
    """
    return {"products": [asdict(product) for product in CATALOG.values()]}


@app.post("/checkout", response_model=ReceiptResponse)
def create_receipt(request: CheckoutRequest) -> ReceiptResponse:
    """Calculer un ticket avec le vrai moteur métier pour un panier JSON validé.

    Paramètre : request, CheckoutRequest validé par FastAPI. Retour : ReceiptResponse.
    HTTP 422 pour un produit inconnu ou une autre valeur métier invalide.
    Aucun effet de bord, mock, persistance, paiement ni appel à un service extérieur.
    """
    try:
        receipt = checkout([item.model_dump() for item in request.items])
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ReceiptResponse.model_validate(receipt)
