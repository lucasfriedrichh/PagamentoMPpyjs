from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import payments

app = FastAPI(
    title="API do Projeto App Quimica",
    description="API para integração com Mercado Pago Checkout Pro",
    version="1.0.0"
)

# Configuração do CORS para permitir requisições do front-end (ex.: http://localhost:3000)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments.router, prefix="/payments", tags=["Payments"])

@app.get("/")
async def read_root():
    return {"message": "API do Projeto App Quimica está ativa"}
