from fastapi import FastAPI
from .routers import authentication, incidents, votes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://aura-azure.vercel.app/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(authentication.router)

app.include_router(incidents.router)

app.include_router(votes.router)