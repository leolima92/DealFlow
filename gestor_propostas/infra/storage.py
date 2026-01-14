import os
import sqlite3
from datetime import datetime
from typing import Dict

from ..domain import GestorPropostas, Cliente, Proposta, ItemProposta, TemplateProposta

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
INSTANCE_DIR = os.path.join(ROOT_DIR, "instance")
DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "dealflow.db")


class StorageManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.environ.get("DEALFLOW_DB_PATH", DEFAULT_DB_PATH)

    def _ensure_db_dir(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_conn(self):
        self._ensure_db_dir()
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        with self._get_conn() as conn:
            cur = conn.cursor()

            # Clientes
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    documento TEXT,
                    contato TEXT
                )
                """
            )

            # Propostas
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS propostas (
                    id INTEGER PRIMARY KEY,
                    cliente_id INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    status TEXT NOT NULL,
                    validade TEXT,
                    responsavel TEXT,
                    condicoes_pagamento TEXT,
                    template_id INTEGER,
                    tipo_desconto TEXT,
                    desconto_percentual REAL,
                    desconto_valor REAL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
                """
            )

            # Itens
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposta_id INTEGER NOT NULL,
                    descricao TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    valor_unitario REAL NOT NULL,
                    FOREIGN KEY (proposta_id) REFERENCES propostas(id)
                )
                """
            )

            # Templates
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    titulo_padrao TEXT,
                    responsavel_padrao TEXT,
                    condicoes_pagamento_padrao TEXT,
                    intro_texto TEXT,
                    termos TEXT,
                    rodape TEXT,
                    cor_primaria TEXT,
                    usar_logo INTEGER,
                    logo_path TEXT
                )
                """
            )

            if not self._has_column(cur, "propostas", "template_id"):
                cur.execute("ALTER TABLE propostas ADD COLUMN template_id INTEGER")

    @staticmethod
    def _has_column(cur: sqlite3.Cursor, table: str, column: str) -> bool:
        cur.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cur.fetchall())

    def salvar_ou_atualizar_cliente(self, cliente: Cliente):
        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM clientes WHERE id = ?", (cliente.id,))
            existe = cur.fetchone() is not None

            if not existe:
                cur.execute(
                    """
                    INSERT INTO clientes (id, nome, documento, contato)
                    VALUES (?, ?, ?, ?)
                    """,
                    (cliente.id, cliente.nome, cliente.documento, cliente.contato),
                )
            else:
                cur.execute(
                    """
                    UPDATE clientes
                       SET nome = ?,
                           documento = ?,
                           contato = ?
                     WHERE id = ?
                    """,
                    (cliente.nome, cliente.documento, cliente.contato, cliente.id),
                )

    def deletar_cliente(self, cliente_id: int):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))

    def salvar_ou_atualizar_proposta(self, proposta: Proposta):
        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM propostas WHERE id = ?", (proposta.id,))
            existe = cur.fetchone() is not None

            data_criacao_str = proposta.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
            validade_str = proposta.validade.strftime("%Y-%m-%d") if proposta.validade else None

            if not existe:
                cur.execute(
                    """
                    INSERT INTO propostas (
                        id, cliente_id, titulo, data_criacao, status,
                        validade, responsavel, condicoes_pagamento,
                        template_id, tipo_desconto, desconto_percentual, desconto_valor
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        proposta.id,
                        proposta.cliente.id,
                        proposta.titulo,
                        data_criacao_str,
                        proposta.status,
                        validade_str,
                        proposta.responsavel,
                        proposta.condicoes_pagamento,
                        proposta.template_id,
                        proposta.tipo_desconto,
                        proposta.desconto_percentual,
                        proposta.desconto_valor,
                    ),
                )
            else:
                cur.execute(
                    """
                    UPDATE propostas
                       SET cliente_id = ?,
                           titulo = ?,
                           data_criacao = ?,
                           status = ?,
                           validade = ?,
                           responsavel = ?,
                           condicoes_pagamento = ?,
                           template_id = ?,
                           tipo_desconto = ?,
                           desconto_percentual = ?,
                           desconto_valor = ?
                     WHERE id = ?
                    """,
                    (
                        proposta.cliente.id,
                        proposta.titulo,
                        data_criacao_str,
                        proposta.status,
                        validade_str,
                        proposta.responsavel,
                        proposta.condicoes_pagamento,
                        proposta.template_id,
                        proposta.tipo_desconto,
                        proposta.desconto_percentual,
                        proposta.desconto_valor,
                        proposta.id,
                    ),
                )

    def deletar_proposta(self, proposta_id: int):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM itens WHERE proposta_id = ?", (proposta_id,))
            cur.execute("DELETE FROM propostas WHERE id = ?", (proposta_id,))

    # =========================================================
    #   TEMPLATES
    # =========================================================
    def salvar_ou_atualizar_template(self, template: TemplateProposta):
        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM templates WHERE id = ?", (template.id,))
            existe = cur.fetchone() is not None

            usar_logo = 1 if template.usar_logo else 0

            if not existe:
                cur.execute(
                    """
                    INSERT INTO templates (
                        id, nome, titulo_padrao, responsavel_padrao,
                        condicoes_pagamento_padrao, intro_texto, termos,
                        rodape, cor_primaria, usar_logo, logo_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        template.id,
                        template.nome,
                        template.titulo_padrao,
                        template.responsavel_padrao,
                        template.condicoes_pagamento_padrao,
                        template.intro_texto,
                        template.termos,
                        template.rodape,
                        template.cor_primaria,
                        usar_logo,
                        template.logo_path,
                    ),
                )
            else:
                cur.execute(
                    """
                    UPDATE templates
                       SET nome = ?,
                           titulo_padrao = ?,
                           responsavel_padrao = ?,
                           condicoes_pagamento_padrao = ?,
                           intro_texto = ?,
                           termos = ?,
                           rodape = ?,
                           cor_primaria = ?,
                           usar_logo = ?,
                           logo_path = ?
                     WHERE id = ?
                    """,
                    (
                        template.nome,
                        template.titulo_padrao,
                        template.responsavel_padrao,
                        template.condicoes_pagamento_padrao,
                        template.intro_texto,
                        template.termos,
                        template.rodape,
                        template.cor_primaria,
                        usar_logo,
                        template.logo_path,
                        template.id,
                    ),
                )

    def deletar_template(self, template_id: int):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM templates WHERE id = ?", (template_id,))

    # =========================================================
    #   ITENS
    # =========================================================
    def sincronizar_itens_proposta(self, proposta: Proposta):
        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("DELETE FROM itens WHERE proposta_id = ?", (proposta.id,))

            for item in proposta.itens:
                cur.execute(
                    """
                    INSERT INTO itens (proposta_id, descricao, quantidade, valor_unitario)
                    VALUES (?, ?, ?, ?)
                    """,
                    (proposta.id, item.descricao, item.quantidade, item.valor_unitario),
                )

    def carregar_tudo(self, gestor: GestorPropostas):
        gestor.clientes.clear()
        gestor.propostas.clear()
        gestor.templates.clear()

        with self._get_conn() as conn:
            cur = conn.cursor()

            # ---- Clientes
            cur.execute("SELECT id, nome, documento, contato FROM clientes ORDER BY id")
            rows_clientes = cur.fetchall()

            mapa_clientes: Dict[int, Cliente] = {}
            max_cliente_id = 0

            for row in rows_clientes:
                cli_id, nome, documento, contato = row
                cliente = Cliente(nome, documento or "", contato or "")
                cliente.id = cli_id
                mapa_clientes[cli_id] = cliente
                gestor.clientes.append(cliente)
                max_cliente_id = max(max_cliente_id, cli_id)

            if max_cliente_id > 0:
                Cliente._contador_id = max_cliente_id + 1

            # ---- Templates
            cur.execute(
                """
                SELECT
                    id, nome, titulo_padrao, responsavel_padrao,
                    condicoes_pagamento_padrao, intro_texto, termos,
                    rodape, cor_primaria, usar_logo, logo_path
                FROM templates
                ORDER BY id
                """
            )
            rows_templates = cur.fetchall()

            max_template_id = 0
            for row in rows_templates:
                (
                    t_id,
                    nome,
                    titulo_padrao,
                    responsavel_padrao,
                    condicoes_pagamento_padrao,
                    intro_texto,
                    termos,
                    rodape,
                    cor_primaria,
                    usar_logo,
                    logo_path,
                ) = row

                template = TemplateProposta(
                    nome=nome,
                    titulo_padrao=titulo_padrao or "",
                    responsavel_padrao=responsavel_padrao or "",
                    condicoes_pagamento_padrao=condicoes_pagamento_padrao or "",
                    intro_texto=intro_texto or "",
                    termos=termos or "",
                    rodape=rodape or "",
                    cor_primaria=cor_primaria or "#1f4e79",
                    usar_logo=bool(usar_logo),
                    logo_path=logo_path or "static/img/dealflow_logo.png",
                )
                template.id = t_id
                gestor.templates.append(template)
                max_template_id = max(max_template_id, t_id)

            if max_template_id > 0:
                TemplateProposta._contador_id = max_template_id + 1

            cur.execute(
                """
                SELECT
                    id, cliente_id, titulo, data_criacao, status,
                    validade, responsavel, condicoes_pagamento, template_id,
                    tipo_desconto, desconto_percentual, desconto_valor
                FROM propostas
                ORDER BY id
                """
            )
            rows_propostas = cur.fetchall()

            mapa_propostas: Dict[int, Proposta] = {}
            max_proposta_id = 0

            for row in rows_propostas:
                (
                    p_id,
                    cliente_id,
                    titulo,
                    data_criacao_str,
                    status,
                    validade_str,
                    responsavel,
                    condicoes_pagamento,
                    template_id,
                    tipo_desconto,
                    desconto_percentual,
                    desconto_valor,
                ) = row

                cliente = mapa_clientes.get(cliente_id)
                if not cliente:
                    continue

                prop = Proposta(
                    cliente=cliente,
                    titulo=titulo,
                    validade=None,
                    responsavel=responsavel or "",
                    condicoes_pagamento=condicoes_pagamento or "",
                    template_id=template_id,
                )

                prop.id = p_id
                try:
                    prop.data_criacao = datetime.strptime(
                        data_criacao_str, "%Y-%m-%d %H:%M:%S"
                    )
                except Exception:
                    prop.data_criacao = datetime.now()

                prop.status = status
                if validade_str:
                    try:
                        prop.validade = datetime.strptime(
                            validade_str, "%Y-%m-%d"
                        ).date()
                    except Exception:
                        prop.validade = None

                prop.tipo_desconto = tipo_desconto
                prop.desconto_percentual = desconto_percentual or 0.0
                prop.desconto_valor = desconto_valor or 0.0

                gestor.propostas.append(prop)
                mapa_propostas[p_id] = prop
                max_proposta_id = max(max_proposta_id, p_id)

            if max_proposta_id > 0:
                Proposta._contador_id = max_proposta_id + 1

            cur.execute(
                """
                SELECT proposta_id, descricao, quantidade, valor_unitario
                FROM itens
                ORDER BY id
                """
            )
            rows_itens = cur.fetchall()

            for row in rows_itens:
                proposta_id, descricao, quantidade, valor_unitario = row
                prop = mapa_propostas.get(proposta_id)
                if not prop:
                    continue
                item = ItemProposta(
                    descricao=descricao,
                    quantidade=int(quantidade),
                    valor_unitario=float(valor_unitario),
                )
                prop.itens.append(item)
