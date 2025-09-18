from django.contrib import admin
from django.urls import path, include
import django_prometheus
from chat.views import HealthView
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/chat/", include("chat.urls")),
    path("", TemplateView.as_view(template_name="index.html")),
    path("wsdemo/", TemplateView.as_view(template_name="wsdemo.html")),  # <= test page
    path("healthz", HealthView.as_view()),
    path("", include("django_prometheus.urls")),  # exposes /metrics
]
