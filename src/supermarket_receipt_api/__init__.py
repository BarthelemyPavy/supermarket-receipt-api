"""Assembler l'API de caisse et enregistrer ses routes HTTP."""

from fastapi import FastAPI

from supermarket_receipt_api.routes import catalog, checkout, health

app = FastAPI(
    title="Supermarket Receipt API", description="Fil rouge du module Usine logicielle & CI/CD"
)
app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(checkout.router)
