from gestor_propostas.models import GestorPropostas
from gestor_propostas.ui import App
from gestor_propostas.login_ui import LoginWindow

def main():
    login = LoginWindow()
    login.mainloop()

    user = login.user
    if not user:
        return

    
    gestor = GestorPropostas()
    app = App(gestor, usuario_logado=user.username)
    app.atualizar_listas()
    app.mainloop()


if __name__ == "__main__":
    main()
