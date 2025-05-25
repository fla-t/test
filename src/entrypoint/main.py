from fastapi import FastAPI

from src.utils.lifespan_builder import lifespan_builder

app = FastAPI(title="forsit-test-backend", lifespan=lifespan_builder)
