"""Route de consultation du catalogue pédagogique."""

from dataclasses import asdict

from fastapi import APIRouter

from supermarket_receipt_api.services.checkout import CATALOG

router = APIRouter()


@router.get("/catalog")
def read_catalog() -> dict[str, list[dict[str, object]]]:
    """Renvoyer les quatre produits et les offres du catalogue pédagogique.

    Paramètres : aucun. Retour : products, liste de copies JSON des Product internes.
    Aucun effet de bord ; les appels suivants ne dépendent pas des réponses précédentes.
    """
    return {"products": [asdict(product) for product in CATALOG.values()]}
