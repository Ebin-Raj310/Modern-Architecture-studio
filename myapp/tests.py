from unittest import mock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from myapp.models import Art, Subscriber, EmailLog

class ViewResponseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.admin = User.objects.create_user(username='admin', email='admin@gmail.com', password='adminpassword123')
        self.client = Client()
        self.client.login(username='testuser', password='password123')
        self.anonymous_client = Client()

    def test_home_view_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'ARCHITEX')

    def test_footer_subscribe_sends_subscribed_mail(self):
        from django.core import mail
        response = self.client.post('/subscribe/', {'email': 'reader@example.com'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertIn('Subscribed!', response.json()['message'])
        self.assertTrue(Subscriber.objects.filter(email='reader@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['reader@example.com'])
        self.assertEqual(mail.outbox[0].from_email, 'eraj21504@gmail.com')
        self.assertIn('successfully subscribed', mail.outbox[0].body)
        self.assertIn('text/html', mail.outbox[0].alternatives[0][1])

    def test_home_email_message_sends_thank_you_visit_again(self):
        from django.core import mail
        response = self.client.post('/email-message/', {'email': 'guest@example.com'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['guest@example.com'])
        self.assertEqual(mail.outbox[0].from_email, 'eraj21504@gmail.com')
        self.assertIn('Thank you', mail.outbox[0].body)
        self.assertIn('Visit again', mail.outbox[0].alternatives[0][0])
        # the visit mail does not subscribe the address
        self.assertFalse(Subscriber.objects.filter(email='guest@example.com').exists())

    @mock.patch('myapp.views.EmailMultiAlternatives.send', side_effect=OSError('smtp down'))
    def test_email_message_failure_is_reported_honestly(self, _send):
        response = self.client.post('/email-message/', {'email': 'guest@example.com'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json()['ok'])

    @mock.patch('myapp.views.EmailMultiAlternatives.send', side_effect=OSError('smtp down'))
    def test_subscribe_mail_failure_still_saves_subscriber(self, _send):
        response = self.client.post('/subscribe/', {'email': 'reader@example.com'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIn('could not send', response.json()['message'])
        self.assertTrue(Subscriber.objects.filter(email='reader@example.com').exists())

    def test_invalid_email_rejected_on_both_forms(self):
        for url in ('/subscribe/', '/email-message/'):
            response = self.client.post(url, {'email': 'nope'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response.json()['ok'])

    def test_legacy_home_post_sends_visit_mail(self):
        from django.core import mail
        response = self.client.post('/', {'email': 'old@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you!')
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_login_opens_dashboard_with_email_details(self):
        # a visitor sends an email first
        self.client.post('/email-message/', {'email': 'guest@example.com'},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.client.post('/subscribe/', {'email': 'fan@example.com'},
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        log = EmailLog.objects.get(recipient='guest@example.com')
        self.assertEqual(log.sent_by, self.user)
        self.assertEqual(log.status, 'sent')

        boss = Client()
        response = boss.post('/login/', {'username': 'admin@gmail.com', 'password': 'admin123456789'})
        self.assertRedirects(response, '/admin-dashboard/', fetch_redirect_response=False)
        page = boss.get('/admin-dashboard/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'guest@example.com')
        self.assertContains(page, 'fan@example.com')
        self.assertContains(page, 'test@example.com')  # the visitor who used the forms
        self.assertContains(page, 'Email Message (home page)')

    def test_admin_wrong_password_denied(self):
        response = Client().post('/login/', {'username': 'admin@gmail.com', 'password': 'wrongpassword1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')

    def test_dashboard_blocked_for_normal_visitors(self):
        self.assertEqual(self.client.get('/admin-dashboard/').status_code, 403)
        self.assertEqual(self.anonymous_client.get('/admin-dashboard/').status_code, 302)

    def test_failed_email_is_logged_with_reason(self):
        with mock.patch('myapp.views.EmailMultiAlternatives.send', side_effect=OSError('smtp down')):
            self.client.post('/email-message/', {'email': 'guest@example.com'},
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        log = EmailLog.objects.get(recipient='guest@example.com')
        self.assertEqual(log.status, 'failed')
        self.assertIn('smtp down', log.error)

    def test_about_view(self):
        response = self.client.get('/about.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_project_view(self):
        response = self.client.get('/project.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project.html')

    def test_contact_view_get(self):
        response = self.client.get('/contact.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_view_post_valid(self):
        response = self.client.post('/contact.html/', {
            'name': 'John',
            'lastname': 'Doe',
            'email': 'john@example.com',
            'message': 'Hello ARCHITEX'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finish.html')
        self.assertTrue(Art.objects.filter(email='john@example.com').exists())
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john@example.com')

    def test_finish_view_post(self):
        response = self.client.post('/finish.html/', {
            'name': 'Jane',
            'lastname': 'Smith',
            'email': 'jane@example.com',
            'message': 'Inquiry message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finish.html')
        self.assertTrue(Art.objects.filter(email='jane@example.com').exists())
        self.assertContains(response, 'Jane Smith')

    def test_finish_view_get(self):
        response = self.client.get('/finish.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finish.html')

    def test_login_view_get(self):
        response = self.anonymous_client.get('/login.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_view_get_slash(self):
        response = self.anonymous_client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_view_get_index(self):
        response = self.anonymous_client.get('/index.html/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_any_email_with_8_char_password(self):
        response = self.anonymous_client.post('/login/', {
            'username': 'random.person@gmail.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='random.person@gmail.com').exists())
        self.assertEqual(self.anonymous_client.get('/').status_code, 200)

    def test_login_rejects_short_password(self):
        response = self.anonymous_client.post('/login/', {
            'username': 'someone@gmail.com',
            'password': '1234567'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least 8 characters')

    def test_login_rejects_email_without_at(self):
        response = self.anonymous_client.post('/login/', {
            'username': 'someone.gmail.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid email')

    def test_login_real_account_correct_password(self):
        response = self.anonymous_client.post('/login/', {
            'username': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_staff_account_needs_real_password(self):
        User.objects.create_superuser(username='boss', email='boss@gmail.com', password='realsecret99')
        response = self.anonymous_client.post('/login/', {
            'username': 'boss@gmail.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')
        self.assertEqual(self.anonymous_client.get('/admin/').status_code, 302)

    def test_login_next_cannot_redirect_offsite(self):
        response = self.anonymous_client.post('/login/?next=https://evil.example/', {
            'username': 'visitor@gmail.com',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example', response['Location'])

    def test_navbar_has_no_username_badge(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'user-nav-status')

    def test_logout_view(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)

    def test_detail_project_pages(self):
        detail_pages = ['modern.html', 'coffee.html', 'park.html', 'house.html', 'mall.html', 'tower.html']
        for page in detail_pages:
            response = self.client.get(f'/{page}/')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, page)
