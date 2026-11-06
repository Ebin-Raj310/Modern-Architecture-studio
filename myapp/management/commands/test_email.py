from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send a test email and show the exact reason if it fails. Usage: python manage.py test_email you@example.com"

    def add_arguments(self, parser):
        parser.add_argument('to', help='Email address that should receive the test mail')

    def handle(self, *args, **options):
        self.stdout.write(f"Backend      : {settings.EMAIL_BACKEND}")
        self.stdout.write(f"From (user)  : {settings.EMAIL_HOST_USER or '(empty)'}")
        self.stdout.write(f"Password len : {len(settings.EMAIL_HOST_PASSWORD)} (must be 16 for a Gmail App Password)")
        if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
            self.stdout.write(self.style.WARNING(
                "\n.env was not read or EMAIL_HOST_PASSWORD is empty - mail will only be printed, not sent.\n"
                "Check: file is named .env, sits next to manage.py, and has EMAIL_HOST_PASSWORD=..."))
        try:
            send_mail('ARCHITEX test email', 'If you can read this, email sending works.',
                      settings.DEFAULT_FROM_EMAIL, [options['to']], fail_silently=False)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"\nFAILED: {type(exc).__name__}: {exc}"))
            text = str(exc)
            if '535' in text or 'Authentication' in text or 'Username and Password' in text:
                self.stdout.write("Meaning: wrong App Password. Create a new one at myaccount.google.com/apppasswords")
            elif 'timed out' in text.lower() or 'unreachable' in text.lower() or 'getaddrinfo' in text:
                self.stdout.write("Meaning: no internet or Wi-Fi blocks port 587. Try a mobile hotspot.")
            return
        self.stdout.write(self.style.SUCCESS("\nSent. Check the inbox (and Spam) of " + options['to']))
