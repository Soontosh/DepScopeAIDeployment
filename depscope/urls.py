"""
URL configuration for depscope project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from live import views
from live import generate_report
from live import upload_pfp
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.live, name='live'),
    path('oauth_redirect', views.oauth_redirect, name='oauth_redirect'),
    path('account_setup/', views.account_setup, name='account_setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/<str:report_id>', views.report, name='report'),
    path("generate_report/", generate_report.generate_report, name="generate_report"),
    path("upload_pfp/<str:report_id>", upload_pfp.upload_pfp, name="upload_pfp"),
    path('contact/', views.contact, name='contact'),
    path('send-email/', views.send_email, name='send_email'),
    path('newsletter_subscribe/', views.newsletter, name='newsletter'),
    path('generate_samples_endpoint/<str:user_id>/', views.generate_samples_endpoint, name='generate_samples_endpoint'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)