from django.urls import path

from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path("simple_get/", views.my_view, name='simple_get_view'),
]  