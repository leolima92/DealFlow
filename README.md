# DealFlow

DealFlow é um sistema simples para **gerenciamento de propostas comerciais**, desenvolvido com Flask.
Permite cadastrar propostas, gerenciar itens, acompanhar status e exportar documentos em **PDF** ou **Excel**,
com foco em simplicidade, organização e boas práticas.

---

## 📌 Funcionalidades

- 👤 Autenticação de usuários
- 📝 Cadastro de propostas e itens
- 🔁 Controle de status das propostas
- 📄 Exportação para **PDF** e **Excel**
- 🔒 Segurança com:
  - Proteção CSRF em formulários
  - Hash de senhas com **Argon2**
  - Cookies com flags de segurança

---

## 🧠 Tecnologias

- **Python 3.10+**
- **Flask**
- **SQLite**
- **ReportLab** (geração de PDF)
- **OpenPyXL** (geração de Excel)

---

## 🚀 Começando

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/leolima92/DealFlow.git
cd DealFlow
````

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as configurações necessárias (ex.: `SECRET_KEY`, e-mail, etc.).

4. Inicialize o banco de dados:

```bash
flask db upgrade
```

5. Crie um usuário administrador:

```bash
flask seed admin
```

6. Execute a aplicação:

```bash
flask run
```

---

## 🧩 Organização do Projeto

```
DealFlow/
│── app/                  # Código principal da aplicação
│   ├── models/           # Modelos de banco de dados
│   ├── routes/           # Rotas / controllers
│   ├── services/         # Serviços (PDF, Excel, etc.)
│   └── templates/        # Templates HTML / documentos
│── migrations/           # Migrations do banco
│── tests/                # Testes automatizados
│── .env.example          # Exemplo de variáveis de ambiente
├── requirements.txt
├── README.md
```

---
