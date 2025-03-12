import os
import requests
import datetime
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

@router.post("/subscriptions/create/{amount}/{description}/{user_id}")
async def create_subscription(amount: float, description: str, user_id: int):
    """
    Cria um plano de assinatura recorrente no Mercado Pago utilizando o endpoint /preapproval.
    
    Parâmetros:
      - amount: valor a ser cobrado mensalmente.
      - description: descrição do plano de assinatura.
      - user_id: identificador do usuário (usado como referência externa).
    
    Retorna:
      - init_point ou preapproval_link ou sandbox_init_point: URL para redirecionamento (dependendo do ambiente).
      - preapproval_id: identificador da pré-aprovação criada.
    """
    url = f"{MP_API_BASE_URL}/preapproval"
    
    # Utiliza datetime.now com timezone.utc para garantir um objeto datetime consciente do fuso horário UTC.
    # start_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    # end_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    
    # # Converte para string ISO8601 e substitui "+00:00" por "Z"
    # start_date = start_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # end_date = end_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


    print("Criando plano de assinatura recorrente para o usuário:", user_id)
    payload = {
        "payer_email": "teste@exemplo.com",  # Em produção, utilize o e-mail real do usuário
        "reason": description,
        "external_reference": str(user_id),
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": amount,
            "repetitions": 12,
            "billing_day": 10,
            "billing_day_proportional":True,
            "currency_id": "BRL"
        },
        "back_url": "http://google.com/",  # URL para redirecionamento após aprovação
        "notification_url": "https://webhook.site/6de197d3-3022-41d6-a002-fd97d47b5309"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in (200, 201):
        data = response.json()
        # Tenta obter o link de redirecionamento: pode vir em init_point ou preapproval_link
        init_point = data.get("init_point") or data.get("preapproval_link")
        sandbox_init_point = data.get("sandbox_init_point")
        preapproval_id = data.get("id")
        return {
            "init_point": init_point,
            "sandbox_init_point": sandbox_init_point,
            "preapproval_id": preapproval_id
        }
    else:
        error_detail = response.text
        print("Erro ao criar a assinatura:", error_detail)
        raise HTTPException(status_code=response.status_code, detail="Erro ao criar preferência de assinatura")


@router.post("/webhook")
async def mercado_pago_webhook(request: Request):
    """
    Endpoint para receber notificações (webhooks) do Mercado Pago.
    Aqui você pode atualizar o status do pagamento no seu sistema.
    """
    data = await request.json()
    print("Webhook recebido:", data)
    return {"status": "received"}
