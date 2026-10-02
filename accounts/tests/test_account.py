from django.test import TestCase
from accounts.models import PendingAccountRegistration, PendingRegistrationToken, Account

class AccountTestCase(TestCase):

    def setUp(self):

        self.account = Account.objects.create( # Cria usuário para testes
            username="test_uuser",
            email="test_uuser@gmail.com"
        )

        self.account.set_password("12345678") # Define senha na conta
        self.account.save(update_fields=["password"]) # Salva a senha
        
        return super().setUp()

     # Faz uma requisição POST para iniciar o cadastro de uma conta
    def request_account_registration(self, email):
        return self.client.post( 
            "/account/register/request/",
            {"email":email}
        )

    # Faz uma requisição POST para confirmar o cadastro da conta
    # Recebe o token de confirmação e os dados do usuário
    def request_confirm_account_registration(self, registration_token, payload):

        return self.client.post(
            f"/account/register/confirm/{registration_token}/", # Monta a URL usando o token de confirmação
            payload # Dados enviados para confirmar o cadastro
        )
    
    # Envia uma requisição POST para o endpoint de login
    def request_login_account(self, payload):

        return self.client.post(
            "/account/login/",
            payload
        )

    # Envia uma requisição para o enpoint responsável por gerar um novo access_token
    def request_refresh_token(self, refresh_token):

        return self.client.post(
            "/account/refresh/",
            {
                "refresh_token": refresh_token
            }
        )

    # Busca no banco de dados um cadastro pendente pelo e-mail
    def get_pending_registration(self, email):
        return PendingAccountRegistration.objects.filter(
            email=email
        ).first()
    # Busca no banco de dados o token associado ao cadastro pendente
    def get_pending_registration_token(self, pending_registration):
        return PendingRegistrationToken.objects.filter(
            pending_registration=pending_registration
        ).first()

    # Testa a solicitação inicial de cadastro.
    def test_request_account_registration(self):

        email = "test_user@gmail.com" # E-mail utilizado no teste

        response = self.request_account_registration(email) # Faz a requisição para iniciar o cadastro

        self.assertEqual(response.status_code, 200) # Verifica se a resposta HTTP possui status 200

        pending_registration = self.get_pending_registration(email) # Busca o cadastro pendente criado pela requisição

        pending_registration_token = self.get_pending_registration_token(pending_registration)

        self.assertTrue(pending_registration)# Verifica se pending_registration existe        
        self.assertTrue(pending_registration_token)# Verifica se pending_registration_token existe

      # Testa a confirmação do cadastro da conta
    def test_confirm_account_registration(self):

        email = "test_user@gmail.com" # E-mail utilizado no teste

        self.request_account_registration(email) # Primeiro solicita o cadastro da conta

        pending_registration = self.get_pending_registration(email) # Recupera o cadastro pendente criado
        pending_registration_token = self.get_pending_registration_token(pending_registration) # Recupera o token associado ao cadastro pendente

        self.assertTrue(pending_registration)  # Verifica se o cadastro pendente existe
        self.assertTrue(pending_registration_token) # Verifica se o token existe

        # Dados necessários para concluir o cadastro
        payload = {
            "username": "test_user",
            "password": "12345678",
            "confirm_password": "12345678",
            "cpf": "00000000000",
        }

        # Envia o token e os dados para confirmar o cadastro
        response = self.request_confirm_account_registration(
            pending_registration_token.key,
            payload
        )

        # Verifica se a confirmação do cadastro retornou HTTP 201
        self.assertEqual(response.status_code, 201)

    # Testa o login de uma conta existente
    def test_login_account(self):

         # Dados enviados na requisição de login
        payload = {
            "email": "test_uuser@gmail.com",
            "password": "12345678"
        }

        response = self.request_login_account(payload)

        # Verifica se o login foi realizado com sucesso
        self.assertEqual(response.status_code, 200)

    def test_refresh_token(self):

        # Dados usados para realizar o login da conta
        payload = { 
            "email": "test_uuser@gmail.com",
            "password": "12345678"
        }

         # Realiza o login e armazena a resposta da requisição
        login_response = self.request_login_account(payload) 

        # Obtém o refresh token retornado no login
        refresh_token = login_response.data["refresh_token"]

        # Envia o refresh token para o endpoint responsável por gerar um novo access token

        response = self.request_refresh_token(refresh_token)

         # Verifica se a requisição foi processada com sucesso
        self.assertEqual(response.status_code, 200)

    def test_logout_account(self):
        # Dados usados para realizar o login
        payload = {
            "email": "test_uuser@gmail.com",
            "password": "12345678"
        }

        # Realiza o login e obtém os tokens
        login_response = self.request_login_account(payload)
        access_token = login_response.data["access_token"]
        refresh_token = login_response.data["refresh_token"]

        # Realiza o logout usando o access token
        response = self.client.post(
            "/account/logout/",
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )   

         # Verifica se o logout foi realizado com sucesso
        self.assertEqual(response.status_code, 204)

          # Tenta utilizar o refresh token após o logout
        refresh_token_response = self.request_refresh_token(refresh_token)

        # Verifica se o refresh token foi invalidado
        self.assertEqual(
            refresh_token_response.status_code, 400
        )