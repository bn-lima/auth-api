from random import randint
from .models import SMSCode
import os
from twilio.rest import Client

def get_sms_code(): # Gera código que será enviado por sms
    str_code = "".join(str(randint(0,9)) for i in range(0,6)) # Cria código de 6 dígitos

    if SMSCode.objects.filter( # Verifica se existe um objeto SMSCode ativo com o mesmo código
        code=str_code,
        active=True,
        expired=False
    ).exists():
        
        return None # Retorna None caso exista
    
    return str_code # Retorna o código caso não exista

def send_sms_code(phone, sms_code): # Envia código por sms
    account_sid = os.getenv("account_sid")
    auth_token = os.getenv("auth_token")
    twillio_phone = os.getenv("twillio_phone") # Número de telefone da conta twillio

    client = Client(account_sid, auth_token)

    client.messages.create( # Envia mensagem com código por sms
        to=phone,
        body=f"Here is your confirmation code: {sms_code}",
        from_ = twillio_phone
    )