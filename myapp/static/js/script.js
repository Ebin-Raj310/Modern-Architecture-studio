document.addEventListener("DOMContentLoaded", function () {

    var header = document.querySelector('.site-navbar, .div1');
    var menuOpen = false;
    var lastWidth = window.innerWidth;

    function syncBodyPadding() {
        if (header) {
            if (window.innerWidth <= 1024) {
                document.body.style.paddingTop = '';
                return;
            }

            var brandRow = header.querySelector('div:first-child');
            var h = brandRow ? brandRow.getBoundingClientRect().height : header.getBoundingClientRect().height;
            var navPadding = parseFloat(getComputedStyle(header).paddingTop) + parseFloat(getComputedStyle(header).paddingBottom);
            document.body.style.paddingTop = (h + navPadding) + 'px';
        }
    }
    syncBodyPadding();

    if (header) {
        function onScroll() {
            if (window.innerWidth <= 1024) return;
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    var formElem = document.getElementById('myform');
    if (formElem) {
        formElem.addEventListener('submit', function () {
            var submitButton = formElem.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
            }
        });
    }

    var hamburger = document.getElementById('navToggle');
    var nav = document.querySelector('.site-nav-links') || document.querySelector('.aaa');

    if (hamburger && nav) {
        var navHeader = hamburger.closest('header');
        var savedScrollY = 0;

        function openMenu() {
            nav.classList.add('nav-open');
            if (navHeader) navHeader.classList.add('menu-open');
            hamburger.textContent = '\u2715';
            hamburger.setAttribute('aria-expanded', 'true');

            savedScrollY = window.scrollY || window.pageYOffset;
            document.body.classList.add('nav-menu-open');
            menuOpen = true;
            if (navHeader) navHeader.scrollTop = 0;
        }

        function closeMenu() {
            if (!menuOpen) return;

            nav.classList.remove('nav-open');
            if (navHeader) navHeader.classList.remove('menu-open');
            hamburger.textContent = '\u2630';
            hamburger.setAttribute('aria-expanded', 'false');


            document.body.classList.remove('nav-menu-open');
            menuOpen = false;
        }

        hamburger.addEventListener('click', function (e) {
            e.stopPropagation();
            if (nav.classList.contains('nav-open')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        nav.querySelectorAll('a:not(.dropdown-toggle)').forEach(function (link) {
            link.addEventListener('click', function () {
                closeMenu();
            });
        });

        document.addEventListener('click', function (e) {
            if (navHeader && !navHeader.contains(e.target)) {
                closeMenu();
            }
        });

        window.addEventListener('resize', function () {

            if (window.innerWidth === lastWidth) return;
            lastWidth = window.innerWidth;

            if (window.innerWidth > 1024) {
                closeMenu();
            }
            syncBodyPadding();
        }, { passive: true });
    }


    function clearFormMessages(input) {
        var scope = input.closest('.video-form-card, .contact-form-pane, .login-box, .footer-subscribe-col') ||
            input.closest('form') || input.parentElement;
        if (!scope) return;
        scope.querySelectorAll('.error, .invalid-feedback, #mess, .subscribe-msg').forEach(function (el) {
            el.textContent = '';
        });
        scope.querySelectorAll('.alert-danger, .text-danger, .server-error, .errorlist, [role="alert"]').forEach(function (el) {
            el.style.visibility = 'hidden';
        });
    }

    document.querySelectorAll('input, textarea, select').forEach(function (inp) {
        inp.addEventListener('input', function () { clearFormMessages(inp); });
    });


    window.addEventListener('pageshow', function () {
        var f = document.getElementById('myform');
        var b = f && f.querySelector('button[type="submit"]');
        if (b) { b.disabled = false; b.textContent = 'Submit Message'; }
    });


    document.querySelectorAll('form[data-subscribe]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!window.fetch || !window.FormData) return;
            e.preventDefault();

            var btn = form.querySelector('button[type="submit"]');
            var msg = form.querySelector('.subscribe-msg');
            if (!msg) {
                msg = document.createElement('p');
                msg.className = 'subscribe-msg';
                msg.setAttribute('role', 'status');
                form.appendChild(msg);
            }

            form.querySelectorAll('.text-success, .text-danger').forEach(function (el) {
                if (el !== msg) el.style.display = 'none';
            });

            var oldLabel = btn ? btn.textContent : '';
            if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
            msg.className = 'subscribe-msg';
            msg.textContent = '';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            }).then(function (res) {
                return res.json().then(function (data) { return data; });
            }).then(function (data) {
                msg.className = 'subscribe-msg ' + (data.ok ? 'ok' : 'err');
                msg.textContent = data.message;
                if (data.ok) form.reset();
            }).catch(function () {
                msg.className = 'subscribe-msg err';
                msg.textContent = 'Something went wrong. Please try again.';
            }).then(function () {
                if (btn) { btn.disabled = false; btn.textContent = oldLabel; }
            });
        });
    });

});


function login() {
    return true;
}

function submitForm(event) {
    return true;
}


(function () {
    var savedY = 0;
    var guardUntil = 0;
    var userScrolled = false;
    var html = document.documentElement;

    function guardActive() {
        return Date.now() < guardUntil && !userScrolled;
    }

    function rememberInputTap(e) {
        var t = e.target;
        if (!t || !t.closest) return;
        var field = t.closest('input, textarea, select');
        if (!field) {
            var label = t.closest('label');
            field = label && label.control;
        }
        if (!field) return;
        savedY = window.pageYOffset || html.scrollTop || 0;
        userScrolled = false;
        guardUntil = Date.now() + 1500;
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
        if (Date.now() >= guardUntil) {
            savedY = window.pageYOffset || html.scrollTop || 0;
            userScrolled = false;
        }
        // Mobile browsers may adjust page scroll after opening the on-screen keyboard.
        guardUntil = Date.now() + 1800;
    }, true);

    ['wheel', 'keydown'].forEach(function (name) {
        window.addEventListener(name, function () {
            if (Date.now() < guardUntil && name === 'wheel') userScrolled = true;
        }, { passive: true });
    });
    window.addEventListener('keydown', function (e) {
        if (['PageUp', 'PageDown', 'Home', 'End', 'ArrowUp', 'ArrowDown', ' '].indexOf(e.key) !== -1 &&
            !(e.target && e.target.matches && e.target.matches('input, textarea, select'))) {
            userScrolled = true;
        }
    }, { passive: true });

    window.addEventListener('scroll', function () {
        if (!guardActive()) return;
        var y = window.pageYOffset || html.scrollTop || 0;
        if (Math.abs(y - savedY) > 3) {
            var old = html.style.scrollBehavior;
            html.style.scrollBehavior = 'auto';
            window.scrollTo(0, savedY);
            html.style.scrollBehavior = old;
        }
    }, { passive: true });
})();
