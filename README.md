# Auth API

API de autenticação e gerenciamento de contas com Django REST Framework, PostgreSQL
e JWT.

## Executando

Crie um `.env` na raiz com as variáveis abaixo. O arquivo não deve ser commitado.

```env
SECRET_KEY=
DEBUG=
RENDER_EXTERNAL_HOSTNAME=
RENDER_POSTGRES_DB=
RENDER_POSTGRES_USER=
RENDER_POSTGRES_PASSWORD=
RENDER_POSTGRES_HOST=
RENDER_POSTGRES_PORT=
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_HOST=
EMAIL_PORT=
DEFAULT_FROM_EMAIL=
```

Para usar Docker, informe também `POSTGRES_DB`, `POSTGRES_USER` e
`POSTGRES_PASSWORD` no `.env`.

```bash
docker compose up --build
docker compose exec api python manage.py migrate
```

A API ficará em `http://localhost:8000`.

Crie um usuário do admin com `python manage.py createsuperuser`. O painel fica em
`/admin/`.

## Autenticação

Envie o access token nos endpoints protegidos:

```http
Authorization: Bearer <access_token>
```

O access token expira em 15 minutos e o refresh token em 7 dias.

## Endpoints

Base URL: `http://localhost:8000/account`

| `POST` | `/register/` | Cria uma conta |
| `POST` | `/login/` | Retorna access e refresh tokens |
| `POST` | `/refresh/` | Gera um novo access token |
| `POST` | `/logout/` | Invalida os refresh tokens da conta |
| `POST` | `/password/reset/request/` | Solicita reset para a conta logada |
| `POST` | `/password/reset/forgot/` | Solicita reset usando o e-mail |
| `POST` | `/password/reset/<reset_token>/` | Altera a senha usando o token |

Os corpos devem ser enviados em JSON, exceto o cadastro com imagem, que pode usar
`multipart/form-data`.

### Cadastro

`POST /register/`

```json
{
	"username": "maria",
	"email": "maria@example.com",
	"password": "uma-senha-segura",
	"confirm_password": "uma-senha-segura"
}
```

### Login

`POST /login/`

```json
{
	"email": "maria@example.com",
	"password": "uma-senha-segura"
}
```

Resposta: `access_token` e `refresh_token`.

### Renovação

`POST /refresh/`

```json
{
	"refresh_token": "<refresh_token>"
}
```

Resposta: `new_access_token`.

### Logout

`POST /logout/`

Requer o cabeçalho `Authorization`. Retorna `204 No Content`.

### Recuperação de senha

Para uma conta autenticada, chame `POST /password/reset/request/` sem campos. Para
uma conta não autenticada, envie o e-mail:

```json
{
	"email": "maria@example.com"
}
```

A solicitação é feita em `POST /password/reset/forgot/`. O link recebido aponta para
`POST /password/reset/<reset_token>/` e deve enviar:

```json
{
	"new_password": "uma-nova-senha",
	"confirm_new_password": "uma-nova-senha"
}
```

O token expira em 15 minutos, só pode ser usado uma vez e a conta pode ter no máximo
3 solicitações ativas. A nova senha não pode ser igual à anterior.

## Erros e manutenção

Erros de validação retornam `400 Bad Request`; credenciais ou tokens inválidos e
requisições sem autenticação retornam `401 Unauthorized`.

Para inativar tokens de reset expirados:

```bash
python manage.py expire_reset_password_tokens
```

Em produção, substitua o endereço local usado no link de recuperação e configure o
servidor SMTP.