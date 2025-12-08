from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from . import db
from .models import Cliente, Proposta, ItemProposta
from .services.excel_report import ExcelReportGenerator
from .services.pdf_report import PdfReportGenerator

bp = Blueprint("ui", __name__)

def get_current_user() -> str | None:
    return session.get("user")


@bp.context_processor
def inject_globals():
    return {"current_user": get_current_user()}


@bp.route("/")
def index():
    total_clientes = Cliente.query.count()
    total_propostas = Proposta.query.count()
    propostas_recent = (
        Proposta.query.order_by(Proposta.data_criacao.desc()).limit(5).all()
    )
    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_propostas=total_propostas,
        propostas_recent=propostas_recent,
    )

@bp.route("/clientes")
def listar_clientes():
    clientes = Cliente.query.order_by(Cliente.nome.asc()).all()
    return render_template("clientes.html", clientes=clientes)


@bp.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        documento = request.form.get("documento", "").strip()
        contato = request.form.get("contato", "").strip()

        if not nome:
            flash("Nome do cliente é obrigatório.", "warning")
            return render_template("novo_cliente.html")

        cliente = Cliente(nome=nome, documento=documento, contato=contato)
        db.session.add(cliente)
        db.session.commit()

        flash("Cliente criado com sucesso.", "success")
        return redirect(url_for("ui.listar_clientes"))

    return render_template("novo_cliente.html")


@bp.route("/propostas")
def listar_propostas():
    status = request.args.get("status")
    busca = request.args.get("q", "").strip().lower()

    query = Proposta.query

    if status:
        query = query.filter_by(status=status)

    if busca:
        query = query.join(Cliente).filter(
            (Proposta.titulo.ilike(f"%{busca}%"))
            | (Cliente.nome.ilike(f"%{busca}%"))
        )

    propostas = query.order_by(Proposta.data_criacao.desc()).all()
    return render_template("propostas.html", propostas=propostas, filtro_status=status, busca=busca)


@bp.route("/propostas/nova", methods=["GET", "POST"])
def nova_proposta():
    clientes = Cliente.query.order_by(Cliente.nome.asc()).all()
    if not clientes:
        flash("Cadastre um cliente antes de criar uma proposta.", "info")
        return redirect(url_for("ui.novo_cliente"))

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        titulo = request.form.get("titulo", "").strip()
        responsavel = request.form.get("responsavel", "").strip()
        validade_str = request.form.get("validade", "").strip()
        condicoes_pagamento = request.form.get("condicoes_pagamento", "").strip()

        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            flash("Cliente inválido.", "danger")
            return render_template("nova_proposta.html", clientes=clientes)

        validade = None
        if validade_str:
            try:
                validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Data de validade inválida. Use AAAA-MM-DD.", "warning")
                return render_template("nova_proposta.html", clientes=clientes)

        if not titulo:
            titulo = f"Proposta {datetime.now().strftime('%Y%m%d_%H%M%S')}"

        proposta = Proposta(
            cliente=cliente,
            titulo=titulo,
            responsavel=responsavel,
            validade=validade,
            condicoes_pagamento=condicoes_pagamento,
        )
        db.session.add(proposta)
        db.session.flush() 

        descricoes = request.form.getlist("item_descricao")
        quantidades = request.form.getlist("item_qtd")
        valores = request.form.getlist("item_valor")

        for desc, qtd, val in zip(descricoes, quantidades, valores):
            desc = (desc or "").strip()
            if not desc:
                continue
            try:
                qtd_int = int((qtd or "1").strip())
                valor_float = float((val or "0").replace(",", "."))
            except ValueError:
                continue

            item = ItemProposta(
                proposta=proposta,
                descricao=desc,
                quantidade=qtd_int,
                valor_unitario=valor_float,
            )
            db.session.add(item)

        db.session.commit()

        flash(f"Proposta #{proposta.id} criada com sucesso.", "success")
        return redirect(url_for("ui.detalhe_proposta", proposta_id=proposta.id))

    return render_template("nova_proposta.html", clientes=clientes)


@bp.route("/propostas/<int:proposta_id>")
def detalhe_proposta(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)
    return render_template("proposta_detalhe.html", proposta=proposta)


@bp.route("/propostas/<int:proposta_id>/status", methods=["POST"])
def alterar_status(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)
    novo_status = request.form.get("status", "").lower()

    try:
        proposta.alterar_status(novo_status)
        db.session.commit()
        flash("Status atualizado com sucesso.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("ui.detalhe_proposta", proposta_id=proposta.id))


@bp.route("/propostas/<int:proposta_id>/desconto", methods=["POST"])
def aplicar_desconto(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)

    tipo = request.form.get("tipo")  
    valor = request.form.get("valor", "").replace(",", ".").strip()

    if tipo == "nenhum":
        proposta.tipo_desconto = None
        proposta.desconto_valor = 0.0
        proposta.desconto_percentual = 0.0
    else:
        try:
            v = float(valor or "0")
        except ValueError:
            flash("Valor de desconto inválido.", "warning")
            return redirect(url_for("ui.detalhe_proposta", proposta_id=proposta.id))

        if tipo == "%":
            proposta.definir_desconto_percentual(v)
        elif tipo == "R":
            proposta.definir_desconto_valor(v)

    db.session.commit()
    flash("Desconto aplicado com sucesso.", "success")
    return redirect(url_for("ui.detalhe_proposta", proposta_id=proposta.id))

@bp.route("/relatorios/propostas/excel")
def exportar_propostas_excel():
    propostas = Proposta.query.all()
    flash("Geração de Excel ainda precisa ser integrada ao serviço.", "info")
    return redirect(url_for("ui.listar_propostas"))


@bp.route("/propostas/<int:proposta_id>/pdf")
def exportar_proposta_pdf(proposta_id: int):
    proposta = Proposta.query.get_or_404(proposta_id)
    flash("Geração de PDF ainda precisa ser integrada ao serviço.", "info")
    return redirect(url_for("ui.detalhe_proposta", proposta_id=proposta.id))
