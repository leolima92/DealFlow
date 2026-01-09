# DealFlow
Sistema moderno de gestao de propostas comerciais.

## Visao geral
DealFlow permite criar, gerenciar e enviar propostas com geracao de PDF/Excel, controle de status e autenticacao.

## Funcionalidades
- Cadastro de clientes e propostas
- Templates de proposta (layout, textos e cor no PDF)
- Itens com descricao, quantidade, valor unitario e descontos
- Status: rascunho, enviada, aceita, recusada, cancelada
- Exportacao em PDF e Excel
- Autenticacao e sessao de usuarios
- Tema claro/escuro com preferencia salva

## Tecnologias
- Python 3.11+
- Flask
- SQLite
- OpenPyXL
- ReportLab
- Bootstrap 5
- JavaScript

## Requisitos
- Python 3.11+

## Instalacao e execucao
1. Crie e ative o ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Instale as dependencias
```bash
pip install flask openpyxl reportlab
```

3. Inicie o servidor
```bash
python app.py
```

Acesse `http://localhost:5000`.

## Configuracao
- `DEALFLOW_SECRET_KEY`: chave de sessao do Flask (recomendado definir em producao).
- Logs em `logs/app.log`.
- Base local em `gestor_propostas/services/gestor_propostas.db`.
- Logo padrao em `static/img/dealflow_logo.png` (usado nos templates).

## Estrutura
```
DealFlow/
  app.py
  gestor_propostas/
    __init__.py
    auth.py
    models.py
    ui.py
    services/
      storage.py
      pdf_report.py
      excel_report.py
      gestor_propostas.db
  webapp/templates/
  static/
```
