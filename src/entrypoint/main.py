from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.utils.lifespan_builder import lifespan_builder
from src.api.product import ProductRouter, CategoryRouter
from src.api.inventory import InventoryRouter
from src.api.sales import SalesRouter

app = FastAPI(title="forsit-test-backend", lifespan=lifespan_builder)

app.include_router(ProductRouter)
app.include_router(CategoryRouter)
app.include_router(InventoryRouter)
app.include_router(SalesRouter)


# exception handler
@app.exception_handler(Exception)
async def exception_handler(_, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)},
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
