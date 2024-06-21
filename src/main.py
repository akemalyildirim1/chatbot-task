"""Main project file."""

from fastapi import FastAPI
from fastapi.middleware import Middleware

from src.api import dropbox_login_router, dropbox_resource_router, user_router
from src.middleware import GenericErrorHandlerMiddleware

app: FastAPI = FastAPI(
    title="Teams Chatbot API",
    description="Teams chatbot API.",
    version="0.1.0",
    middleware=[Middleware(GenericErrorHandlerMiddleware)],
)

app.include_router(dropbox_login_router)
app.include_router(dropbox_resource_router)
app.include_router(user_router)
