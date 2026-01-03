import tkinter as tk
from tkinter import ttk, messagebox

from .auth import AuthManager, User


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Sistema de Gestão de Propostas")
        self.geometry("320x200")
        self.resizable(False, False)

        self._user: User | None = None

        AuthManager.ensure_default_admin()  # garante admin/admin pelo menos uma vez

        self._criar_widgets()

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Usuário:").pack(anchor="w", pady=(0, 3))
        self.entry_user = ttk.Entry(frame)
        self.entry_user.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(frame, text="Senha:").pack(anchor="w", pady=(0, 3))
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.pack(fill=tk.X, pady=(0, 8))

        self.entry_user.focus()

        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(frame_botoes, text="Entrar", command=self._login)\
            .pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(frame_botoes, text="Cadastrar Usuário", command=self._cadastro)\
            .pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        ttk.Label(
            frame,
            text="Dica inicial: usuário admin / senha admin",
            foreground="gray"
        ).pack(anchor="w", pady=(10, 0))

        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Atenção", "Informe usuário e senha.")
            return

        user = AuthManager.authenticate(username, password)

        if user:
            self._user = user
            self.destroy()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    def _cadastro(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Atenção", "Preencha usuário e senha para cadastrar.")
            return

        if AuthManager.create_user(username, password):
            messagebox.showinfo("Sucesso", f"Usuário '{username}' cadastrado com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível cadastrar. Usuário já existe?")

    @property
    def user(self) -> User | None:
        return self._user
