"""Démarrer l'API en local avec python -m supermarket_receipt_api."""

import uvicorn


def main() -> None:
    """Lancer le serveur HTTP local sur le port 8000.

    Paramètres : aucun. Retour : None après l'arrêt du serveur.
    Écoute uniquement sur 127.0.0.1 ; bloque le processus jusqu'à son interruption.
    """
    uvicorn.run("supermarket_receipt_api:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
