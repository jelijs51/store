from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.ApiOverview, name="API Overview"),
    path("categories", views.categories_view, name="Categories"),
    path("categories/<int:id>", views.category_view, name="Categories by ID"),
    path("products", views.products_view, name="Products"),
    path("products/<int:id>", views.products_view, name="Product by ID"),
]
