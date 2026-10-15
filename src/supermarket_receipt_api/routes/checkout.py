"""Route HTTP de calcul d'un ticket de caisse."""

from fastapi import APIRouter, HTTPException

from supermarket_receipt_api.schemas.checkout import CheckoutRequest, ReceiptResponse
from supermarket_receipt_api.services.checkout import checkout

router = APIRouter()


@router.post("/checkout", response_model=ReceiptResponse)
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
