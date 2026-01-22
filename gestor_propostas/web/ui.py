from datetime import datetime
from functools import wraps
import logging
import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
    after_this_request,
)

from ..app_context import get_context


bp = Blueprint("ui", __name__)
logger = logging.getLogger(__name__)


# ========= helpers ========= #

def _cliente_service():
    return get_context().cliente_service


def _proposta_service():
    return get_context().proposta_service


def _template_service():
    return get_context().template_service


def _dashboard_service():
    return get_context().dashboard_service


def _auth_service():
    return get_context().auth_service


def _report_service():
    return get_context().report_service


def _parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_money(value: str):
    if value is None:
        return None
    cleaned = value.strip().replace("R$", "").replace(" ", "")
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("ui.login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapper


@bp.context_processor
def inject_user():
    """Disponibiliza o usuário logado no template como 'usuario_logado'."""
    return {"usuario_logado": session.get("username")}


# ========= auth ========= #

@bp.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("ui.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = _auth_service().authenticate(username, password)
        if user:
            session["username"] = user.username
            logger.info(f"Usuário '{user.username}' fez login com sucesso.")
            flash(f"Bem-vindo, {user.username}!", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("ui.index"))
        else:
            flash("Usuário ou senha inválidos.", "error")

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    username = session.get("username")
    session.clear()
    logger.info(f"Usuário '{username}' fez logout.")
    flash("Sessão encerrada.", "info")
    return redirect(url_for("ui.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    # se já está logado, manda pro dashboard
    if "username" in session:
        return redirect(url_for("ui.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not password:
            flash("Usuário e senha são obrigatórios.", "error")
            return redirect(url_for("ui.register"))

        if password != confirm:
            flash("As senhas não conferem.", "error")
            return redirect(url_for("ui.register"))

        user = _auth_service().create_user(username, password)
        if not user:
            flash("Usuário já existe. Escolha outro.", "error")
            return redirect(url_for("ui.register"))

        flash("Usuário criado com sucesso! Faça login.", "success")
        return redirect(url_for("ui.login"))

    return render_template("register.html")


# ========= dashboard ========= #

@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "").strip().lower()

    vm = _dashboard_service().build_dashboard(q, status)

    return render_template(
        "index.html",
        propostas=vm.propostas,
        filtro_q=vm.filtro_q,
        filtro_status=vm.filtro_status,
        statuses=vm.statuses,
        total_propostas=vm.total_propostas,
        total_clientes=vm.total_clientes,
        qtd_aceitas=vm.qtd_aceitas,
        valor_total_aceitas=vm.valor_total_aceitas,
        status_data=vm.status_data,
        arrecadacao_mes_data=vm.arrecadacao_mes_data,
    )


# ========= propostas ========= #

@bp.route("/propostas/<int:pid>")
@login_required
def proposta_detalhe(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    if not proposta.cliente:
        flash("Cliente da proposta não encontrado.", "error")
        return redirect(url_for("ui.index"))

    templates = _template_service().listar()
    template_selecionado = (
        _template_service().obter_por_id(proposta.template_id)
        if proposta.template_id
        else None
    )

    return render_template(
        "proposta_detalhe.html",
        proposta=proposta,
        templates=templates,
        template_selecionado=template_selecionado,
    )


@bp.route("/propostas/nova", methods=["GET", "POST"])
@login_required
def nova_proposta():
    clientes = _cliente_service().listar()
    templates = _template_service().listar()

    if not clientes:
        flash("Cadastre ao menos um cliente antes de criar uma proposta.", "info")
        return redirect(url_for("ui.novo_cliente"))

    if request.method == "POST":
        cliente_id = int(request.form.get("cliente_id", "0"))
        titulo = request.form.get("titulo", "").strip()
        responsavel = request.form.get("responsavel", "").strip()
        validade_str = request.form.get("validade", "").strip()
        template_id = _parse_int(request.form.get("template_id"))

        forma_pagamento = request.form.get("forma_pagamento", "").strip()
        num_parcelas = request.form.get("num_parcelas", "").strip()
        pagamento_obs = request.form.get("pagamento_obs", "").strip()

        cliente = next((c for c in clientes if c.id == cliente_id), None)
        if not cliente:
            flash("Cliente inválido.", "error")
            return redirect(url_for("ui.nova_proposta"))

        validade = None
        if validade_str:
            try:
                validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Data de validade inválida. Use AAAA-MM-DD.", "error")
                return redirect(url_for("ui.nova_proposta"))

        template = _template_service().obter_por_id(template_id) if template_id else None

        prop = _proposta_service().criar_com_template(
            cliente=cliente,
            titulo=titulo,
            responsavel=responsavel,
            forma_pagamento=forma_pagamento,
            num_parcelas=num_parcelas,
            pagamento_obs=pagamento_obs,
            validade=validade,
            template=template,
        )

        logger.info(f"Proposta #{prop.id} criada por usuário '{session.get('username')}' para cliente '{cliente.nome}'.")
        flash(f"Proposta #{prop.id} criada com sucesso!", "success")
        return redirect(url_for("ui.proposta_detalhe", pid=prop.id))

    return render_template(
        "nova_proposta.html",
        clientes=clientes,
        templates=templates,
    )


@bp.route("/propostas/<int:pid>/add_item", methods=["POST"])
@login_required
def add_item(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    desc = request.form.get("descricao", "").strip()
    qtd_str = request.form.get("quantidade", "0").strip()
    valor_str = request.form.get("valor_unitario", "0").strip()

    if not desc:
        flash("Descrição é obrigatória.", "error")
        return redirect(url_for("ui.proposta_detalhe", pid=pid))

    qtd = _parse_int(qtd_str)
    valor = _parse_money(valor_str)

    if qtd is None or qtd <= 0:
        flash("Quantidade deve ser um número inteiro maior que zero.", "error")
        return redirect(url_for("ui.proposta_detalhe", pid=pid))

    if valor is None or valor < 0:
        flash("Valor unitário deve ser um número válido maior ou igual a zero.", "error")
        return redirect(url_for("ui.proposta_detalhe", pid=pid))

    _proposta_service().adicionar_item(proposta, desc, qtd, valor)

    flash("Item adicionado com sucesso!", "success")
    return redirect(url_for("ui.proposta_detalhe", pid=pid))


@bp.route("/propostas/<int:pid>/desconto", methods=["POST"])
@login_required
def aplicar_desconto(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    tipo = request.form.get("tipo", "nenhum")
    valor_str = request.form.get("valor", "").strip()

    if tipo == "nenhum":
        _proposta_service().aplicar_desconto(proposta, tipo)
        msg = "Desconto removido."
    else:
        valor = _parse_money(valor_str)
        if valor is None:
            flash("Informe um valor numérico para desconto.", "error")
            return redirect(url_for("ui.proposta_detalhe", pid=pid))
        if valor < 0:
            flash("O desconto não pode ser negativo.", "error")
            return redirect(url_for("ui.proposta_detalhe", pid=pid))

        if tipo == "%":
            if valor > 100:
                flash("Desconto percentual deve ser entre 0 e 100.", "error")
                return redirect(url_for("ui.proposta_detalhe", pid=pid))
            _proposta_service().aplicar_desconto(proposta, tipo, valor)
            msg = f"Desconto de {valor:.2f}% aplicado."
        elif tipo == "R":
            _proposta_service().aplicar_desconto(proposta, tipo, valor)
            msg = f"Desconto de R$ {valor:.2f} aplicado."
        else:
            msg = "Tipo de desconto inválido."
    flash(msg, "success")
    return redirect(url_for("ui.proposta_detalhe", pid=pid))


@bp.route("/propostas/<int:pid>/pagamento", methods=["POST"])
@login_required
def atualizar_pagamento(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    forma_pagamento = request.form.get("forma_pagamento", "").strip()
    num_parcelas = request.form.get("num_parcelas", "").strip()
    pagamento_obs = request.form.get("pagamento_obs", "").strip()

    cond_parts = []
    if forma_pagamento:
        cond_parts.append(f"Forma: {forma_pagamento}")
    if num_parcelas:
        cond_parts.append(f"Parcelas: {num_parcelas}x")
    if pagamento_obs:
        cond_parts.append(f"Obs: {pagamento_obs}")
    cond_pag = " | ".join(cond_parts)

    _proposta_service().atualizar_pagamento(proposta, cond_pag)

    flash("Condições de pagamento atualizadas.", "success")
    return redirect(url_for("ui.proposta_detalhe", pid=pid))


@bp.route("/propostas/<int:pid>/template", methods=["POST"])
@login_required
def atualizar_template(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    template_id = _parse_int(request.form.get("template_id"))
    if template_id:
        template = _template_service().obter_por_id(template_id)
        if not template:
            flash("Template invalido.", "error")
            return redirect(url_for("ui.proposta_detalhe", pid=pid))
        _proposta_service().atualizar_template(proposta, template.id)
        flash("Template atualizado.", "success")
    else:
        _proposta_service().atualizar_template(proposta, None)
        flash("Template removido.", "success")

    return redirect(url_for("ui.proposta_detalhe", pid=pid))


@bp.route("/propostas/<int:pid>/excluir", methods=["POST"])
@login_required
def excluir_proposta(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    if not _proposta_service().excluir(pid):
        flash(
            "Erro ao excluir no banco, mas proposta foi removida da lista atual.",
            "error",
        )

    flash(f"Proposta #{pid} excluída com sucesso.", "success")
    return redirect(url_for("ui.index"))


@bp.route("/propostas/<int:pid>/aprovar", methods=["POST"])
@login_required
def aprovar_proposta(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    if proposta.status == "aceita":
        flash(f"A Proposta #{pid} já está aceita.", "info")
        return redirect(url_for("ui.index"))

    _proposta_service().alterar_status(proposta, "aceita")

    logger.info(f"Proposta #{pid} aprovada por usuário '{session.get('username')}'.")
    flash(f"Proposta #{pid} aprovada com sucesso!", "success")
    return redirect(url_for("ui.index"))


@bp.route("/propostas/<int:pid>/enviar", methods=["POST"])
@login_required
def enviar_proposta(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    if proposta.status == "enviada":
        flash(f"A Proposta #{pid} já foi enviada.", "info")
        return redirect(url_for("ui.index"))

    _proposta_service().alterar_status(proposta, "enviada")

    logger.info(f"Proposta #{pid} marcada como enviada por usuário '{session.get('username')}'.")
    flash(f"Proposta #{pid} marcada como enviada!", "success")
    return redirect(url_for("ui.index"))


@bp.route("/propostas/excel")
@login_required
def download_excel():
    propostas = _proposta_service().listar()
    if not propostas:
        flash("Não há propostas para exportar.", "info")
        return redirect(url_for("ui.index"))

    caminho = _report_service().gerar_excel_temp()
    return send_file(caminho, as_attachment=True)


@bp.route("/propostas/<int:pid>/pdf")
@login_required
def download_pdf(pid: int):
    proposta = _proposta_service().obter_por_id(pid)
    if not proposta:
        flash("Proposta não encontrada.", "error")
        return redirect(url_for("ui.index"))

    template = (
        _template_service().obter_por_id(proposta.template_id)
        if proposta.template_id
        else None
    )
    tmp_path = _report_service().gerar_pdf_temp(proposta, template=template)

    @after_this_request
    def _cleanup(response):
        try:
            os.remove(tmp_path)
        except OSError:
            logger.warning("Falha ao remover PDF temporário: %s", tmp_path)
        return response

    return send_file(
        tmp_path,
        as_attachment=True,
        download_name=f"proposta_{proposta.id}.pdf",
    )


# ========= propostas ========= #

@bp.route("/propostas", endpoint="listar_propostas")
@login_required
def propostas_lista():
    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    vm = _dashboard_service().build_propostas_list(
        q=q,
        status=status,
        page=page,
        per_page=per_page,
    )

    return render_template(
        "propostas.html",
        propostas=vm.propostas,
        filtro_q=vm.filtro_q,
        filtro_status=vm.filtro_status,
        statuses=vm.statuses,
        current_page=vm.current_page,
        total_pages=vm.total_pages,
        total_propostas=vm.total_propostas,
    )


# ========= templates ========= #

@bp.route("/templates")
@login_required
def templates_lista():
    return render_template("templates.html", templates=_template_service().listar())


@bp.route("/templates/novo", methods=["GET", "POST"])
@login_required
def novo_template():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome do template e obrigatorio.", "error")
            return redirect(url_for("ui.novo_template"))

        _template_service().criar(
            nome=nome,
            titulo_padrao=request.form.get("titulo_padrao", "").strip(),
            responsavel_padrao=request.form.get("responsavel_padrao", "").strip(),
            condicoes_pagamento_padrao=request.form.get("condicoes_pagamento_padrao", "").strip(),
            intro_texto=request.form.get("intro_texto", "").strip(),
            termos=request.form.get("termos", "").strip(),
            rodape=request.form.get("rodape", "").strip(),
            cor_primaria=request.form.get("cor_primaria", "").strip() or "#1f4e79",
            usar_logo=request.form.get("usar_logo") == "1",
            logo_path=request.form.get("logo_path", "").strip() or "static/img/dealflow_logo.png",
        )
        flash("Template criado com sucesso.", "success")
        return redirect(url_for("ui.templates_lista"))

    return render_template("template_form.html", template=None)


@bp.route("/templates/<int:tid>/editar", methods=["GET", "POST"])
@login_required
def editar_template(tid: int):
    template = _template_service().obter_por_id(tid)
    if not template:
        flash("Template nao encontrado.", "error")
        return redirect(url_for("ui.templates_lista"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome do template e obrigatorio.", "error")
            return redirect(url_for("ui.editar_template", tid=tid))

        template.nome = nome
        template.titulo_padrao = request.form.get("titulo_padrao", "").strip()
        template.responsavel_padrao = request.form.get("responsavel_padrao", "").strip()
        template.condicoes_pagamento_padrao = request.form.get("condicoes_pagamento_padrao", "").strip()
        template.intro_texto = request.form.get("intro_texto", "").strip()
        template.termos = request.form.get("termos", "").strip()
        template.rodape = request.form.get("rodape", "").strip()
        template.cor_primaria = request.form.get("cor_primaria", "").strip() or "#1f4e79"
        template.usar_logo = request.form.get("usar_logo") == "1"
        template.logo_path = request.form.get("logo_path", "").strip() or "static/img/dealflow_logo.png"

        _template_service().atualizar(template)
        flash("Template atualizado.", "success")
        return redirect(url_for("ui.templates_lista"))

    return render_template("template_form.html", template=template)


@bp.route("/templates/<int:tid>/excluir", methods=["POST"])
@login_required
def excluir_template(tid: int):
    template = _template_service().obter_por_id(tid)
    if not template:
        flash("Template nao encontrado.", "error")
        return redirect(url_for("ui.templates_lista"))

    _template_service().excluir(tid)

    flash("Template excluido.", "success")
    return redirect(url_for("ui.templates_lista"))


# ========= clientes ========= #

@bp.route("/clientes")
@login_required
def clientes():
    return render_template("clientes.html", clientes=_cliente_service().listar())


@bp.route("/clientes/novo", methods=["GET", "POST"])
@login_required
def novo_cliente():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        documento = request.form.get("documento", "").strip()
        contato = request.form.get("contato", "").strip()

        if not nome:
            flash("Nome do cliente é obrigatório.", "error")
            return redirect(url_for("ui.novo_cliente"))

        cliente = _cliente_service().criar(nome, documento, contato)

        flash(f"Cliente '{cliente.nome}' criado com sucesso!", "success")
        return redirect(url_for("ui.clientes"))

    return render_template("novo_cliente.html")
