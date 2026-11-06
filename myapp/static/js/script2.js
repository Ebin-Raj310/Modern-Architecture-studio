const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const usernameError = document.getElementById("usernameError");
const passwordError = document.getElementById("passwordError");
const togglePasswordBtn = document.getElementById("togglePassword");
const rememberMe = document.getElementById("rememberMe");
const loginMessage = document.getElementById("loginMessage");
const forgotPassword = document.getElementById("forgotPassword");
const serverError = document.getElementById("serverError");

const savedUser = localStorage.getItem("architex_saved_user");
if (savedUser && usernameInput) {
    usernameInput.value = savedUser;
    if (rememberMe) rememberMe.checked = true;
}

function clearErrors() {
    if (usernameError) usernameError.textContent = "";
    if (passwordError) passwordError.textContent = "";
    if (loginMessage) loginMessage.textContent = "";
    // keep the space (no display:none) so the page never jumps on mobile
    if (serverError) serverError.style.visibility = "hidden";
}


[usernameInput, passwordInput].forEach(function (inp) {
    if (inp) inp.addEventListener("input", clearErrors);
});

if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener("click", function () {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePasswordBtn.textContent = "Hide";
        } else {
            passwordInput.type = "password";
            togglePasswordBtn.textContent = "Show";
        }
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
        clearErrors();

        const username = usernameInput ? usernameInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value : "";
        let isValid = true;

        if (username === "") {
            if (usernameError) usernameError.textContent = "Please enter your email address.";
            isValid = false;
        } else if (!/^[^@\s]+@[^@\s]+$/.test(username)) {
            if (usernameError) usernameError.textContent = "Enter a valid email address.";
            isValid = false;
        }

        if (password === "") {
            if (passwordError) passwordError.textContent = "Please enter your password.";
            isValid = false;
        } else if (password.length < 8) {
            if (passwordError) passwordError.textContent = "Password must be at least 8 characters.";
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            return;
        }

        if (rememberMe && rememberMe.checked) {
            localStorage.setItem("architex_saved_user", username);
        } else {
            localStorage.removeItem("architex_saved_user");
        }

        if (loginMessage) {
            loginMessage.style.color = "#4ade80";
            loginMessage.textContent = "Signing in...";
        }
    });
}

if (forgotPassword) {
    forgotPassword.addEventListener("click", function (e) {
        e.preventDefault();
        const email = usernameInput ? usernameInput.value.trim() : "";
        if (!email) {
            if (usernameError) usernameError.textContent = "Enter your email above to reset password.";
            if (usernameInput) usernameInput.focus();
        } else {
            alert("Password reset link sent to: " + email);
        }
    });
}


(function () {
    var savedY = 0;
    var guardUntil = 0;
    var html = document.documentElement;

    function rememberInputTap(e) {
        var target = e.target;
        if (!target || !target.closest) return;
        var field = target.closest('input, textarea, select');
        if (!field) {
            var label = target.closest('label');
            field = label && label.control;
        }
        if (!field) return;

        savedY = window.pageYOffset || html.scrollTop || 0;
        guardUntil = Date.now() + 1800;
    }

    if ('PointerEvent' in window) {
        document.addEventListener('pointerdown', rememberInputTap, true);
    } else {
        document.addEventListener('touchstart', rememberInputTap, { capture: true, passive: true });
        document.addEventListener('mousedown', rememberInputTap, true);
    }

    document.addEventListener('focusin', function (e) {
        var target = e.target;
        if (!target || !target.matches || !target.matches('input, textarea, select')) return;
        if (Date.now() >= guardUntil) savedY = window.pageYOffset || html.scrollTop || 0;
        guardUntil = Date.now() + 1800;
    }, true);

    window.addEventListener('scroll', function () {
        if (Date.now() >= guardUntil) return;
        var currentY = window.pageYOffset || html.scrollTop || 0;
        if (Math.abs(currentY - savedY) > 2) {
            var oldScrollBehavior = html.style.scrollBehavior;
            html.style.scrollBehavior = 'auto';
            window.scrollTo(0, savedY);
            html.style.scrollBehavior = oldScrollBehavior;
        }
    }, { passive: true });
})();
