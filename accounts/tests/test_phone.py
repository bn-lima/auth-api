from django.test import TestCase
from unittest.mock import patch
from accounts.models import Account, SMSCode

class PhoneTestCase(TestCase):

    def setUp(self):

        self.default_phone = "11111111111"
        self.default_email = "test_user@gmail.com"  # Define o e-mail padrão utilizado nos testes
        self.default_password = "12345678"  # Define a senha padrão utilizada nos testes

        self.account = Account.objects.create(  # Cria uma conta para ser utilizada nos testes
            username="test_user",
            email=self.default_email,   
        )

        self.account.set_password(self.default_password)  # Define a senha da conta
        self.account.save(update_fields=["password"])  # Salva apenas o campo da senha

        return super().setUp()

    # Realiza o login da conta e retorna os tokens de autenticação
    def login_and_get_auth_tokens(self, email, password):

        # Envia a requisição de login com o email e a senha informados
        response = self.client.post(
            "/account/login/",
            {
                "email": email,
                "password": password
            }
        )

         # Obtém os dados retornados pela API
        data = response.data

        # Retorna o access token e o refresh token
        return data["access_token"], data["refresh_token"]

    # Envia a requisição para adicionar um número de telefone
    def request_add_phone_number(self, access_token, phone):

         # Envia o número de telefone e o token de autenticação
        return self.client.post(
            "/account/phone/send-code/",
            {
                "phone": phone
            },
            HTTP_AUTHORIZATION = f"Bearer {access_token}",
        )


    # Testa a adição de um número de telefone
    @patch("accounts.serializers.send_sms_code")    
    def test_add_phone_number(self, mock_send_sms_code):

         # Define o retorno da função responsável pelo envio do SMS
        mock_send_sms_code.return_value = True

        # Realiza o login e obtém o access token
        access_token, _ = self.login_and_get_auth_tokens(
            self.default_email,
            self.default_password
        )

        # Verifica se o access token foi obtido
        self.assertTrue(access_token)

        # Envia a requisição para adicionar o número de telefone
        response = self.request_add_phone_number(
            access_token,
            self.default_phone
        )

         # Verifica se a requisição foi processada com sucesso
        self.assertEqual(response.status_code, 200)

        # Busca o código SMS criado para a conta
        sms_code = SMSCode.objects.filter(
            account=self.account
        ).first()

        # Verifica se o código SMS foi criado
        self.assertTrue(sms_code)

    # Testa a confirmação do número de telefone
    @patch("accounts.serializers.send_sms_code")
    def test_confirm_phone_number(self, mock_send_sms_code):

         # Define o retorno da função responsável pelo envio do SMS
        mock_send_sms_code.return_value = True

        # Realiza o login e obtém o access token
        access_token, _ = self.login_and_get_auth_tokens(
            self.default_email,
            self.default_password
        )

        # Verifica se o access token foi obtido
        self.assertTrue(access_token)

         # Envia a requisição para adicionar o número de telefone
        add_phone_response = self.request_add_phone_number(
            access_token,
            self.default_phone
        )

         # Verifica se a requisição de adição do telefone foi processada com sucesso
        self.assertEqual(add_phone_response.status_code, 200)

        # Busca o código SMS criado para a conta
        sms = SMSCode.objects.filter(
            account=self.account
        ).first()

         # Verifica se o código SMS foi criado
        self.assertTrue(sms)

        # Envia o código SMS para confirmar o número de telefone
        response = self.client.post(
            "/account/phone/confirm/",
            {
                "verification_code": sms.code
            },
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )

         # Atualiza os dados da conta com os valores atuais do banco de dados
        self.account.refresh_from_db()

        # Verifica se o número de telefone foi salvo corretamente na conta
        self.assertEqual(
            self.account.phone,
            self.default_phone
        )

          # Verifica se a confirmação do telefone foi processada com sucesso
        self.assertEqual(response.status_code, 200)