# 💼 DealFlow  
### Sistema moderno de gestão de propostas comerciais

DealFlow é um sistema profissional para criação, gerenciamento e envio de propostas comerciais.  
Desenvolvido em **Python + Flask**, o projeto oferece uma interface elegante, modo escuro, geração de PDFs, exportação Excel, controle de usuários, formas de pagamento e muito mais.

---

## 🚀 Funcionalidades Principais

### 📝 Criação completa de propostas
- Cadastro de clientes  
- Itens detalhados (descrição, quantidade, valor unitário)  
- Cálculo automático de subtotal e total  
- Descontos percentuais ou por valor  
- Condições de pagamento estruturadas (PIX, cartão, boleto, parcelas etc.)

### 🎨 Modo Escuro (Dark Mode)
- Alternância entre tema claro/escuro  
- Preferência é salva automaticamente no navegador  
- Interface moderna e agradável

### 📄 Exportação
- Geração de **PDF profissional**
- Exportação de todas as propostas para **Excel**
- Downloads diretos com um clique

### 🔐 Sistema de Login
- Cadastro de usuários
- Autenticação por sessão
- Proteção das rotas administrativas

### 🔁 Controle de Status da Proposta
- rascunho  
- enviada  
- aceita  
- recusada  
- cancelada  

Com botão dedicado para **Enviar Proposta**.

### ➕ Outras funcionalidades
- Duplicar propostas
- Excluir propostas
- Filtrar por título, cliente e status
- Dashboard inicial com métricas (propostas, clientes, valores)

---

## 🛠️ Tecnologias

DealFlow foi construído com:

- **Python 3.11+**
- **Flask**
- **SQLite** (persistência local)
- **OpenPyXL** (Excel)
- **FPDF** (relatórios em PDF)
- **Bootstrap 5** (UI responsiva)
- **JavaScript** (Dark mode + UX)

---

## 📦 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/dealflow.git
cd dealflow
```

### 2. Crie o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute o servidor Flask
```bash
python webapp/app.py
```


Acesse:

http://localhost:5000

📂 Estrutura do Projeto
dealflow/
│
├── gestor_propostas/
│   ├── models.py
│   ├── storage.py
│   ├── excel_report.py
│   ├── pdf_report.py
│   ├── auth.py
│   └── __init__.py
│
├── webapp/
│   ├── app.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── index.html
│   │   ├── nova_proposta.html
│   │   ├── proposta_detalhe.html
│   │   └── clientes.html
│   └── static/ (caso adicione CSS/JS)
│
├── README.md
