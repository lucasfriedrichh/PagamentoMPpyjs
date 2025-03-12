import os
import requests
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

router = APIRouter()

ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
MP_API_BASE_URL = os.getenv("MP_API_BASE_URL", "https://api.mercadopago.com")

@router.post("/create/{amount}/{description}/{user_id}")
async def create_payment(amount: float, description: str, user_id: int):
    """
    Cria uma preferência de pagamento para o Checkout Pro do Mercado Pago.
    Retorna os URLs de redirecionamento (sandbox_init_point para testes ou init_point para produção).
    """
    print('Deu certo')
    url = f"{MP_API_BASE_URL}/checkout/preferences"
    payload = {
        "items": [{
            "title": description,
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": amount
        }],
        "payer": {
            "id": str(user_id)
        },
        "back_urls": {
            "success": "http://localhost:3000/success",
            "failure": "http://localhost:3000/failure",
            "pending": "http://localhost:3000/pending"
        },
        "notification_url": "https://webhook.site/6de197d3-3022-41d6-a002-fd97d47b5309"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in (200, 201):
        data = response.json()
        return {
            "init_point": data.get("init_point"),
            "sandbox_init_point": data.get("sandbox_init_point"),
            "preference_id": data.get("id")
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Erro ao criar preferência de pagamento")

@router.post("/webhook")
async def mercado_pago_webhook(request: Request):
    """
    Endpoint para receber notificações (webhooks) do Mercado Pago.
    Aqui você pode atualizar o status do pagamento no seu sistema.
    """
    data = await request.json()
    print("Webhook recebido:", data)
    return {"status": "received"}
