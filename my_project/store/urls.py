from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.ApiOverview),
    path("categories", views.categories_view),
    path("categories/<int:id>", views.category_by_id_view),
    path("products", views.products_view),
    path("products/<int:id>", views.product_by_id_view),
]
