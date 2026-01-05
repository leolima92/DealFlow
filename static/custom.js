document.addEventListener("DOMContentLoaded", () => {
    const html = document.documentElement;
    const btn = document.getElementById("themeToggle");

    // Carrega tema salvo
    let saved = localStorage.getItem("theme");
    if (saved) {
        html.setAttribute("data-theme", saved);
    }

    // Funções para toggle de senha
    window.togglePassword = function() {
        const password = document.getElementById('password');
        const toggleBtn = document.getElementById('togglePassword');
        if (password && toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
                password.setAttribute('type', type);
                icon.className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
            }
        }
    };

    window.toggleConfirm = function() {
        const confirm = document.getElementById('confirm');
        const toggleBtn = document.getElementById('toggleConfirm');
        if (confirm && toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                const type = confirm.getAttribute('type') === 'password' ? 'text' : 'password';
                confirm.setAttribute('type', type);
                icon.className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
            }
        }
    };

    updateIcon();

    btn.addEventListener("click", () => {
        let current = html.getAttribute("data-theme");

        let newTheme = current === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", newTheme);

        localStorage.setItem("theme", newTheme);
        updateIcon();
    });

    function updateIcon() {
        let current = html.getAttribute("data-theme");
        btn.textContent = current === "dark" ? "☀️" : "🌙";
    }
    
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", e => {
            const targetId = link.getAttribute("href").substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    // Adicionar event listeners aos buttons se existirem
    const togglePasswordBtn = document.getElementById('togglePassword');
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', window.togglePassword);
    }

    const toggleConfirmBtn = document.getElementById('toggleConfirm');
    if (toggleConfirmBtn) {
        toggleConfirmBtn.addEventListener('click', window.toggleConfirm);
    }
});
