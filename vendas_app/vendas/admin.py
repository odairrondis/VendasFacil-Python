# from django.contrib import admin

# Register your models here.

"""
=============================================================================
ARQUIVO: vendas/admin.py
=============================================================================
Objetivo: Registrar os modelos no painel administrativo do Django
Descrição: Aqui configuramos como os modelos aparecem no admin
=============================================================================
"""

from django.contrib import admin
from .models import Marca, Product, Client, Sale, SaleItem, AccountsReceivable, AccountsPayable


# =============================================================================
# ADMIN: Marca
# =============================================================================
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Marca.
    """
    list_display = ['nome', 'criada_em']
    search_fields = ['nome']
    ordering = ['nome']


# =============================================================================
# ADMIN: Product
# =============================================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Product.
    """
    list_display = ['nome', 'usuario', 'marca', 'preco', 'estoque', 'ativo', 'criado_em']
    list_filter = ['ativo', 'marca', 'usuario', 'criado_em']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'descricao', 'marca')
        }),
        ('Preço e Estoque', {
            'fields': ('preco', 'estoque')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )


# =============================================================================
# ADMIN: Client
# =============================================================================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Client.
    """
    list_display = ['nome', 'usuario', 'email', 'telefone', 'ativo', 'criado_em']
    list_filter = ['ativo', 'usuario', 'criado_em']
    search_fields = ['nome', 'email', 'telefone', 'cpf_cnpj']
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'email', 'telefone', 'cpf_cnpj')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )


# =============================================================================
# ADMIN: SaleItem (Inline)
# =============================================================================
class SaleItemInline(admin.TabularInline):
    """
    Configuração inline para editar itens de venda dentro da venda.
    """
    model = SaleItem
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['produto', 'quantidade', 'preco_unitario', 'subtotal']


# =============================================================================
# ADMIN: Sale
# =============================================================================
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Sale.
    """
    list_display = ['id', 'usuario', 'cliente', 'valor_total', 'forma_pagamento', 'data_vencimento', 'data_venda']
    list_filter = ['usuario', 'forma_pagamento', 'data_venda']
    search_fields = ['cliente__nome', 'observacoes']
    readonly_fields = ['data_venda', 'criado_em', 'atualizado_em', 'valor_total']
    inlines = [SaleItemInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'cliente', 'data_venda')
        }),
        ('Valores', {
            'fields': ('valor_total',)
        }),
        ('Pagamento', {
            'fields': ('forma_pagamento', 'data_vencimento')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )


# =============================================================================
# ADMIN: AccountsReceivable
# =============================================================================
@admin.register(AccountsReceivable)
class AccountsReceivableAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo AccountsReceivable.
    """
    list_display = ['id', 'usuario', 'cliente', 'valor', 'data_vencimento', 'status', 'criado_em']
    list_filter = ['usuario', 'status', 'data_vencimento']
    search_fields = ['cliente__nome', 'observacoes']
    readonly_fields = ['criado_em', 'venda']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'venda', 'cliente')
        }),
        ('Valores', {
            'fields': ('valor',)
        }),
        ('Datas', {
            'fields': ('data_vencimento', 'data_pagamento')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Data de Criação', {
            'fields': ('criado_em',)
        }),
    )


# =============================================================================
# ADMIN: AccountsPayable
# =============================================================================
@admin.register(AccountsPayable)
class AccountsPayableAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo AccountsPayable.
    """
    list_display = ['id', 'usuario', 'descricao', 'valor', 'data_vencimento', 'status', 'criado_em']
    list_filter = ['usuario', 'status', 'data_vencimento']
    search_fields = ['descricao', 'observacoes']
    readonly_fields = ['criado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'descricao')
        }),
        ('Valores', {
            'fields': ('valor',)
        }),
        ('Datas', {
            'fields': ('data_vencimento', 'data_pagamento')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Data de Criação', {
            'fields': ('criado_em',)
        }),
    )