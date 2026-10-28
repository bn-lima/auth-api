# Auth API

API de autenticação e gerenciamento de contas, construída com Django REST
Framework, PostgreSQL e JWT. Inclui cadastro confirmado por e-mail, recuperação
de senha, verificação de telefone por SMS, exclusão de conta e um painel de
gerenciamento restrito a administradores.

## Funcionalidades

- Cadastro de conta em duas etapas: solicitação por e-mail e confirmação por
  token.
- Login por e-mail e senha, emissão de access/refresh tokens e logout com
  invalidação dos refresh tokens emitidos para a conta.
- Verificação de autenticação por access token.
- Solicitação autenticada ou não autenticada de redefinição de senha.
- Cadastro e confirmação de telefone por código SMS.
- Solicitação autenticada e confirmação por e-mail para excluir a própria
  conta.
- Painel de administração de contas, disponível para usuários administradores
  (`is_staff`), com listagem, filtros, paginação, consulta, criação, atualização
  e exclusão.
- Administração Django em `/admin/` e arquivos de mídia em `/media/`.

## Requisitos

- Python 3.14 (versão usada no CI).
- Docker e Docker Compose para executar a configuração do projeto em
  contêineres.
- PostgreSQL; o Compose fornece PostgreSQL 16.

As dependências Python estão listadas em [requirements.txt](requirements.txt).

## Configuração e execução

Crie um arquivo `.env` na raiz do repositório. Ele é ignorado pelo Git e não
deve ser commitado.

### Variáveis de ambiente

| Variável | Uso |
| --- | --- |
| `SECRET_KEY` | Chave secreta do Django. |
| `DEBUG` | Ativa o modo de depuração quando o valor é exatamente `True`. |
| `RENDER_EXTERNAL_HOSTNAME` | Host externo aceito pela configuração de produção. |
| `POSTGRES_DB` | Nome do banco PostgreSQL. |
| `POSTGRES_USER` | Usuário do banco PostgreSQL. |
| `POSTGRES_PASSWORD` | Senha do banco PostgreSQL. |
| `POSTGRES_HOST` | Host do banco; use `db` no Docker Compose ou o host local correspondente. |
| `POSTGRES_PORT` | Porta do PostgreSQL, normalmente `5432`. |
| `EMAIL_USERNAME` | Usuário SMTP. |
| `EMAIL_PASSWORD` | Senha SMTP. |
| `EMAIL_HOST` | Host SMTP. |
| `EMAIL_PORT` | Porta SMTP. |
| `DEFAULT_FROM_EMAIL` | Endereço de remetente usado na configuração de produção. |
| `account_sid` | SID da conta Twilio para envio de SMS. |
| `auth_token` | Token de autenticação da conta Twilio. |
| `twilio_phone` | Número remetente cadastrado na Twilio. |

O serviço `db` do Compose usa essas variáveis PostgreSQL e o serviço `api`
conecta ao host `db`. Com o `.env` configurado, inicie e prepare o banco:

```bash
docker compose up --build
docker compose exec api python manage.py migrate
```

A API ficará disponível em `http://localhost:8000`. Crie um usuário
administrador com:

```bash
docker compose exec api python manage.py createsuperuser
```

Para executar sem Docker, instale as dependências e configure
`POSTGRES_HOST` para o host PostgreSQL acessível ao processo:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O painel Django fica em `http://localhost:8000/admin/`. A configuração CORS
permite atualmente a origem `http://localhost:5174`.

## Autenticação

As rotas protegidas usam JWT. Envie o access token no cabeçalho:

```http
Authorization: Bearer <access_token>
```

O access token expira em 15 minutos e o refresh token em 7 dias. O endpoint de
renovação retorna um novo access token. O logout invalida os refresh tokens
registrados para a conta.

Os exemplos abaixo usam `http://localhost:8000` como base URL e JSON como
formato do corpo, salvo indicação diferente.

## API de contas

Base: `/account/`

| Método | Endpoint | Autenticação | Descrição |
| --- | --- | --- | --- |
| `POST` | `/account/register/request/` | Não | Solicita cadastro e envia e-mail de confirmação. |
| `POST` | `/account/register/confirm/<registration_token>/` | Não | Confirma cadastro com token e dados da conta. |
| `POST` | `/account/login/` | Não | Autentica por e-mail e senha e retorna tokens JWT. |
| `POST` | `/account/refresh/` | Não | Emite um novo access token a partir do refresh token. |
| `POST` | `/account/logout/` | Sim | Invalida os refresh tokens da conta. |
| `GET` | `/account/authenticated/` | Sim | Confirma que o access token é válido. |
| `POST` | `/account/password/reset/request/` | Sim | Solicita redefinição de senha para a conta autenticada. |
| `POST` | `/account/password/reset/forgot/` | Não | Solicita redefinição de senha informando o e-mail. |
| `POST` | `/account/password/reset/<reset_token>/` | Não | Define uma nova senha usando o token recebido por e-mail. |
| `POST` | `/account/phone/send-code/` | Sim | Solicita envio de código SMS para um telefone. |
| `POST` | `/account/phone/confirm/` | Sim | Confirma o telefone com o código SMS. |
| `POST` | `/account/delete/request/` | Sim | Solicita exclusão da própria conta e envia confirmação por e-mail. |
| `DELETE` | `/account/delete/confirm/<deletion_token>/` | Não | Confirma a exclusão da conta usando o token. |

### Cadastro

Primeiro solicite a confirmação para um endereço de e-mail:

```http
POST /account/register/request/
Content-Type: application/json
```

```json
{
  "email": "maria@example.com"
}
```

O link enviado por e-mail contém o token usado na segunda etapa. Confirme o
cadastro com username e senha; CPF e imagem de perfil são opcionais.

```http
POST /account/register/confirm/<registration_token>/
Content-Type: application/json
```

```json
{
  "username": "maria",
  "password": "uma-senha-segura",
  "confirm_password": "uma-senha-segura",
  "cpf": "12345678901"
}
```

O cadastro pendente expira em 24 horas; cada token de confirmação expira em
15 minutos. São permitidos até três tokens ativos por solicitação pendente. A
senha deve ter ao menos oito caracteres e não pode conter espaços. Para enviar
uma imagem de perfil, use `multipart/form-data`.

### Login, renovação e logout

Faça login com o endereço de e-mail e a senha:

```http
POST /account/login/
Content-Type: application/json
```

```json
{
  "email": "maria@example.com",
  "password": "uma-senha-segura"
}
```

A resposta contém `access_token` e `refresh_token`. Para renovar o access
token:

```json
{
  "refresh_token": "<refresh_token>"
}
```

Envie esse corpo para `POST /account/refresh/`; a resposta contém
`new_access_token`. Para sair, envie `POST /account/logout/` com o cabeçalho
Bearer; a resposta é `204 No Content`.

### Redefinição de senha

Uma conta autenticada solicita o link sem corpo em:
`POST /account/password/reset/request/`
Sem autenticação, envie o e-mail para
`POST /account/password/reset/forgot/`:

```json
{
  "email": "maria@example.com"
}
```

Use o token do e-mail no caminho e envie a nova senha e sua confirmação:

```http
POST /account/password/reset/<reset_token>/
Content-Type: application/json
```

```json
{
  "new_password": "uma-nova-senha",
  "confirm_new_password": "uma-nova-senha"
}
```

O token expira em 15 minutos. Cada conta pode ter até três solicitações ativas;
após redefinir a senha, os tokens de redefinição ativos da conta são
desativados. A nova senha deve ter ao menos oito caracteres, não pode conter
espaços e não pode ser igual à senha atual.

### Telefone

Solicite um código enviando um telefone com 10 ou 11 dígitos para
`POST /account/phone/send-code/`:

```json
{
  "phone": "11987654321"
}
```

Depois, confirme em `POST /account/phone/confirm/`:

```json
{
  "verification_code": "123456"
}
```

O código tem seis dígitos e expira em 15 minutos. Um número não pode estar
associado a outra conta; cada conta pode ter até três códigos SMS ativos.
Configure as variáveis Twilio indicadas acima para integrar o envio.

### Exclusão da própria conta

Solicite a exclusão autenticado, sem corpo:
`POST /account/delete/request/`. A confirmação chega por e-mail e deve ser
feita com o token no caminho:

```http
DELETE /account/delete/confirm/<deletion_token>/
```

O token expira em 15 minutos e são permitidas até três solicitações ativas por
conta.

## Painel de gerenciamento de contas

Base: `/control-panel/account/`. Todos os endpoints exigem autenticação de
administrador (`is_staff`). A criação, atualização e exclusão exigem a senha
atual do administrador no campo `confirmation_password`.

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `GET` | `/control-panel/account/list/` | Lista contas com filtros e paginação. |
| `POST` | `/control-panel/account/create/` | Cria uma conta pelo painel. |
| `GET` | `/control-panel/account/<id>/detail/` | Retorna os dados detalhados da conta. |
| `PUT`, `PATCH` | `/control-panel/account/<id>/update/` | Atualiza os dados da conta. |
| `DELETE` | `/control-panel/account/<id>/delete/` | Exclui a conta após validar a senha do administrador. |

A listagem aceita os filtros `username`, `email` e `created_at`, além dos
parâmetros de paginação `page` e `page_size`. O tamanho padrão é 20 e o máximo
é 200.

Exemplo de criação:

```json
{
  "email": "nova-conta@example.com",
  "username": "nova-conta",
  "password": "uma-senha-segura",
  "confirm_password": "uma-senha-segura",
  "confirmation_password": "senha-do-administrador",
  "cpf": "12345678901",
  "phone": "11987654321"
}
```

Na atualização, envie os campos que deseja alterar e
`confirmation_password`. A exclusão também requer `confirmation_password` no
corpo JSON. A criação e atualização aceitam imagem de perfil; use
`multipart/form-data` quando enviar um arquivo.

## Administração e manutenção

O projeto disponibiliza estes comandos Django para limpeza/inativação de
registros expirados ou inativos:

| Comando | Ação |
| --- | --- |
| `python manage.py mark_pending_registration_tokens_as_expired` | Inativa tokens de cadastro expirados. |
| `python manage.py delete_expired_registration_requests` | Exclui solicitações de cadastro expiradas. |
| `python manage.py expire_reset_password_tokens` | Inativa tokens de redefinição de senha expirados. |
| `python manage.py expire_inactive_deletion_tokens` | Inativa tokens de exclusão expirados. |
| `python manage.py exclude_inactive_sms_codes` | Exclui códigos SMS inativos. |

Esses comandos podem ser executados dentro do contêiner `api` com
`docker compose exec api` antes do comando. O repositório não agenda sua
execução automaticamente.

## Testes e automação

Execute os testes Django com:

```bash
python manage.py test
```

O workflow de CI instala as dependências, sobe a aplicação com Docker Compose e
executa os testes. Após um CI bem-sucedido na branch `main`, o workflow de CD
dispara o deploy no Render e tenta fazer rollback se a implantação falhar ou
atingir o tempo limite. Esses workflows dependem dos secrets configurados no
GitHub Actions.
