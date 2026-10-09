from django.test import TestCase
from accounts.models import Account

class ControlPanelTestCase(TestCase): # Classe de testes do painel de controle

    def setUp(self):

        self.default_email = "test_user@gmail.com" # Define email padrão
        self.default_password = "12345678" # Define senha padrão

        self.account = Account.objects.create_superuser( # Cria uma conta de admin usando o email padrão
            email=self.default_email,
            username="test_user",
        )
        # Define e salva a senha padrão na conta
        self.account.set_password(self.default_password)
        self.account.save(update_fields=["password"])

        return super().setUp()


    def login_and_get_access_token(self, email, password): # Realiza login e retorna access_token

        # Faz requisição para o endpoint de login passando o email e senha
        response = self.client.post(
            "/account/login/",
            {
                "email":email,
                "password":password
            }
        )

        return response.data.get("access_token")
        

    def test_accounts_list(self):  # Testa a listagem de contas

        # Pega access_token chamando login_and_get_access_token
        access_token = self.login_and_get_access_token(
            self.default_email,
            self.default_password
        )

        self.assertTrue(access_token) # Verifica se o access_token existe

        # Faz requisição para o endpoint que lista as contas
        response = self.client.get(
            "/control-panel/account/list/",
            HTTP_AUTHORIZATION = f"Bearer {access_token}" # Passa o access_token no headers
        )

        # Verifica se a requisição foi bem sucedida
        self.assertEqual(response.status_code, 200)

    def test_account_detail(self): # Testa detalhes da conta

        # Pega access_token passando default_email e default_password
        access_token = self.login_and_get_access_token(
            self.default_email,
            self.default_password
        )

        # Verifica se access_token existe
        self.assertTrue(access_token)

        # Faz requisição para o endpoint que mostra os detalhes da conta
        response = self.client.get(
            f"/control-panel/account/{self.account.id}/detail/",
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )

        # Verifica se a requisição foi bem sucedida
        self.assertEqual(response.status_code, 200)