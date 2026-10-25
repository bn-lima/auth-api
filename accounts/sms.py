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

def get_valid_account_sms_code(code, account):

    try: # Busca um código SMS válido para a conta
        sms_code = SMSCode.objects.get(
            account=account,
            code=code,
            active=True,
            expired=False
        )
    # Retorna None caso o código não exista ou não seja válido.
    except SMSCode.DoesNotExist: 
        return None

    return sms_code

def deactivate_account_sms_codes(account): 
    # Desativa todos os códigos SMS ativos e não expirados da conta.
    account.sms_codes.filter(
        active=True,
        expired=False
    ).update(active=False)

def send_sms_code(phone, sms_code): # Envia código por sms
    account_sid = os.getenv("account_sid")
    auth_token = os.getenv("auth_token")
    twilio_phone = os.getenv("twilio_phone") # Número de telefone da conta twillio

    client = Client(account_sid, auth_token)

    client.messages.create( # Envia mensagem com código por sms
        to=phone,
        body=f"Here is your confirmation code: {sms_code}",
        from_ = twilio_phone
    )