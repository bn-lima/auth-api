from django.test import TestCase
from accounts.models import Account, ResetPasswordToken


class PasswordTestCase(TestCase):

    def setUp(self):

        self.account = Account.objects.create(  # Cria uma conta para ser utilizada nos testes
            username="test_user",
            email="test_user@gmail.com",   
        )

        self.account.set_password("12345678")  # Define a senha da conta
        self.account.save(update_fields=["password"])  # Salva apenas o campo da senha

        self.default_email = "test_user@gmail.com"  # Define o e-mail padrão utilizado nos testes
        self.default_password = "12345678"  # Define a senha padrão utilizada nos testes

        return super().setUp()

    def request_password_reset(self, access_token):  # Envia uma requisição para solicitar o reset de senha

        return self.client.post(
            "/account/password/reset/request/",
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )

    def request_reset_password(self, reset_token, payload):

        return self.client.post(
            f"/account/password/reset/{reset_token}/",
            payload
        )

    def login_account_and_get_auth_tokens(self, email, password):  # Realiza o login e retorna os tokens de autenticação

        response = self.client.post(  # Envia uma requisição para o endpoint de login
            "/account/login/",
            {
                "email": email,
                "password": password
            }
        )

        data = response.data  # Obtém os dados retornados pela API
        return data["access_token"], data["refresh_token"]  # Retorna o access token e o refresh token

    def test_reset_password_request(self):  # Testa a solicitação de reset de senha

        access_token, _ = self.login_account_and_get_auth_tokens(  # Realiza o login e obtém o access token
            self.default_email,
            self.default_password
        )

        response = self.request_password_reset(access_token)  # Solicita o reset de senha

        self.assertEqual(response.status_code, 200)  # Verifica se a solicitação foi realizada com sucesso

        reset_token = ResetPasswordToken.objects.filter(  # Busca o token de reset associado à conta
            account=self.account
        ).first()

        self.assertTrue(reset_token)  # Verifica se o token de reset foi criado

    def test_reset_password(self): # Testa troca de senha

        access_token, _ = self.login_account_and_get_auth_tokens( # Pega o access_token da conta
            self.default_email,
            self.default_password
        )
        # Envia uma requisição para endpoint responsável por gerar uma solicitação de troca de senha
        reset_request_response = self.request_password_reset(access_token)

        self.assertEqual(reset_request_response.status_code, 200) # Verifica se a requisição foi aceita

        reset_token = ResetPasswordToken.objects.filter(  # Busca o token de reset associado à conta
            account=self.account
        ).first()

        self.assertTrue(reset_token) # Verifica se reset_token existe

        payload = { # Cria payload que será enviado para o endpoint de troca de senha
            "new_password":"11111111",
            "confirm_new_password": "11111111"
        }

        response = self.request_reset_password( # Faz uma requisição para o endpoint de troca de senha
            reset_token.key,
            payload
        )

        self.assertEqual(response.status_code, 200) # Verifica se a troca de senha foi bem sucedida

        login_response = self.client.post( # Tenta fazer login com a nova senha
            "/account/login/",
            {
                "email": self.default_email,
                "password": "11111111"
            }
        )

        self.assertEqual(login_response.status_code, 200) # Verica se o login foi feito com sucesso