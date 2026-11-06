from django.urls import path
from myapp import views

urlpatterns = [
    path("", views.home, name='read'),
    path("home/", views.home, name='home'),
    path("home.html/", views.home, name='home.html'),
    path("subscribe/", views.subscribe, name='subscribe'),
    path("email-message/", views.email_message, name='email_message'),
    path("login/", views.login, name='login'),
    path("login.html/", views.login, name='login_html'),
    path("index.html/", views.login, name='index.html'),
    path("logout/", views.logout_view, name='logout'),
    path("admin-dashboard/", views.admin_dashboard, name='admin_dashboard'),
    path("about.html/", views.about, name='about.html'),
    path("project.html/", views.project, name='project.html'),
    path("contact.html/", views.contact, name='contact.html'),
    path("finish.html/", views.finish, name='finish.html'),
    path("modern.html/", views.modern, name='modern.html'),
    path("coffee.html/", views.coffee, name='coffee.html'),
    path("park.html/", views.park, name='park.html'),
    path("house.html/", views.house, name='house.html'),
    path("mall.html/", views.mall, name='mall.html'),
    path("tower.html/", views.tower, name='tower.html'),
]