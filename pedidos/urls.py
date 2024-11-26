# pedidos/urls.py

from django.urls import path
from . import views

app_name = 'pedidos'  # Nombre de la aplicación

urlpatterns = [
    path('procesar/', views.procesar_pedido, name='procesar_pedido'),  # Ruta para procesar pedidos
    path('transaction/commit', views.commit_transaction, name='commit_transaction'),
    path('create_transaction/', views.create_transaction, name='create_transaction'),
    path('reporte_pedidos/', views.reporte_pedidos, name='reporte_pedidos'),

  
]