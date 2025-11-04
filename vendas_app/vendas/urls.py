
"""
=============================================================================
ARQUIVO: vendas/urls.py
=============================================================================
Objetivo: Definir as rotas (URLs) da aplicação
Descrição: Aqui mapeamos cada URL para sua respectiva view
=============================================================================
"""

from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    # Autenticação
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('home/', views.home_view, name='home'),

     # Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:pk>/deletar/', views.cliente_delete, name='cliente_delete'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),

    # Produtos
    path('produtos/', views.produtos_list, name='produtos_list'),
    path('produtos/novo/', views.produto_create, name='produto_create'),
    path('produtos/<int:pk>/editar/', views.produto_edit, name='produto_edit'),
    path('produtos/<int:pk>/deletar/', views.produto_delete, name='produto_delete'),
    path('produtos/<int:pk>/', views.produto_detail, name='produto_detail'),
    path('produtos/<int:pk>/ajustar-estoque/', views.produto_ajustar_estoque, name='produto_ajustar_estoque'),

     # Vendas
    path('vendas/', views.vendas_list, name='vendas_list'),
    path('vendas/nova/', views.venda_create, name='venda_create'),
    path('vendas/<int:pk>/', views.venda_detail, name='venda_detail'),
    path('vendas/<int:pk>/deletar/', views.venda_delete, name='venda_delete'),
    path('vendas/<int:pk>/pdf/', views.venda_gerar_pdf, name='venda_gerar_pdf'),

    # Contas a Receber
    path('contas-receber/', views.contas_receber_list, name='contas_receber_list'),
    path('contas-receber/<int:pk>/', views.conta_receber_detail, name='conta_receber_detail'),
    path('contas-receber/<int:pk>/marcar-pago/', views.conta_receber_marcar_pago, name='conta_receber_marcar_pago'),
    path('contas-receber/<int:pk>/marcar-nao-pago/', views.conta_receber_marcar_nao_pago, name='conta_receber_marcar_nao_pago'),

     # Contas a Pagar
    path('contas-pagar/', views.contas_pagar_list, name='contas_pagar_list'),
    path('contas-pagar/nova/', views.conta_pagar_create, name='conta_pagar_create'),
    path('contas-pagar/<int:pk>/', views.conta_pagar_detail, name='conta_pagar_detail'),
    path('contas-pagar/<int:pk>/editar/', views.conta_pagar_edit, name='conta_pagar_edit'),
    path('contas-pagar/<int:pk>/deletar/', views.conta_pagar_delete, name='conta_pagar_delete'),
    path('contas-pagar/<int:pk>/marcar-pago/', views.conta_pagar_marcar_pago, name='conta_pagar_marcar_pago'),
    path('contas-pagar/<int:pk>/marcar-nao-pago/', views.conta_pagar_marcar_nao_pago, name='conta_pagar_marcar_nao_pago'),
]

