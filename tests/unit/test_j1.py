"""Corrigé du socle J1 : cas choisis à partir du contrat métier.

Ces tests complètent les 100 cas fournis sans les remplacer. Ils appellent les
fonctions directement, sans serveur, réseau ni modification de fichiers.
"""

import pytest

from supermarket_receipt_api.checkout import (
    line_subtotal_cents,
    percentage_discount_cents,
    three_for_two_discount_cents,
    validate_quantity,
)


def test_percentage_discount_rounds_half_a_cent_up() -> None:
    """Reproduire le cas de démonstration : 10 % de 105 centimes vaut 11 centimes.

    Aucun paramètre ni effet de bord. Le contrat impose d'arrondir 10,5 vers 11,
    alors que les cas de départ ne produisent que des réductions entières.

    Returns:
        None: Le test réussit si le demi-centime est arrondi vers le haut.
    """
    assert percentage_discount_cents(105, 10) == 11


@pytest.mark.parametrize("quantity", [pytest.param(7, id="normal"), pytest.param(1, id="minimum")])
def test_validate_quantity_preserves_valid_integer(quantity: int) -> None:
    """Accepter une quantité normale et la plus petite quantité autorisée.

    Aucun effet de bord ni conversion de la quantité.

    Args:
        quantity (int): Quantité strictement positive fournie par pytest.

    Returns:
        None: Le test réussit si la valeur est conservée sous forme d'entier.
    """
    result = validate_quantity(quantity)

    assert result == quantity
    assert type(result) is int


@pytest.mark.parametrize("quantity", [pytest.param(0, id="zero"), pytest.param(-1, id="negative")])
def test_validate_quantity_rejects_non_positive_integer(quantity: int) -> None:
    """Refuser la borne exclue zéro et une quantité négative.

    Aucun effet de bord ; ces erreurs attendues font réussir le test.

    Args:
        quantity (int): Quantité hors du domaine strictement positif.

    Returns:
        None: Le test réussit si une ValueError identifie quantity.
    """
    with pytest.raises(ValueError, match="quantity"):
        validate_quantity(quantity)


@pytest.mark.parametrize(
    "quantity",
    [
        pytest.param("2", id="numeric-string"),
        pytest.param(2.5, id="fraction"),
        pytest.param(True, id="boolean-is-not-a-quantity"),
        pytest.param(None, id="missing-value"),
    ],
)
def test_validate_quantity_rejects_other_types(quantity: object) -> None:
    """Refuser les conversions implicites et le cas particulier du booléen.

    Aucun effet de bord. Python traite bool comme un sous-type de int, mais le
    contrat exclut explicitement les booléens.

    Args:
        quantity (object): Valeur qui n'est pas une quantité entière autorisée.

    Returns:
        None: Le test réussit si une TypeError identifie quantity.
    """
    with pytest.raises(TypeError, match="quantity"):
        validate_quantity(quantity)


@pytest.mark.parametrize(
    "quantity, expected_discount",
    [
        pytest.param(2, 0, id="before-first-group"),
        pytest.param(3, 99, id="first-complete-group"),
        pytest.param(4, 99, id="remainder-is-paid"),
        pytest.param(6, 198, id="two-complete-groups"),
    ],
)
def test_three_for_two_counts_complete_groups(quantity: int, expected_discount: int) -> None:
    """Vérifier le seuil de la promotion, les restes et plusieurs groupes.

    Aucun effet de bord. Une pièce à 99 centimes est offerte par groupe complet
    de trois ; une pièce restante ne crée pas de remise supplémentaire.

    Args:
        quantity (int): Nombre de pièces choisi autour des seuils utiles.
        expected_discount (int): Remise attendue en centimes selon le contrat.

    Returns:
        None: Le test réussit si la réduction correspond aux groupes complets.
    """
    assert three_for_two_discount_cents(99, quantity) == expected_discount


def test_three_for_two_accepts_a_free_product() -> None:
    """Accepter le prix nul, autorisé par le contrat des fonctions génériques.

    Aucun paramètre ni effet de bord. Une pièce offerte à prix nul ne change
    pas le montant de la remise.

    Returns:
        None: Le test réussit si la réduction reste nulle.
    """
    assert three_for_two_discount_cents(0, 3) == 0


@pytest.mark.parametrize(
    "unit_price_cents, quantity, expected_error, field",
    [
        pytest.param(-1, 3, ValueError, "unit_price_cents", id="negative-price"),
        pytest.param(99, 0, ValueError, "quantity", id="zero-quantity"),
        pytest.param(True, 3, TypeError, "unit_price_cents", id="boolean-price"),
        pytest.param(99, True, TypeError, "quantity", id="boolean-quantity"),
    ],
)
def test_three_for_two_rejects_invalid_inputs(
    unit_price_cents: object,
    quantity: object,
    expected_error: type[Exception],
    field: str,
) -> None:
    """Vérifier que la fonction de remise applique aussi ses préconditions.

    Aucun effet de bord ; chaque cas invalide une précondition différente.

    Args:
        unit_price_cents (object): Prix valide ou valeur volontairement invalide.
        quantity (object): Quantité valide ou valeur volontairement invalide.
        expected_error (type[Exception]): Exception définie par le contrat.
        field (str): Nom du paramètre à retrouver dans le message.

    Returns:
        None: Le test réussit si l'erreur attendue identifie le paramètre.
    """
    with pytest.raises(expected_error, match=field):
        three_for_two_discount_cents(unit_price_cents, quantity)


@pytest.mark.parametrize(
    "quantity, expected_subtotal",
    [
        pytest.param(499, 0, id="below-half-a-cent"),
        pytest.param(500, 1, id="exactly-half-a-cent"),
        pytest.param(501, 1, id="above-half-a-cent"),
    ],
)
def test_weighted_subtotal_rounds_around_half_a_cent(quantity: int, expected_subtotal: int) -> None:
    """Tester les trois positions autour du seuil d'arrondi au demi-centime.

    Aucun effet de bord. Avec un prix de 1 centime par kilogramme, les trois
    quantités donnent 0,499, 0,500 et 0,501 centime avant arrondi.

    Args:
        quantity (int): Poids en grammes choisi autour de 500 g.
        expected_subtotal (int): Sous-total arrondi attendu en centimes.

    Returns:
        None: Le test réussit si le seuil et l'unité au kilogramme sont respectés.
    """
    assert line_subtotal_cents(1, quantity, "gram") == expected_subtotal


def test_line_subtotal_accepts_a_zero_price() -> None:
    """Vérifier la borne autorisée du prix, indépendamment de la quantité.

    Aucun paramètre ni effet de bord. Les cas nominaux à la pièce et au poids
    restent couverts par la suite initiale, que ce test complète.

    Returns:
        None: Le test réussit si deux pièces gratuites ont un sous-total nul.
    """
    assert line_subtotal_cents(0, 2, "piece") == 0


@pytest.mark.parametrize(
    "unit_price_cents, quantity, unit, expected_error, field",
    [
        pytest.param(-1, 1, "piece", ValueError, "unit_price_cents", id="negative-price"),
        pytest.param(1.5, 1, "piece", TypeError, "unit_price_cents", id="fractional-price"),
        pytest.param(100, 0, "piece", ValueError, "quantity", id="zero-quantity"),
        pytest.param(100, True, "piece", TypeError, "quantity", id="boolean-quantity"),
        pytest.param(100, 1, "kg", ValueError, "unit", id="unknown-unit"),
        pytest.param(100, 1, None, TypeError, "unit", id="unit-must-be-a-string"),
    ],
)
def test_line_subtotal_rejects_inputs_outside_its_contract(
    unit_price_cents: object,
    quantity: object,
    unit: object,
    expected_error: type[Exception],
    field: str,
) -> None:
    """Vérifier les erreurs attendues pour le prix, la quantité et l'unité.

    Aucun effet de bord. Un seul paramètre est invalide par cas, pour rendre
    l'origine du refus explicite.

    Args:
        unit_price_cents (object): Prix valide ou volontairement hors contrat.
        quantity (object): Quantité valide ou volontairement hors contrat.
        unit (object): Unité valide, inconnue ou d'un type incorrect.
        expected_error (type[Exception]): Exception attendue pour ce cas.
        field (str): Nom du paramètre attendu dans le message d'erreur.

    Returns:
        None: Le test réussit si la fonction refuse l'entrée comme prévu.
    """
    with pytest.raises(expected_error, match=field):
        line_subtotal_cents(unit_price_cents, quantity, unit)
