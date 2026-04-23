from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studyagent.api.routes.chat import router as chat_router
from studyagent.core.config import load_config
from studyagent.db.init import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    await init_db(config.database.url)
    yield


def create_app() -> FastAPI:
    config = load_config()
    app = FastAPI(
        title="StudyAgent",
        version="0.1.0",
        description="AI-powered CS learning agent",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    return app


app = create_app()


def main():
    config = load_config()
    uvicorn.run(
        "studyagent.api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug,
    )


if __name__ == "__main__":
    main()
