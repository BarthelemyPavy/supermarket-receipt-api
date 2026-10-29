"""Démarrer l'API en local avec python -m supermarket_receipt_api."""

import uvicorn


def main() -> None:
    """Lancer le serveur HTTP local sur le port 8000.

    Écoute uniquement sur 127.0.0.1 ; bloque le processus jusqu'à son interruption.

    Returns:
        None: Le contrôle revient à l'appelant après l'arrêt du serveur.
    """
    uvicorn.run("supermarket_receipt_api.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
