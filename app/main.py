from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Chatbot AI Service")
app.include_router(router)