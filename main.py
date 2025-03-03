import uvicorn  # type: ignore

from fastapi import FastAPI, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from starlette.responses import JSONResponse  # type: ignore

from slowapi.errors import RateLimitExceeded  # type: ignore

from src.configuration import messages
from src.api import utils, contacts, auth, users

app = FastAPI()

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

origins = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": messages.RATE_LIMIT_EXCEEDED},
    )


@app.get("/")
async def root():
    return {"message": messages.WELCOME_MESSAGE}


def main():
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, workers=4)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)


if __name__ == "__main__":
    main()
