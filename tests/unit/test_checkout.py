"""Six cas de départ sur deux fonctions : une suite verte n'est pas une preuve exhaustive."""

import pytest

from app.checkout import line_subtotal_cents, percentage_discount_cents


@pytest.mark.parametrize(
    "unit_price_cents, quantity, unit, expected",
    [(100, 2, "piece", 200), (199, 1000, "gram", 199), (199, 2000, "gram", 398)],
)
def test_line_subtotal_nominal(
    unit_price_cents: int, quantity: int, unit: str, expected: int
) -> None:
    """Vérifier trois calculs de brut sans fraction de centime.

    Paramètres : prix et quantité entiers, unité str, expected entier attendu.
    Retour : None ; assertion en cas d'écart. Aucun effet de bord ni application HTTP.
    """
    assert line_subtotal_cents(unit_price_cents, quantity, unit) == expected


@pytest.mark.parametrize(
    "subtotal_cents, discount_percent, expected", [(1000, 20, 200), (1200, 10, 120), (800, 25, 200)]
)
def test_percentage_discount_nominal(
    subtotal_cents: int, discount_percent: int, expected: int
) -> None:
    """Vérifier trois réductions sans fraction de centime.

    Paramètres : sous-total, pourcentage et expected, entiers fournis par pytest.
    Retour : None ; assertion en cas d'écart. Aucun effet de bord ni application HTTP.
    """
    assert percentage_discount_cents(subtotal_cents, discount_percent) == expected
