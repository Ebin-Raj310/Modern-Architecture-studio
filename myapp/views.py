import logging
import re

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import DatabaseError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from myapp.models import Art, Subscriber, EmailLog
from .forms import ArtForm, LoginForm


EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+$')
MIN_PASSWORD_LENGTH = 8

logger = logging.getLogger(__name__)


def login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin_dashboard'))
        return redirect(reverse('home.html'))

    error = None
    if request.method == 'POST':
        email = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')

        if not EMAIL_PATTERN.match(email) or len(email) > 150:
            error = "Please enter a valid email address (it must contain @)."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = "Password must be at least 8 characters."
        else:

            user = authenticate(request, username=email, password=password)
            if user is None:
                existing = User.objects.filter(username=email).first() or \
                    User.objects.filter(email__iexact=email).first()
                if existing is not None:
                    user = authenticate(request, username=existing.username, password=password)


            if user is None:
                protected = User.objects.filter(is_staff=True, email__iexact=email).exists() or \
                    User.objects.filter(is_staff=True, username=email).exists() or \
                    User.objects.filter(is_superuser=True, email__iexact=email).exists()
                if protected:
                    error = "Invalid email or password."
                else:
                    user, created = User.objects.get_or_create(
                        username=email, defaults={'email': email}
                    )
                    if created:
                        user.set_unusable_password()
                        user.save(update_fields=['password'])
                    user.backend = 'django.contrib.auth.backends.ModelBackend'

            if user is not None:
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if user.is_staff:
                    return redirect(reverse('admin_dashboard'))
                next_url = request.GET.get('next') or request.POST.get('next') or ''
                if not url_has_allowed_host_and_scheme(
                        next_url, allowed_hosts={request.get_host()},
                        require_https=request.is_secure()):
                    next_url = reverse('home.html')
                return redirect(next_url)

    form = LoginForm()
    return render(request, "index.html", {'form': form, 'error': error})

def logout_view(request):
    auth_logout(request)
    return redirect(reverse('login'))

@login_required
def home(request):
    if request.method == 'POST':

        return email_message(request)
    return render(request, "home.html")


def _read_email(request):
    """Return (email, error) from the posted form."""
    email = request.POST.get('email', '').strip()
    if not email:
        return None, 'Please enter your email address.'
    try:
        validate_email(email)
    except ValidationError:
        return None, 'Please enter a valid email address.'
    return email, None


def _respond(request, ok, message, status=200):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': ok, 'message': message}, status=status)
    context = {'success': message} if ok else {'error': message}
    return render(request, 'home.html', context, status=status)


def _log_email(request, email, kind, subject, sent, error_text):
    """Keep a record of every email attempt for the admin dashboard."""
    try:
        EmailLog.objects.create(
            recipient=email,
            kind=kind,
            subject=subject,
            status='sent' if sent else 'failed',
            error='' if sent else error_text,
            sent_by=request.user if request.user.is_authenticated else None,
        )
    except Exception:
        logger.exception('Could not write email log')


@require_POST
def email_message(request):
    """Home page "EMAIL MESSAGE" form: sends a thank-you / visit-again mail to the typed address."""
    email, error = _read_email(request)
    if error:
        return _respond(request, False, error, 400)

    subject = 'Thank you for visiting - ARCHITEX Modern Architecture Studio'
    sent, error_text = send_branded_email(
        email,
        subject=subject,
        heading='Thank you! Visit again.',
        lines=[
            'Thank you for visiting ARCHITEX Modern Architecture Studio.',
            'We would love to see you again. Visit again soon to explore our latest projects.',
        ],
    )
    _log_email(request, email, 'message', subject, sent, error_text)
    if sent:
        return _respond(request, True, f'Thank you! A message has been sent to {email}.')
    message = 'We could not send the email right now. Please try again later.'
    if settings.DEBUG and error_text:
        message += f' [{error_text}]'
    return _respond(request, False, message, 502)


@require_POST
def subscribe(request):
    """Footer "Subscribe Now" form (every page): saves the email and sends a "Subscribed" mail."""
    email, error = _read_email(request)
    if error:
        return _respond(request, False, error, 400)

    try:
        Subscriber.objects.get_or_create(email=email.lower())
    except DatabaseError:
        logger.exception('Subscriber table missing - run: python manage.py migrate')
        return _respond(request, False, 'Server setup is incomplete. Please run "python manage.py migrate".', 500)

    subject = 'Subscribed - ARCHITEX Modern Architecture Studio'
    sent, error_text = send_branded_email(
        email,
        subject=subject,
        heading='Subscribed!',
        lines=[
            'You have been successfully subscribed to ARCHITEX Modern Architecture Studio.',
            'You will now receive updates about our latest projects, design ideas and studio news.',
        ],
    )
    _log_email(request, email, 'subscribe', subject, sent, error_text)
    if sent:
        return _respond(request, True, f'Subscribed! A confirmation email has been sent to {email}.')
    message = 'Subscribed! (We could not send the confirmation email right now.)'
    if settings.DEBUG and error_text:
        message = f'Subscribed! Confirmation email failed: {error_text}'
    return _respond(request, True, message)


def send_branded_email(email, subject, heading, lines):
    """Send an ARCHITEX-styled HTML mail.

    Returns (sent, error_text). sent is True only if it was really handed to the mail server.
    """
    text = "Hello,\n\n" + "\n".join(lines) + (
        "\n\nWarm regards,\n"
        "ARCHITEX Modern Architecture Studio\n"
        "123 Architecture Avenue, Tamil Nadu, India\n"
    )
    paragraphs = ''.join(f'<p style="margin:0 0 12px;">{escape(line)}</p>' for line in lines)
    html = (
        '<div style="background:#f4f4f4;padding:24px 0;font-family:Arial,Helvetica,sans-serif;">'
        '<table role="presentation" align="center" width="560" cellpadding="0" cellspacing="0" '
        'style="max-width:560px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;">'
        '<tr><td style="background:#111111;color:#ffffff;padding:22px 28px;font-size:20px;'
        'letter-spacing:2px;font-weight:bold;">ARCHITEX</td></tr>'
        '<tr><td style="padding:28px;color:#222222;font-size:15px;line-height:1.6;">'
        f'<h2 style="margin:0 0 12px;font-size:20px;">{escape(heading)}</h2>'
        '<p style="margin:0 0 12px;">Hello,</p>'
        f'{paragraphs}'
        '<p style="margin:16px 0 0;">Warm regards,<br><strong>ARCHITEX Modern Architecture Studio</strong></p>'
        '</td></tr>'
        '<tr><td style="background:#fafafa;color:#777777;padding:16px 28px;font-size:12px;">'
        '123 Architecture Avenue, Tamil Nadu, India<br>'
        'You received this email because this address was entered on our website.'
        '</td></tr></table></div>'
    )
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        message.attach_alternative(html, 'text/html')
        sent = message.send(fail_silently=False) > 0
        # console backend (no app password yet) only prints to the terminal - not a real delivery
        if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
            return False, 'Gmail app password not set (.env) - mail was only printed in the terminal.'
        return sent, '' if sent else 'Mail server did not accept the message.'
    except Exception as exc:
        logger.exception('Email to %s failed', email)
        return False, f'{type(exc).__name__}: {exc}'[:500]


@login_required
def about(request):
    return render(request, "about.html")

@login_required
def project(request):
    return render(request, "project.html")

@login_required
def contact(request):
    if request.method == 'POST':
        form = ArtForm(request.POST)
        if form.is_valid():
            art_instance = form.save()
            return render(request, "finish.html", {
                'success': 'Thank you! Your message has been received.',
                'response': art_instance
            })
        return render(request, "contact.html", {
            'form': form,
            'error': 'Please check and fill all required fields correctly.'
        })

    myform = ArtForm()
    return render(request, "contact.html", {'form': myform})

@login_required
def finish(request):
    if request.method == 'POST':
        form = ArtForm(request.POST)
        if form.is_valid():
            art_instance = form.save()
            return render(request, "finish.html", {
                'success': 'Thank you! Your message has been received.',
                'response': art_instance
            })
        return render(request, "contact.html", {
            'form': form,
            'error': 'Please check and fill all required fields correctly.'
        })

    return render(request, "finish.html", {
        'success': 'Thank you! Your submission has been processed.'
    })

@login_required
def modern(request):
    return render(request, "modern.html")

@login_required
def coffee(request):
    return render(request, "coffee.html")

@login_required
def park(request):
    return render(request, "park.html")

@login_required
def house(request):
    return render(request, "house.html")

@login_required
def mall(request):
    return render(request, "mall.html")

@login_required
def tower(request):
    return render(request, "tower.html")


@login_required
def admin_dashboard(request):
    """Admin-only overview: who used the site and which emails were sent to whom."""
    if not request.user.is_staff:
        raise PermissionDenied

    try:
        EmailLog.objects.exists()
    except DatabaseError:
        return render(request, 'admin_dashboard.html', {
            'setup_error': 'Database is not up to date. Stop the server and run: python manage.py migrate',
            'visitors': [], 'email_logs': [], 'subscribers': [], 'inquiries': [],
        })

    visitors = (
        User.objects.filter(is_staff=False)
        .annotate(
            emails_total=Count('email_logs'),
            emails_sent=Count('email_logs', filter=Q(email_logs__status='sent')),
        )
        .order_by('-last_login', '-date_joined')
    )
    logs = EmailLog.objects.select_related('sent_by')
    context = {
        'visitors': visitors[:200],
        'visitor_count': visitors.count(),
        'email_logs': logs[:200],
        'emails_total': logs.count(),
        'emails_sent': logs.filter(status='sent').count(),
        'emails_failed': logs.filter(status='failed').count(),
        'subscribers': Subscriber.objects.all()[:200],
        'subscriber_count': Subscriber.objects.count(),
        'inquiries': Art.objects.all()[:200],
        'inquiry_count': Art.objects.count(),
    }
    return render(request, 'admin_dashboard.html', context)
