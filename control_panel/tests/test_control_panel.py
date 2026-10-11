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

    def test_delete_account(self): # Testa a exclusão de uma conta

        test_account = Account.objects.create(
            email="test_account2@gmail.com",
            username = "test_account2"
        )

        # Realiza login e obtém o access_token
        access_token = self.login_and_get_access_token(
            self.default_email,
            self.default_password
        )

        # Verifica se o access_token foi obtido
        self.assertTrue(access_token)

        # Envia uma requisição DELETE para excluir a conta
        response = self.client.delete(
            f"/control-panel/account/{test_account.id}/delete/",
            data={"confirmation_password":self.default_password},
            content_type="application/json",
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )

        # Verifica se a exclusão foi bem-sucedida
        self.assertEqual(response.status_code, 200)

        # Verifica se a conta foi removida do banco de dados
        self.assertFalse(
            Account.objects.filter(
                id=test_account.id
            ).exists()
        )

    def test_update_account(self): # Testa a atualização de dados da conta

        # Obtém o token de acesso da conta padrão
        access_token = self.login_and_get_access_token(
            self.default_email,
            self.default_password
        )

         # Verifica se o token de acesso foi obtido
        self.assertTrue(access_token)

        # Define os dados que serão enviados para atualizar a conta
        payload = {
            "confirmation_password": self.default_password,
            "username": "updated_account",
            "cpf": "00000000000",
            "phone": "11111111111"
        }

        # Envia uma requisição PATCH para atualizar a conta autenticada
        response = self.client.patch(
            f"/control-panel/account/{self.account.id}/update/",

            data=payload,
            content_type="application/json",
            
            HTTP_AUTHORIZATION = f"Bearer {access_token}",
        )

        # Verifica se a atualização foi realizada com sucesso
        self.assertEqual(response.status_code, 200)

        # Atualiza os dados da conta com os valores salvos no banco
        self.account.refresh_from_db()

        # Verifica se o nome de usuário foi atualizado
        self.assertEqual(
            payload["username"], self.account.username
        )

         # Verifica se o CPF foi atualizado
        self.assertEqual(
            payload["cpf"], self.account.cpf
        )

        # Verifica se o telefone foi atualizado
        self.assertEqual(
            payload["phone"], self.account.phone
        )

    def test_create_account(self): # Testa a criação de uma conta

        access_token = self.login_and_get_access_token( # Faz login e pega access_token
            self.default_email,
            self.default_password
        )

        self.assertTrue(access_token) # Verifica se o token de acesso foi pego com sucesso

        payload = { # Cria o payload para a criação da conta
            "email": "test_account@gmail.com",
            "username": "test_account",
            "cpf": "11111111111",
            "phone": "99999999999",
            "confirmation_password": self.default_password,
            "password": "12345678",
            "confirm_password": "12345678"
        }

        response = self.client.post( # Faz requisição de criação de conta enviando o payload com os dados
            "/control-panel/account/create/",
            payload,
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )

        self.assertEqual(response.status_code, 201) # Verifica se a requisição foi bem sucessedida

        self.assertTrue( # Verifica se a conta realmente foi criada
            Account.objects.filter(
                email = "test_account@gmail.com"
            ).exists()
        )