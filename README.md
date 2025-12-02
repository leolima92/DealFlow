# 🧾 Sistema de Gestão de Propostas Comerciais

**Aplicação desktop desenvolvida em Python + Tkinter, com arquitetura orientada a objetos e exportação profissional para Excel.**

---

## 📌 Sobre o Projeto

O **Sistema de Gestão de Propostas Comerciais** é uma aplicação simples, porém robusta, para gerenciamento de clientes, criação de propostas e geração de relatórios em Excel.

Ele oferece uma experiência completa para pequenas empresas, freelancers ou equipes comerciais que precisam registrar oportunidades e gerar propostas organizadas, mantendo tudo centralizado em um único sistema.

---

## 🚀 Funcionalidades Principais

### 👤 **Gerenciamento de Clientes**

* Cadastro de novos clientes
* Documento e informações de contato opcionais
* Lista sempre atualizada na interface

### 🧾 **Criação e Gerenciamento de Propostas**

* Definição de título, validade, responsável e condições de pagamento
* Status da proposta:

  * *rascunho, enviada, aceita, recusada, cancelada*
* Filtro por status direto na interface

### 📦 **Itens de Proposta**

* Adição de múltiplos itens com:

  * Descrição
  * Quantidade
  * Valor unitário
* Cálculo automático:

  * Subtotal
  * Desconto
  * Total final

### 💰 **Descontos**

* Desconto em **%**
* Desconto em **valor fixo (R$)**
* Possibilidade de remover desconto

### 📑 **Exportação para Excel**

Geração automática de arquivo *Excel* com duas abas:

* **Propostas:** informações gerais de cada proposta
* **Itens:** lista detalhada de todos os itens vinculados

### 🔁 **Duplicar Proposta**

* Cria uma nova proposta com todos os campos e itens copiados
* Útil para orçamentos recorrentes

---

## 🧱 Arquitetura do Projeto (POO)

A aplicação segue uma estrutura clara e organizada:

### **Classes principais**

| Classe                 | Responsabilidade                             |
| ---------------------- | -------------------------------------------- |
| `Cliente`              | Armazena dados do cliente                    |
| `ItemProposta`         | Representa um item dentro da proposta        |
| `Proposta`             | Controla itens, descontos, status e cálculos |
| `GestorPropostas`      | Gerencia listas de clientes e propostas      |
| `ExcelReportGenerator` | Gera o relatório Excel com abas              |
| `App`                  | Interface gráfica (Tkinter)                  |

---

## 🖥️ Tecnologias Utilizadas

* **Python 3.x**
* **Tkinter** (GUI)
* **OpenPyXL** (geração de planilhas Excel)
* **POO (Programação Orientada a Objetos)**
* **Typing** (tipagem opcional para maior clareza)

---

## 📦 Como Executar o Projeto

### 🔧 Pré-requisitos

Certifique-se de ter o Python instalado:

```bash
python --version
```

E instale a dependência necessária:

```bash
pip install openpyxl
```

### ▶️ Rodando a aplicação

```bash
python main.py
```

---

## 📂 Estrutura Recomendada de Pastas

```
GestorPropostas/
│
├── relatorios/             # Excel gerado automaticamente
├── main.py                 # Arquivo principal
├── README.md               # Documentação do projeto

```
---

## 📝 Possíveis Melhorias Futuras

* 💾 Persistência de dados (SQLite ou JSON)
* 🌐 Versão web com Flask ou Django
* 🎨 Estilização avançada da interface
* 🧮 Cálculo de impostos ou margens
* 📤 Exportação da proposta em PDF

