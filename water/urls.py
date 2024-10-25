from django.urls import path, include  
from . import views
from water.views import (
    edit_customer, delete_place, edit_place, place_list, 
    watermeter_list, edit_watermeter, delete_watermeter
)
import debug_toolbar
from django.contrib import admin


urlpatterns = [
    path('update-reading/', views.update_reading, name='update_reading'),  # URL for updating watermeter reading

    path('', views.main_page, name='main_page'),  # Main page with menu

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('customers/delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),
 
    path('places/', place_list, name='place_list'),
    path('places/add/', views.add_place, name='add_place'),
    path('places/edit/<int:place_id>/', edit_place, name='edit_place'),
    path('places/delete/<int:place_id>/', delete_place, name='delete_place'),

    path('watermeters/', watermeter_list, name='watermeter_list'),
    path('watermeters/add/', views.add_watermeter, name='add_watermeter'),
    path('watermeters/edit/<int:watermeter_id>/', edit_watermeter, name='edit_watermeter'),
    path('watermeters/delete/<int:watermeter_id>/', delete_watermeter, name='delete_watermeter'),

    path('watermeters_places/', views.watermeter_place_list, name='watermeter_place_list'), 
    path('watermeters_places/add/', views.add_watermeter_place, name='add_watermeter_place'),
    path('watermeters_places/edit/<int:connection_id>/', views.edit_watermeter_place, name='edit_watermeter_place'),
    path('watermeters_places/delete/<int:connection_id>/', views.delete_watermeter_place, name='delete_watermeter_place'),
    path('watermeter-place/connect/', views.connect_watermeter_place, name='connect_watermeter_place'),       

    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/add-contract/', views.add_contract, name='add_contract'),
    path('contracts/edit/<int:contract_id>/', views.edit_contract, name='edit_contract'),
    path('contracts/delete/<int:contract_id>/', views.delete_contract, name='delete_contract'),
    path('contracts/active/', views.active_contracts, name='contracts_active_list'),
    path('contracts/finish/<int:contract_id>/', views.finish_contract, name='finish_contract'),

    # New URL patterns for VAT, Providers, and Products
    path('vat/', views.vat_list, name='vat_list'),
    path('vat/add/', views.add_vat, name='add_vat'),
    path('vat/edit/<int:pk>/', views.edit_vat, name='edit_vat'),
    path('vat/delete/<int:pk>/', views.delete_vat, name='delete_vat'),

    path('providers/', views.provider_list, name='provider_list'),
    path('providers/add/', views.add_provider, name='add_provider'),
    path('providers/edit/<int:pk>/', views.edit_provider, name='edit_provider'),
    path('providers/delete/<int:pk>/', views.delete_provider, name='delete_provider'),

    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
]

