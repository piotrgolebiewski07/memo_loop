"""
URL configuration for config project.
R
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from words import views
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path("study/", include("words.urls")),
    path('admin/', admin.site.urls),
    path('ready-sets/', views.ready_sets, name="ready_sets"),
    path('my-sets/', views.my_sets, name="my_sets"),
    path('my-sets/create/', views.create_set, name="create_set"),
    path('my-sets/<slug:slug>/', views.my_set_detail, name="my_set_detail"),
    path('accounts/', include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register")
]


