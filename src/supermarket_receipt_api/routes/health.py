"""Sondes HTTP du processus et de la version déployée."""

import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Indiquer que le processus HTTP répond.

    Paramètres : aucun. Retour : dictionnaire contenant status égal à ok.
    Aucun effet de bord ; cette sonde ne vérifie aucune dépendance externe.
    """
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    """Exposer la version déclarée dans l'environnement du processus.

    Paramètres : aucun. Retour : APP_VERSION sous la clé version, ou dev si absente.
    Lit une variable d'environnement sans modifier le processus ni le système.
    """
    return {"version": os.environ.get("APP_VERSION", "dev")}
