from django.contrib import admin
from .models import Art, Contact, Subscriber, EmailLog

@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lastname', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'lastname', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'created_at')
    search_fields = ('phone',)
    readonly_fields = ('created_at',)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'kind', 'status', 'sent_by', 'created_at')
    list_filter = ('kind', 'status', 'created_at')
    search_fields = ('recipient', 'subject')
    readonly_fields = ('created_at',)
