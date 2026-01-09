import pytest

from gestor_propostas.models import Cliente, ItemProposta, Proposta


def test_calculo_total_sem_desconto():
    cliente = Cliente("ACME")
    proposta = Proposta(cliente, titulo="Teste")

    proposta.adicionar_item(ItemProposta("Servico", 2, 100.0))
    proposta.adicionar_item(ItemProposta("Produto", 1, 50.0))

    assert proposta.calcular_subtotal() == 250.0
    assert proposta.calcular_total() == 250.0


def test_desconto_percentual():
    cliente = Cliente("ACME")
    proposta = Proposta(cliente)
    proposta.adicionar_item(ItemProposta("Servico", 2, 100.0))

    proposta.definir_desconto_percentual(10)

    assert proposta.calcular_desconto() == 20.0
    assert proposta.calcular_total() == 180.0


def test_desconto_valor():
    cliente = Cliente("ACME")
    proposta = Proposta(cliente)
    proposta.adicionar_item(ItemProposta("Servico", 2, 100.0))

    proposta.definir_desconto_valor(15)

    assert proposta.calcular_desconto() == 15.0
    assert proposta.calcular_total() == 185.0


def test_status_valido_e_invalido():
    cliente = Cliente("ACME")
    proposta = Proposta(cliente)

    proposta.alterar_status("aceita")
    assert proposta.status == "aceita"

    with pytest.raises(ValueError):
        proposta.alterar_status("desconhecido")
