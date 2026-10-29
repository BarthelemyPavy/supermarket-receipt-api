"""Exposer le catalogue et le calcul des tickets avec FastAPI."""

import os
from dataclasses import asdict

from fastapi import FastAPI, HTTPException

from supermarket_receipt_api.checkout import CATALOG, checkout
from supermarket_receipt_api.schemas import CheckoutRequest, ReceiptResponse

app = FastAPI(
    title="Supermarket Receipt API", description="Fil rouge du module Usine logicielle & CI/CD"
)


@app.get("/health")
def health() -> dict[str, str]:
    """Indiquer que le processus HTTP répond.

    Aucun effet de bord ; cette sonde ne vérifie aucune dépendance externe.

    Returns:
        dict[str, str]: Dictionnaire contenant "status" égal à "ok".
    """
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    """Exposer la version déclarée dans l'environnement du processus.

    Lit une variable d'environnement sans modifier le processus ni le système.

    Returns:
        dict[str, str]: Valeur de APP_VERSION sous la clé "version", ou "dev" si absente.
    """
    return {"version": os.environ.get("APP_VERSION", "dev")}


@app.get("/catalog")
def read_catalog() -> dict[str, list[dict[str, object]]]:
    """Renvoyer les quatre produits et les offres du catalogue pédagogique.

    Aucun effet de bord ; les appels suivants ne dépendent pas des réponses précédentes.

    Returns:
        dict[str, list[dict[str, object]]]: Dictionnaire dont la clé "products" contient
        une liste de copies sérialisables en JSON des produits du catalogue.
    """
    return {"products": [asdict(product) for product in CATALOG.values()]}


@app.post("/checkout", response_model=ReceiptResponse)
def create_receipt(request: CheckoutRequest) -> ReceiptResponse:
    """Calculer un ticket avec le vrai moteur métier pour un panier JSON validé.

    Aucun effet de bord, mock, persistance, paiement ni appel à un service extérieur.

    Args:
        request (CheckoutRequest): Panier validé par FastAPI.

    Returns:
        ReceiptResponse: Ticket calculé et validé pour la réponse JSON.

    Raises:
        HTTPException: Avec le statut 422 pour un produit inconnu ou une autre valeur
            métier invalide.
    """
    try:
        receipt = checkout([item.model_dump() for item in request.items])
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ReceiptResponse.model_validate(receipt)
