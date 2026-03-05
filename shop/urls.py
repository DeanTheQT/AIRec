from django.urls import path
from .views import recommend_view, add_product, product_list

urlpatterns = [
    path("recommend/", recommend_view, name="recommend"),
    path('add/', add_product, name='add_product'),
    path('list/', product_list, name='product_list'),
]