"""Vérifier ensemble les routes, la validation, le vrai moteur et le JSON en J2.

TestClient appelle l'application en mémoire, sans serveur réseau ni conteneur.
Les montants attendus viennent du contrat du starter, avec les pommes à 20 %.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from supermarket_receipt_api.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Ouvrir un client de test sur l'application réelle, puis le fermer.

    Aucun paramètre ni appel réseau externe. Le contexte gère le cycle de vie de
    l'application pour le test ; aucun catalogue ni comportement métier n'est remplacé.

    Yields:
        TestClient: Client en mémoire relié à l'application FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client


def test_checkout_returns_the_documented_receipt(client: TestClient) -> None:
    """Vérifier le cas nominal et la forme complète du ticket JSON.

    Args:
        client (TestClient): Client en mémoire fourni par la fixture.

    Returns:
        None: Les assertions comparent la réponse au contrat, sans persistance.
    """
    response = client.post("/checkout", json={"items": [{"product_id": "milk", "quantity": 2}]})

    assert response.status_code == 200
    assert response.json() == {
        "lines": [
            {
                "product_id": "milk",
                "name": "Brique de lait",
                "quantity": 2,
                "unit": "piece",
                "unit_price_cents": 100,
                "subtotal_cents": 200,
                "discount_cents": 0,
                "total_cents": 200,
            }
        ],
        "subtotal_cents": 200,
        "discount_cents": 0,
        "total_cents": 200,
    }


def test_checkout_aggregates_before_the_promotion_and_keeps_order(client: TestClient) -> None:
    """Vérifier que deux lignes de brosses donnent une seule promotion sur trois pièces.

    Args:
        client (TestClient): Client utilisant la validation et le vrai moteur.

    Returns:
        None: Les assertions vérifient l'agrégation, l'ordre et les montants.
        Le panier ne crée aucun état persistant dans l'application.
    """
    response = client.post(
        "/checkout",
        json={
            "items": [
                {"product_id": "toothbrush", "quantity": 2},
                {"product_id": "milk", "quantity": 1},
                {"product_id": "toothbrush", "quantity": 1},
            ]
        },
    )

    assert response.status_code == 200
    receipt = response.json()
    assert [line["product_id"] for line in receipt["lines"]] == ["toothbrush", "milk"]
    assert receipt["lines"][0] == {
        "product_id": "toothbrush",
        "name": "Brosse à dents",
        "quantity": 3,
        "unit": "piece",
        "unit_price_cents": 99,
        "subtotal_cents": 297,
        "discount_cents": 99,
        "total_cents": 198,
    }
    assert receipt["subtotal_cents"] == 397
    assert receipt["discount_cents"] == 99
    assert receipt["total_cents"] == 298


def test_checkout_returns_a_rounded_weighted_line_with_its_discount(client: TestClient) -> None:
    """Vérifier les unités et l'arrondi du demi-centime sur 500 grammes de pommes.

    Args:
        client (TestClient): Client en mémoire de l'application réelle.

    Returns:
        None: Le test vérifie 99,5 centimes arrondis à 100, puis 20 % de remise.
        La requête ne modifie pas le catalogue.
    """
    response = client.post("/checkout", json={"items": [{"product_id": "apples", "quantity": 500}]})

    assert response.status_code == 200
    assert response.json() == {
        "lines": [
            {
                "product_id": "apples",
                "name": "Pommes",
                "quantity": 500,
                "unit": "gram",
                "unit_price_cents": 199,
                "subtotal_cents": 100,
                "discount_cents": 20,
                "total_cents": 80,
            }
        ],
        "subtotal_cents": 100,
        "discount_cents": 20,
        "total_cents": 80,
    }


def test_checkout_accepts_an_empty_basket(client: TestClient) -> None:
    """Vérifier le panier vide, accepté par le contrat HTTP.

    Args:
        client (TestClient): Client en mémoire fourni par la fixture.

    Returns:
        None: Les assertions vérifient un ticket vide et trois totaux nuls.
        Aucun état n'est créé dans l'application.
    """
    response = client.post("/checkout", json={"items": []})

    assert response.status_code == 200
    assert response.json() == {
        "lines": [],
        "subtotal_cents": 0,
        "discount_cents": 0,
        "total_cents": 0,
    }


@pytest.mark.parametrize(
    "payload, expected_location",
    [
        pytest.param({}, ["body", "items"], id="missing-items"),
        pytest.param({"items": {}}, ["body", "items"], id="items-must-be-a-list"),
        pytest.param(
            {"items": [], "discount_percent": 100},
            ["body", "discount_percent"],
            id="unexpected-root-field",
        ),
        pytest.param(
            {"items": [{"quantity": 1}]},
            ["body", "items", 0, "product_id"],
            id="missing-product-id",
        ),
        pytest.param(
            {"items": [{"product_id": "milk"}]},
            ["body", "items", 0, "quantity"],
            id="missing-quantity",
        ),
        pytest.param(
            {"items": [{"product_id": 12, "quantity": 1}]},
            ["body", "items", 0, "product_id"],
            id="product-id-must-be-a-string",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": 1, "unit_price_cents": 1}]},
            ["body", "items", 0, "unit_price_cents"],
            id="client-cannot-set-a-price",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": 0}]},
            ["body", "items", 0, "quantity"],
            id="zero-quantity",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": -1}]},
            ["body", "items", 0, "quantity"],
            id="negative-quantity",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": True}]},
            ["body", "items", 0, "quantity"],
            id="boolean-is-not-a-quantity",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": "2"}]},
            ["body", "items", 0, "quantity"],
            id="numeric-string-is-not-converted",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": 1.5}]},
            ["body", "items", 0, "quantity"],
            id="fractional-quantity",
        ),
        pytest.param(
            {"items": [{"product_id": "milk", "quantity": None}]},
            ["body", "items", 0, "quantity"],
            id="null-quantity",
        ),
    ],
)
def test_checkout_rejects_invalid_requests(
    client: TestClient, payload: dict[str, object], expected_location: list[str | int]
) -> None:
    """Vérifier le refus HTTP et le champ signalé, sans figer le texte de FastAPI.

    Args:
        client (TestClient): Client de l'application réelle.
        payload (dict[str, object]): Corps JSON contenant une violation du contrat.
        expected_location (list[str | int]): Chemin du champ refusé dans le corps JSON.

    Returns:
        None: Le test attend HTTP 422 et une erreur située au bon endroit.
        La requête ne modifie ni le catalogue ni un état persistant.
    """
    response = client.post("/checkout", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert isinstance(errors, list)
    assert any(error["loc"] == expected_location for error in errors)


def test_checkout_rejects_an_unknown_product_without_normalizing_it(client: TestClient) -> None:
    """Vérifier que le moteur refuse un identifiant inconnu et que la route traduit l'erreur.

    Args:
        client (TestClient): Client faisant appel au moteur réel, sans mock.

    Returns:
        None: Les assertions vérifient HTTP 422 et un message métier dans detail.
        Le produit "Milk" ne remplace pas silencieusement le produit "milk".
    """
    response = client.post("/checkout", json={"items": [{"product_id": "Milk", "quantity": 1}]})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "product_id" in detail
    assert "Milk" in detail


def test_catalog_exposes_the_four_products_and_their_offers(client: TestClient) -> None:
    """Vérifier le catalogue HTTP à partir du contrat, indépendamment de sa constante Python.

    Args:
        client (TestClient): Client en mémoire fourni par la fixture.

    Returns:
        None: Les assertions vérifient les quatre produits, leurs prix et promotions.
        L'ordre du catalogue n'est pas imposé et aucun produit n'est modifié.
    """
    response = client.get("/catalog")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"products"}
    assert len(payload["products"]) == 4
    products = {product["product_id"]: product for product in payload["products"]}
    assert products == {
        "toothbrush": {
            "product_id": "toothbrush",
            "name": "Brosse à dents",
            "unit": "piece",
            "unit_price_cents": 99,
            "promotion": "three_for_two",
            "discount_percent": 0,
        },
        "apples": {
            "product_id": "apples",
            "name": "Pommes",
            "unit": "gram",
            "unit_price_cents": 199,
            "promotion": "percentage",
            "discount_percent": 20,
        },
        "rice": {
            "product_id": "rice",
            "name": "Sac de riz",
            "unit": "piece",
            "unit_price_cents": 249,
            "promotion": "percentage",
            "discount_percent": 10,
        },
        "milk": {
            "product_id": "milk",
            "name": "Brique de lait",
            "unit": "piece",
            "unit_price_cents": 100,
            "promotion": "none",
            "discount_percent": 0,
        },
    }
