from django.contrib import admin
from django.urls import path
from learning import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("healthz/", views.healthz, name="healthz"),
    path("api/lesson/", views.lesson_api, name="lesson_api"),
]
