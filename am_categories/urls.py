""" am_categories URL Configuration """

from django.urls import path

from categories.viewsets import CategoriesViewSet

urlpatterns = [
    path(
        'categories/',
        CategoriesViewSet.as_view(actions={'post': 'create'})),
    path(
        'categories/<int:pk>/',
        CategoriesViewSet.as_view(actions={'get': 'retrieve'})),
]
