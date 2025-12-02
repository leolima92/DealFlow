from gestor_propostas.models import GestorPropostas
from gestor_propostas.ui import App


def main():
    gestor = GestorPropostas()
    app = App(gestor)
    app.atualizar_listas()
    app.mainloop()


if __name__ == "__main__":
    main()
