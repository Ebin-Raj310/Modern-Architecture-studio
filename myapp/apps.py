from django.apps import AppConfig


def ensure_admin_user(sender, **kwargs):
    """Create / refresh the dashboard admin account from ADMIN_EMAIL + ADMIN_PASSWORD."""
    from django.conf import settings
    from django.contrib.auth import get_user_model

    email = (getattr(settings, 'ADMIN_EMAIL', '') or '').strip().lower()
    password = getattr(settings, 'ADMIN_PASSWORD', '') or ''
    if not email or not password:
        return

    User = get_user_model()
    user = (
        User.objects.filter(username=email).first()
        or User.objects.filter(email__iexact=email, is_staff=True).first()
    )
    if user is None:
        user = User(username=email)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    if not user.pk or not user.check_password(password):
        user.set_password(password)
    user.save()


class MyappConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(ensure_admin_user, sender=self)
