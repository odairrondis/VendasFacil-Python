# from django.db import models

# Create your models here.
"""
=============================================================================
ARQUIVO: vendas/models.py
=============================================================================
Objetivo: Definir os modelos (tabelas) do banco de dados
Descrição: Aqui criamos a estrutura de dados da aplicação com isolamento
           total por usuário
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# =============================================================================
# MODELO: Marca
# =============================================================================
class Marca(models.Model):
    """
    Modelo para armazenar marcas de produtos.
    
    Atributos:
        nome (str): Nome da marca
        criada_em (datetime): Data de criação
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome da marca do produto"
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nome']

    def __str__(self):
        return self.nome


# =============================================================================
# MODELO: Product
# =============================================================================
class Product(models.Model):
    """
    Modelo para armazenar produtos.
    Cada produto pertence a um usuário específico (isolamento de dados).
    
    Atributos:
        usuario (User): Usuário proprietário do produto
        nome (str): Nome do produto
        descricao (str): Descrição do produto
        preco (Decimal): Preço unitário
        marca (Marca): Marca do produto
        estoque (int): Quantidade em estoque
        ativo (bool): Se o produto está ativo
        criado_em (datetime): Data de criação
        atualizado_em (datetime): Data da última atualização
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='produtos',
        help_text="Usuário proprietário do produto"
    )
    nome = models.CharField(
        max_length=200,
        help_text="Nome do produto"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição detalhada do produto"
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço unitário do produto"
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        help_text="Marca do produto"
    )
    estoque = models.IntegerField(
        default=0,
        help_text="Quantidade em estoque"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Se o produto está ativo"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-criado_em']
        # Garante que cada usuário não pode ter dois produtos com o mesmo nome
        unique_together = ('usuario', 'nome')

    def __str__(self):
        return f"{self.nome} - {self.marca}"


# =============================================================================
# MODELO: Client
# =============================================================================
class Client(models.Model):
    """
    Modelo para armazenar clientes.
    Cada cliente pertence a um usuário específico (isolamento de dados).
    
    Atributos:
        usuario (User): Usuário proprietário do cliente
        nome (str): Nome do cliente
        email (str): Email do cliente
        telefone (str): Telefone do cliente
        cpf_cnpj (str): CPF ou CNPJ do cliente
        endereco (str): Endereço do cliente
        cidade (str): Cidade
        estado (str): Estado
        cep (str): CEP
        ativo (bool): Se o cliente está ativo
        criado_em (datetime): Data de criação
        atualizado_em (datetime): Data da última atualização
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clientes',
        help_text="Usuário proprietário do cliente"
    )
    nome = models.CharField(
        max_length=200,
        help_text="Nome completo do cliente"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email do cliente"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Telefone do cliente"
    )
    cpf_cnpj = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="CPF ou CNPJ do cliente"
    )
    endereco = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Endereço do cliente"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Cidade do cliente"
    )
    estado = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Estado (UF) do cliente"
    )
    cep = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="CEP do cliente"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Se o cliente está ativo"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-criado_em']
        # Garante que cada usuário não pode ter dois clientes com o mesmo nome
        unique_together = ('usuario', 'nome')

    def __str__(self):
        return self.nome


# =============================================================================
# MODELO: Sale
# =============================================================================
class Sale(models.Model):
    """
    Modelo para armazenar vendas.
    Cada venda pertence a um usuário específico (isolamento de dados).
    
    Atributos:
        usuario (User): Usuário proprietário da venda
        cliente (Client): Cliente da venda
        data_venda (datetime): Data da venda
        valor_total (Decimal): Valor total da venda
        forma_pagamento (str): Forma de pagamento (Dinheiro, Cartão, Boleto, etc)
        data_vencimento (date): Data de vencimento do pagamento
        observacoes (str): Observações sobre a venda
        criado_em (datetime): Data de criação
        atualizado_em (datetime): Data da última atualização
    """
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('boleto', 'Boleto'),
        ('pix', 'PIX'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vendas',
        help_text="Usuário proprietário da venda"
    )
    cliente = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='vendas',
        help_text="Cliente da venda"
    )
    data_venda = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da venda"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Valor total da venda"
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        default='dinheiro',
        help_text="Forma de pagamento"
    )
    data_vencimento = models.DateField(
        help_text="Data de vencimento do pagamento"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre a venda"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome} - R$ {self.valor_total}"

    def calcular_valor_total(self):
        """
        Calcula o valor total da venda somando todos os itens.
        """
        total = sum(item.subtotal for item in self.itens.all())
        self.valor_total = total
        self.save()
        return total


# =============================================================================
# MODELO: SaleItem
# =============================================================================
class SaleItem(models.Model):
    """
    Modelo para armazenar itens de uma venda.
    Cada item representa um produto vendido em uma venda específica.
    
    Atributos:
        venda (Sale): Venda à qual o item pertence
        produto (Product): Produto vendido
        quantidade (int): Quantidade vendida
        preco_unitario (Decimal): Preço unitário no momento da venda
        subtotal (Decimal): Quantidade x Preço unitário
    """
    venda = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='itens',
        help_text="Venda à qual o item pertence"
    )
    produto = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='itens_venda',
        help_text="Produto vendido"
    )
    quantidade = models.IntegerField(
        help_text="Quantidade vendida"
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço unitário no momento da venda"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Subtotal do item (quantidade x preço)"
    )

    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"

    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para calcular o subtotal automaticamente.
        """
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        # Recalcula o valor total da venda
        self.venda.calcular_valor_total()


# =============================================================================
# MODELO: AccountsReceivable
# =============================================================================
class AccountsReceivable(models.Model):
    """
    Modelo para armazenar contas a receber.
    Criado automaticamente quando uma venda é registrada.
    
    Atributos:
        usuario (User): Usuário proprietário
        venda (Sale): Venda relacionada
        cliente (Client): Cliente devedor
        valor (Decimal): Valor a receber
        data_vencimento (date): Data de vencimento
        data_pagamento (date): Data do pagamento (null se não pago)
        status (str): Status (pendente, vencido, pago)
        observacoes (str): Observações
        criado_em (datetime): Data de criação
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('vencido', 'Vencido'),
        ('pago', 'Pago'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contas_receber',
        help_text="Usuário proprietário"
    )
    venda = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='contas_receber_venda',
        help_text="Venda relacionada"
    )
    cliente = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contas_receber',
        help_text="Cliente devedor"
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor a receber"
    )
    data_vencimento = models.DateField(
        help_text="Data de vencimento"
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        help_text="Data do pagamento (preenchido quando pago)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        help_text="Status da conta"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['data_vencimento']

    def __str__(self):
        return f"Conta #{self.id} - {self.cliente.nome} - R$ {self.valor}"

    def atualizar_status(self):
        """
        Atualiza o status automaticamente baseado na data de vencimento.
        """
        if self.status == 'pago':
            return

        hoje = timezone.now().date()
        if self.data_vencimento < hoje:
            self.status = 'vencido'
        else:
            self.status = 'pendente'
        self.save()


# =============================================================================
# MODELO: AccountsPayable
# =============================================================================
class AccountsPayable(models.Model):
    """
    Modelo para armazenar contas a pagar (boletos).
    Registro manual de pagamentos a fazer.
    
    Atributos:
        usuario (User): Usuário proprietário
        descricao (str): Descrição do boleto/pagamento
        valor (Decimal): Valor a pagar
        data_vencimento (date): Data de vencimento
        data_pagamento (date): Data do pagamento (null se não pago)
        status (str): Status (pendente, vencido, pago)
        observacoes (str): Observações
        criado_em (datetime): Data de criação
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('vencido', 'Vencido'),
        ('pago', 'Pago'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contas_pagar',
        help_text="Usuário proprietário"
    )
    descricao = models.CharField(
        max_length=300,
        help_text="Descrição do boleto/pagamento"
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor a pagar"
    )
    data_vencimento = models.DateField(
        help_text="Data de vencimento"
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        help_text="Data do pagamento (preenchido quando pago)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        help_text="Status da conta"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ['data_vencimento']

    def __str__(self):
        return f"Boleto #{self.id} - {self.descricao} - R$ {self.valor}"

    def atualizar_status(self):
        """
        Atualiza o status automaticamente baseado na data de vencimento.
        """
        if self.status == 'pago':
            return

        hoje = timezone.now().date()
        if self.data_vencimento < hoje:
            self.status = 'vencido'
        else:
            self.status = 'pendente'
        self.save()