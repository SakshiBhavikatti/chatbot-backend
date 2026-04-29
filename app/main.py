from fastapi import FastAPI
from app.routers.chat import router as chat_router
from app.routers.faq import router as faq_router
from app.routers.incident import router as incident_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chatbot Backend"
)

app.include_router(chat_router)
app.include_router(faq_router)
app.include_router(incident_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)