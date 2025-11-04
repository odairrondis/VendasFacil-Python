# from django.shortcuts import render

# Create your views here.

"""
=============================================================================
ARQUIVO: vendas/views.py
=============================================================================
Objetivo: Definir as views (lógica das páginas) da aplicação
Descrição: Aqui processamos as requisições e retornamos as respostas
=============================================================================
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Client, Product, Sale, SaleItem, AccountsReceivable, AccountsPayable, Marca


# =============================================================================
# VIEW: Login
# =============================================================================
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    View para fazer login na aplicação.
    
    GET: Retorna a página de login
    POST: Processa o login do usuário
    
    Contexto:
        - Nenhum contexto especial
    
    Template: login.html
    """
    # Se o usuário já está autenticado, redireciona para home
    if request.user.is_authenticated:
        return redirect('vendas:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        # Validação básica
        if not email or not senha:
            messages.error(request, 'Email e senha são obrigatórios!')
            return render(request, 'vendas/login.html')

        try:
            # Busca o usuário pelo email
            usuario = User.objects.get(email=email)
            # Autentica com o username
            user = authenticate(request, username=usuario.username, password=senha)

            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                return redirect('vendas:home')
            else:
                messages.error(request, 'Email ou senha incorretos!')
        except User.DoesNotExist:
            messages.error(request, 'Email ou senha incorretos!')

    return render(request, 'vendas/login.html')


# =============================================================================
# VIEW: Registro
# =============================================================================
@require_http_methods(["GET", "POST"])
def registro_view(request):
    """
    View para registrar um novo usuário.
    
    GET: Retorna a página de registro
    POST: Cria um novo usuário
    
    Contexto:
        - Nenhum contexto especial
    
    Template: registro.html
    """
    # Se o usuário já está autenticado, redireciona para home
    if request.user.is_authenticated:
        return redirect('vendas:home')

    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()

        # Validações
        if not nome_completo or not email or not senha or not confirmar_senha:
            messages.error(request, 'Todos os campos são obrigatórios!')
            return render(request, 'vendas/registro.html')

        if len(senha) < 6:
            messages.error(request, 'A senha deve ter no mínimo 6 caracteres!')
            return render(request, 'vendas/registro.html')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não conferem!')
            return render(request, 'vendas/registro.html')

        # Verifica se o email já existe
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado!')
            return render(request, 'vendas/registro.html')

        try:
            # Cria o novo usuário
            # O username será gerado a partir do email
            username = email.split('@')[0]
            
            # Se o username já existe, adiciona um número
            contador = 1
            username_original = username
            while User.objects.filter(username=username).exists():
                username = f"{username_original}{contador}"
                contador += 1

            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=nome_completo.split()[0],  # Primeiro nome
                last_name=' '.join(nome_completo.split()[1:]) if len(nome_completo.split()) > 1 else ''
            )

            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('vendas:login')

        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')

    return render(request, 'vendas/registro.html')


# =============================================================================
# VIEW: Logout
# =============================================================================
@login_required(login_url='vendas:login')
def logout_view(request):
    """
    View para fazer logout da aplicação.
    
    Redireciona para a página de login após logout.
    """
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('vendas:login')


# =============================================================================
# VIEW: Home (Dashboard)
# =============================================================================
@login_required(login_url='vendas:login')
def home_view(request):
    """
    View da página inicial (Dashboard).
    Mostra um resumo das informações do usuário.
    
    Contexto:
        - total_clientes: Total de clientes do usuário
        - total_produtos: Total de produtos do usuário
        - total_vendas_mes: Total de vendas do mês atual
        - valor_vendas_mes: Valor total de vendas do mês
        - contas_receber_vencidas: Contas a receber vencidas
        - contas_receber_hoje: Contas a receber que vencem hoje
        - contas_receber_pendentes: Contas a receber pendentes
        - contas_pagar_vencidas: Contas a pagar vencidas
        - contas_pagar_hoje: Contas a pagar que vencem hoje
        - contas_pagar_pendentes: Contas a pagar pendentes
    
    Template: home.html
    """
    usuario = request.user
    hoje = timezone.now().date()

    # Dados do usuário
    total_clientes = Client.objects.filter(usuario=usuario, ativo=True).count()
    total_produtos = Product.objects.filter(usuario=usuario, ativo=True).count()

    # Vendas do mês
    primeiro_dia_mes = hoje.replace(day=1)
    vendas_mes = Sale.objects.filter(
        usuario=usuario,
        data_venda__date__gte=primeiro_dia_mes
    )
    total_vendas_mes = vendas_mes.count()
    valor_vendas_mes = vendas_mes.aggregate(Sum('valor_total'))['valor_total__sum'] or 0

    # Contas a receber
    contas_receber = AccountsReceivable.objects.filter(usuario=usuario)
    
    contas_receber_vencidas = contas_receber.filter(
        status='vencido'
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    contas_receber_hoje = contas_receber.filter(
        data_vencimento=hoje,
        status__in=['pendente', 'vencido']
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    contas_receber_pendentes = contas_receber.filter(
        status='pendente'
    ).count()

    # Contas a pagar
    contas_pagar = AccountsPayable.objects.filter(usuario=usuario)
    
    contas_pagar_vencidas = contas_pagar.filter(
        status='vencido'
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    contas_pagar_hoje = contas_pagar.filter(
        data_vencimento=hoje,
        status__in=['pendente', 'vencido']
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    contas_pagar_pendentes = contas_pagar.filter(
        status='pendente'
    ).count()

    contexto = {
        'total_clientes': total_clientes,
        'total_produtos': total_produtos,
        'total_vendas_mes': total_vendas_mes,
        'valor_vendas_mes': valor_vendas_mes,
        'contas_receber_vencidas': contas_receber_vencidas,
        'contas_receber_hoje': contas_receber_hoje,
        'contas_receber_pendentes': contas_receber_pendentes,
        'contas_pagar_vencidas': contas_pagar_vencidas,
        'contas_pagar_hoje': contas_pagar_hoje,
        'contas_pagar_pendentes': contas_pagar_pendentes,
    }

    return render(request, 'vendas/home.html', contexto)

# =============================================================================
# VIEWS: CLIENTES
# =============================================================================

@login_required(login_url='vendas:login')
def clientes_list(request):
    """
    View para listar todos os clientes do usuário.
    
    GET: Retorna a lista de clientes
    
    Contexto:
        - clientes: Lista de clientes do usuário
        - total_clientes: Total de clientes
    
    Template: clientes/list.html
    """
    usuario = request.user
    
    # Busca todos os clientes do usuário
    clientes = Client.objects.filter(usuario=usuario).order_by('-criado_em')
    
    # Filtro por status (ativo/inativo)
    status = request.GET.get('status', 'ativo')
    if status == 'ativo':
        clientes = clientes.filter(ativo=True)
    elif status == 'inativo':
        clientes = clientes.filter(ativo=False)
    
    # Busca por nome
    busca = request.GET.get('busca', '').strip()
    if busca:
        clientes = clientes.filter(nome__icontains=busca)
    
    contexto = {
        'clientes': clientes,
        'total_clientes': clientes.count(),
        'status_filtro': status,
        'busca': busca,
    }
    
    return render(request, 'vendas/clientes/list.html', contexto)


@login_required(login_url='vendas:login')
def cliente_create(request):
    """
    View para criar um novo cliente.
    
    GET: Retorna o formulário de criação
    POST: Cria um novo cliente
    
    Contexto:
        - Nenhum contexto especial
    
    Template: clientes/form.html
    """
    usuario = request.user
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        cep = request.POST.get('cep', '').strip()
        
        # Validações
        if not nome:
            messages.error(request, 'Nome do cliente é obrigatório!')
            return render(request, 'vendas/clientes/form.html')
        
        # Verifica se já existe um cliente com o mesmo nome
        if Client.objects.filter(usuario=usuario, nome=nome).exists():
            messages.error(request, 'Já existe um cliente com este nome!')
            return render(request, 'vendas/clientes/form.html')
        
        try:
            # Cria o novo cliente
            cliente = Client.objects.create(
                usuario=usuario,
                nome=nome,
                email=email if email else None,
                telefone=telefone if telefone else None,
                cpf_cnpj=cpf_cnpj if cpf_cnpj else None,
                endereco=endereco if endereco else None,
                cidade=cidade if cidade else None,
                estado=estado if estado else None,
                cep=cep if cep else None,
            )
            
            messages.success(request, f'Cliente "{nome}" criado com sucesso!')
            return redirect('vendas:clientes_list')
        
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
    
    return render(request, 'vendas/clientes/form.html')


@login_required(login_url='vendas:login')
def cliente_edit(request, pk):
    """
    View para editar um cliente existente.
    
    GET: Retorna o formulário com dados do cliente
    POST: Atualiza os dados do cliente
    
    Args:
        pk: ID do cliente
    
    Contexto:
        - cliente: Dados do cliente
    
    Template: clientes/form.html
    """
    usuario = request.user
    
    try:
        cliente = Client.objects.get(pk=pk, usuario=usuario)
    except Client.DoesNotExist:
        messages.error(request, 'Cliente não encontrado!')
        return redirect('vendas:clientes_list')
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        cep = request.POST.get('cep', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        # Validações
        if not nome:
            messages.error(request, 'Nome do cliente é obrigatório!')
            contexto = {'cliente': cliente, 'edicao': True}
            return render(request, 'vendas/clientes/form.html', contexto)
        
        # Verifica se já existe outro cliente com o mesmo nome
        if Client.objects.filter(usuario=usuario, nome=nome).exclude(pk=pk).exists():
            messages.error(request, 'Já existe outro cliente com este nome!')
            contexto = {'cliente': cliente, 'edicao': True}
            return render(request, 'vendas/clientes/form.html', contexto)
        
        try:
            # Atualiza o cliente
            cliente.nome = nome
            cliente.email = email if email else None
            cliente.telefone = telefone if telefone else None
            cliente.cpf_cnpj = cpf_cnpj if cpf_cnpj else None
            cliente.endereco = endereco if endereco else None
            cliente.cidade = cidade if cidade else None
            cliente.estado = estado if estado else None
            cliente.cep = cep if cep else None
            cliente.ativo = ativo
            cliente.save()
            
            messages.success(request, f'Cliente "{nome}" atualizado com sucesso!')
            return redirect('vendas:clientes_list')
        
        except Exception as e:
            messages.error(request, f'Erro ao atualizar cliente: {str(e)}')
    
    contexto = {
        'cliente': cliente,
        'edicao': True,
    }
    
    return render(request, 'vendas/clientes/form.html', contexto)


@login_required(login_url='vendas:login')
def cliente_delete(request, pk):
    """
    View para deletar um cliente.
    
    GET: Retorna página de confirmação
    POST: Deleta o cliente
    
    Args:
        pk: ID do cliente
    
    Template: clientes/confirm_delete.html
    """
    usuario = request.user
    
    try:
        cliente = Client.objects.get(pk=pk, usuario=usuario)
    except Client.DoesNotExist:
        messages.error(request, 'Cliente não encontrado!')
        return redirect('vendas:clientes_list')
    
    if request.method == 'POST':
        nome_cliente = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente "{nome_cliente}" deletado com sucesso!')
        return redirect('vendas:clientes_list')
    
    contexto = {
        'cliente': cliente,
    }
    
    return render(request, 'vendas/clientes/confirm_delete.html', contexto)


@login_required(login_url='vendas:login')
def cliente_detail(request, pk):
    """
    View para visualizar detalhes de um cliente.
    
    GET: Retorna os detalhes do cliente
    
    Args:
        pk: ID do cliente
    
    Contexto:
        - cliente: Dados do cliente
        - total_vendas: Total de vendas do cliente
        - valor_total_vendas: Valor total de vendas
        - contas_receber: Contas a receber do cliente
    
    Template: clientes/detail.html
    """
    usuario = request.user
    
    try:
        cliente = Client.objects.get(pk=pk, usuario=usuario)
    except Client.DoesNotExist:
        messages.error(request, 'Cliente não encontrado!')
        return redirect('vendas:clientes_list')
    
    # Dados do cliente
    vendas = Sale.objects.filter(usuario=usuario, cliente=cliente)
    total_vendas = vendas.count()
    valor_total_vendas = vendas.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    # Contas a receber
    contas_receber = AccountsReceivable.objects.filter(
        usuario=usuario,
        cliente=cliente
    ).order_by('-data_vencimento')
    
    contexto = {
        'cliente': cliente,
        'total_vendas': total_vendas,
        'valor_total_vendas': valor_total_vendas,
        'contas_receber': contas_receber,
    }
    
    return render(request, 'vendas/clientes/detail.html', contexto)

# =============================================================================
# VIEWS: PRODUTOS
# =============================================================================

@login_required(login_url='vendas:login')
def produtos_list(request):
    """
    View para listar todos os produtos do usuário.
    
    GET: Retorna a lista de produtos
    
    Contexto:
        - produtos: Lista de produtos do usuário
        - total_produtos: Total de produtos
        - marcas: Lista de marcas para filtro
    
    Template: produtos/list.html
    """
    usuario = request.user
    
    # Busca todos os produtos do usuário
    produtos = Product.objects.filter(usuario=usuario).order_by('-criado_em')
    
    # Filtro por status (ativo/inativo)
    status = request.GET.get('status', 'ativo')
    if status == 'ativo':
        produtos = produtos.filter(ativo=True)
    elif status == 'inativo':
        produtos = produtos.filter(ativo=False)
    
    # Filtro por marca
    marca_id = request.GET.get('marca', '')
    if marca_id:
        produtos = produtos.filter(marca_id=marca_id)
    
    # Busca por nome
    busca = request.GET.get('busca', '').strip()
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )
    
    # Marcas para filtro
    marcas = Marca.objects.all()
    
    contexto = {
        'produtos': produtos,
        'total_produtos': produtos.count(),
        'status_filtro': status,
        'marca_filtro': marca_id,
        'busca': busca,
        'marcas': marcas,
    }
    
    return render(request, 'vendas/produtos/list.html', contexto)


@login_required(login_url='vendas:login')
def produto_create(request):
    """
    View para criar um novo produto.
    
    GET: Retorna o formulário de criação
    POST: Cria um novo produto
    
    Contexto:
        - marcas: Lista de marcas
    
    Template: produtos/form.html
    """
    usuario = request.user
    marcas = Marca.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        preco = request.POST.get('preco', '').strip()
        marca_id = request.POST.get('marca', '')
        estoque = request.POST.get('estoque', '0').strip()
        
        # Validações
        if not nome:
            messages.error(request, 'Nome do produto é obrigatório!')
            contexto = {'marcas': marcas}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        if not preco:
            messages.error(request, 'Preço do produto é obrigatório!')
            contexto = {'marcas': marcas}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        # Verifica se já existe um produto com o mesmo nome
        if Product.objects.filter(usuario=usuario, nome=nome).exists():
            messages.error(request, 'Já existe um produto com este nome!')
            contexto = {'marcas': marcas}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        try:
            # Converte valores
            preco = float(preco.replace(',', '.'))
            estoque = int(estoque) if estoque else 0
            
            # Valida valores
            if preco < 0:
                messages.error(request, 'Preço não pode ser negativo!')
                contexto = {'marcas': marcas}
                return render(request, 'vendas/produtos/form.html', contexto)
            
            if estoque < 0:
                messages.error(request, 'Estoque não pode ser negativo!')
                contexto = {'marcas': marcas}
                return render(request, 'vendas/produtos/form.html', contexto)
            
            # Cria o novo produto
            marca = None
            if marca_id:
                try:
                    marca = Marca.objects.get(id=marca_id)
                except Marca.DoesNotExist:
                    pass
            
            produto = Product.objects.create(
                usuario=usuario,
                nome=nome,
                descricao=descricao if descricao else None,
                preco=preco,
                marca=marca,
                estoque=estoque,
            )
            
            messages.success(request, f'Produto "{nome}" criado com sucesso!')
            return redirect('vendas:produtos_list')
        
        except ValueError:
            messages.error(request, 'Preço e estoque devem ser números válidos!')
        except Exception as e:
            messages.error(request, f'Erro ao criar produto: {str(e)}')
    
    contexto = {'marcas': marcas}
    return render(request, 'vendas/produtos/form.html', contexto)


@login_required(login_url='vendas:login')
def produto_edit(request, pk):
    """
    View para editar um produto existente.
    
    GET: Retorna o formulário com dados do produto
    POST: Atualiza os dados do produto
    
    Args:
        pk: ID do produto
    
    Contexto:
        - produto: Dados do produto
        - marcas: Lista de marcas
    
    Template: produtos/form.html
    """
    usuario = request.user
    marcas = Marca.objects.all()
    
    try:
        produto = Product.objects.get(pk=pk, usuario=usuario)
    except Product.DoesNotExist:
        messages.error(request, 'Produto não encontrado!')
        return redirect('vendas:produtos_list')
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        preco = request.POST.get('preco', '').strip()
        marca_id = request.POST.get('marca', '')
        estoque = request.POST.get('estoque', '0').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        # Validações
        if not nome:
            messages.error(request, 'Nome do produto é obrigatório!')
            contexto = {'produto': produto, 'marcas': marcas, 'edicao': True}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        if not preco:
            messages.error(request, 'Preço do produto é obrigatório!')
            contexto = {'produto': produto, 'marcas': marcas, 'edicao': True}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        # Verifica se já existe outro produto com o mesmo nome
        if Product.objects.filter(usuario=usuario, nome=nome).exclude(pk=pk).exists():
            messages.error(request, 'Já existe outro produto com este nome!')
            contexto = {'produto': produto, 'marcas': marcas, 'edicao': True}
            return render(request, 'vendas/produtos/form.html', contexto)
        
        try:
            # Converte valores
            preco = float(preco.replace(',', '.'))
            estoque = int(estoque) if estoque else 0
            
            # Valida valores
            if preco < 0:
                messages.error(request, 'Preço não pode ser negativo!')
                contexto = {'produto': produto, 'marcas': marcas, 'edicao': True}
                return render(request, 'vendas/produtos/form.html', contexto)
            
            if estoque < 0:
                messages.error(request, 'Estoque não pode ser negativo!')
                contexto = {'produto': produto, 'marcas': marcas, 'edicao': True}
                return render(request, 'vendas/produtos/form.html', contexto)
            
            # Atualiza o produto
            marca = None
            if marca_id:
                try:
                    marca = Marca.objects.get(id=marca_id)
                except Marca.DoesNotExist:
                    pass
            
            produto.nome = nome
            produto.descricao = descricao if descricao else None
            produto.preco = preco
            produto.marca = marca
            produto.estoque = estoque
            produto.ativo = ativo
            produto.save()
            
            messages.success(request, f'Produto "{nome}" atualizado com sucesso!')
            return redirect('vendas:produtos_list')
        
        except ValueError:
            messages.error(request, 'Preço e estoque devem ser números válidos!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar produto: {str(e)}')
    
    contexto = {
        'produto': produto,
        'marcas': marcas,
        'edicao': True,
    }
    
    return render(request, 'vendas/produtos/form.html', contexto)


@login_required(login_url='vendas:login')
def produto_delete(request, pk):
    """
    View para deletar um produto.
    
    GET: Retorna página de confirmação
    POST: Deleta o produto
    
    Args:
        pk: ID do produto
    
    Template: produtos/confirm_delete.html
    """
    usuario = request.user
    
    try:
        produto = Product.objects.get(pk=pk, usuario=usuario)
    except Product.DoesNotExist:
        messages.error(request, 'Produto não encontrado!')
        return redirect('vendas:produtos_list')
    
    if request.method == 'POST':
        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome_produto}" deletado com sucesso!')
        return redirect('vendas:produtos_list')
    
    contexto = {
        'produto': produto,
    }
    
    return render(request, 'vendas/produtos/confirm_delete.html', contexto)


@login_required(login_url='vendas:login')
def produto_detail(request, pk):
    """
    View para visualizar detalhes de um produto.
    
    GET: Retorna os detalhes do produto
    
    Args:
        pk: ID do produto
    
    Contexto:
        - produto: Dados do produto
        - total_vendas: Total de vendas do produto
        - quantidade_vendida: Quantidade total vendida
    
    Template: produtos/detail.html
    """
    usuario = request.user
    
    try:
        produto = Product.objects.get(pk=pk, usuario=usuario)
    except Product.DoesNotExist:
        messages.error(request, 'Produto não encontrado!')
        return redirect('vendas:produtos_list')
    
    # Dados do produto
    itens_venda = SaleItem.objects.filter(produto=produto)
    total_vendas = itens_venda.count()
    quantidade_vendida = itens_venda.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    
    contexto = {
        'produto': produto,
        'total_vendas': total_vendas,
        'quantidade_vendida': quantidade_vendida,
    }
    
    return render(request, 'vendas/produtos/detail.html', contexto)


@login_required(login_url='vendas:login')
def produto_ajustar_estoque(request, pk):
    """
    View para ajustar o estoque de um produto.
    
    GET: Retorna o formulário de ajuste
    POST: Ajusta o estoque
    
    Args:
        pk: ID do produto
    
    Template: produtos/ajustar_estoque.html
    """
    usuario = request.user
    
    try:
        produto = Product.objects.get(pk=pk, usuario=usuario)
    except Product.DoesNotExist:
        messages.error(request, 'Produto não encontrado!')
        return redirect('vendas:produtos_list')
    
    if request.method == 'POST':
        operacao = request.POST.get('operacao', 'adicionar')
        quantidade = request.POST.get('quantidade', '0').strip()
        motivo = request.POST.get('motivo', '').strip()
        
        try:
            quantidade = int(quantidade)
            
            if quantidade <= 0:
                messages.error(request, 'Quantidade deve ser maior que zero!')
                contexto = {'produto': produto}
                return render(request, 'vendas/produtos/ajustar_estoque.html', contexto)
            
            # Ajusta o estoque
            if operacao == 'adicionar':
                produto.estoque += quantidade
                mensagem = f'Adicionado {quantidade} unidade(s) ao estoque'
            else:  # remover
                if produto.estoque < quantidade:
                    messages.error(request, f'Estoque insuficiente! Disponível: {produto.estoque}')
                    contexto = {'produto': produto}
                    return render(request, 'vendas/produtos/ajustar_estoque.html', contexto)
                
                produto.estoque -= quantidade
                mensagem = f'Removido {quantidade} unidade(s) do estoque'
            
            produto.save()
            
            if motivo:
                mensagem += f' - Motivo: {motivo}'
            
            messages.success(request, mensagem)
            return redirect('vendas:produto_detail', pk=pk)
        
        except ValueError:
            messages.error(request, 'Quantidade deve ser um número válido!')
        except Exception as e:
            messages.error(request, f'Erro ao ajustar estoque: {str(e)}')
    
    contexto = {
        'produto': produto,
    }
    
    return render(request, 'vendas/produtos/ajustar_estoque.html', contexto)

# =============================================================================
# VIEWS: VENDAS
# =============================================================================

@login_required(login_url='vendas:login')
def vendas_list(request):
    """
    View para listar todas as vendas do usuário.
    
    GET: Retorna a lista de vendas
    
    Contexto:
        - vendas: Lista de vendas do usuário
        - total_vendas: Total de vendas
        - valor_total: Valor total de todas as vendas
    
    Template: vendas/list.html
    """
    usuario = request.user
    
    # Busca todas as vendas do usuário
    vendas = Sale.objects.filter(usuario=usuario).order_by('-data_venda')
    
    # Filtro por cliente
    cliente_id = request.GET.get('cliente', '')
    if cliente_id:
        vendas = vendas.filter(cliente_id=cliente_id)
    
    # Filtro por forma de pagamento
    forma_pagamento = request.GET.get('forma_pagamento', '')
    if forma_pagamento:
        vendas = vendas.filter(forma_pagamento=forma_pagamento)
    
    # Busca por período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if data_inicio:
        try:
            data_inicio_obj = timezone.datetime.strptime(data_inicio, '%Y-%m-%d').date()
            vendas = vendas.filter(data_venda__date__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            data_fim_obj = timezone.datetime.strptime(data_fim, '%Y-%m-%d').date()
            vendas = vendas.filter(data_venda__date__lte=data_fim_obj)
        except:
            pass
    
    # Clientes para filtro
    clientes = Client.objects.filter(usuario=usuario, ativo=True)
    
    # Totais
    total_vendas = vendas.count()
    valor_total = vendas.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    contexto = {
        'vendas': vendas,
        'total_vendas': total_vendas,
        'valor_total': valor_total,
        'cliente_filtro': cliente_id,
        'forma_pagamento_filtro': forma_pagamento,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'clientes': clientes,
        'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES,
    }
    
    return render(request, 'vendas/vendas/list.html', contexto)


@login_required(login_url='vendas:login')
def venda_create(request):
    """
    View para criar uma nova venda.
    
    GET: Retorna o formulário de criação
    POST: Cria uma nova venda com itens
    
    Contexto:
        - clientes: Lista de clientes
        - produtos: Lista de produtos
    
    Template: vendas/form.html
    """
    usuario = request.user
    clientes = Client.objects.filter(usuario=usuario, ativo=True)
    produtos = Product.objects.filter(usuario=usuario, ativo=True)
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente', '')
        forma_pagamento = request.POST.get('forma_pagamento', 'dinheiro')
        data_vencimento = request.POST.get('data_vencimento', '')
        parcelas = request.POST.get('parcelas', '1')
        observacoes = request.POST.get('observacoes', '').strip()
        
        # Validações
        if not cliente_id:
            messages.error(request, 'Cliente é obrigatório!')
            contexto = {'clientes': clientes, 'produtos': produtos, 'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES}
            return render(request, 'vendas/vendas/form.html', contexto)
        
        if not data_vencimento:
            messages.error(request, 'Data de vencimento é obrigatória!')
            contexto = {'clientes': clientes, 'produtos': produtos, 'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES}
            return render(request, 'vendas/vendas/form.html', contexto)
        
        try:
            cliente = Client.objects.get(id=cliente_id, usuario=usuario)
        except Client.DoesNotExist:
            messages.error(request, 'Cliente não encontrado!')
            contexto = {'clientes': clientes, 'produtos': produtos, 'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES}
            return render(request, 'vendas/vendas/form.html', contexto)
        
        try:
            # Converte data de vencimento
            data_vencimento_obj = timezone.datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            
            # Converte parcelas
            parcelas = int(parcelas) if parcelas else 1
            if parcelas < 1:
                parcelas = 1
            
            # Cria a venda
            venda = Sale.objects.create(
                usuario=usuario,
                cliente=cliente,
                forma_pagamento=forma_pagamento,
                data_vencimento=data_vencimento_obj,
                observacoes=observacoes if observacoes else None,
            )
            
            # Processa os itens da venda
            produtos_ids = request.POST.getlist('produto_id[]')
            quantidades = request.POST.getlist('quantidade[]')
            precos = request.POST.getlist('preco[]')
            
            if not produtos_ids:
                venda.delete()
                messages.error(request, 'Adicione pelo menos um produto à venda!')
                contexto = {'clientes': clientes, 'produtos': produtos, 'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES}
                return render(request, 'vendas/vendas/form.html', contexto)
            
            # Cria os itens da venda
            for produto_id, quantidade, preco in zip(produtos_ids, quantidades, precos):
                if not produto_id or not quantidade or not preco:
                    continue
                
                try:
                    produto = Product.objects.get(id=produto_id, usuario=usuario)
                    quantidade = int(quantidade)
                    preco = float(preco.replace(',', '.'))
                    
                    if quantidade <= 0:
                        continue
                    
                    if preco < 0:
                        continue
                    
                    # Cria o item da venda
                    SaleItem.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=preco,
                    )
                
                except (Product.DoesNotExist, ValueError):
                    continue
            
            # Recalcula o valor total da venda
            venda.calcular_valor_total()
            
            # Cria as contas a receber (uma por parcela)
            valor_parcela = venda.valor_total / parcelas
            
            for i in range(parcelas):
                # Calcula a data de vencimento para cada parcela
                # Adiciona i meses à data de vencimento
                mes_vencimento = data_vencimento_obj.month + i
                ano_vencimento = data_vencimento_obj.year
                
                # Ajusta o ano se o mês ultrapassar 12
                while mes_vencimento > 12:
                    mes_vencimento -= 12
                    ano_vencimento += 1
                
                # Cria a data de vencimento da parcela
                try:
                    data_parcela = data_vencimento_obj.replace(
                        month=mes_vencimento,
                        year=ano_vencimento
                    )
                except ValueError:
                    # Se o dia não existe no mês (ex: 31 de fevereiro)
                    # usa o último dia do mês
                    from calendar import monthrange
                    ultimo_dia = monthrange(ano_vencimento, mes_vencimento)[1]
                    data_parcela = data_vencimento_obj.replace(
                        month=mes_vencimento,
                        year=ano_vencimento,
                        day=ultimo_dia
                    )
                
                # Cria a conta a receber
                AccountsReceivable.objects.create(
                    usuario=usuario,
                    venda=venda,
                    cliente=cliente,
                    valor=valor_parcela,
                    data_vencimento=data_parcela,
                    observacoes=f'Parcela {i+1} de {parcelas}' if parcelas > 1 else None,
                )
            
            messages.success(request, f'Venda #{venda.id} criada com sucesso! {parcelas} parcela(s) gerada(s).')
            return redirect('vendas:venda_detail', pk=venda.pk)
        
        except Exception as e:
            messages.error(request, f'Erro ao criar venda: {str(e)}')
    
    contexto = {
        'clientes': clientes,
        'produtos': produtos,
        'formas_pagamento': Sale.FORMA_PAGAMENTO_CHOICES,
    }
    
    return render(request, 'vendas/vendas/form.html', contexto)
@login_required(login_url='vendas:login')
def venda_detail(request, pk):
    """
    View para visualizar detalhes de uma venda.
    
    GET: Retorna os detalhes da venda
    
    Args:
        pk: ID da venda
    
    Contexto:
        - venda: Dados da venda
        - itens: Itens da venda
        - contas_receber: Contas a receber relacionadas
    
    Template: vendas/detail.html
    """
    usuario = request.user
    
    try:
        venda = Sale.objects.get(pk=pk, usuario=usuario)
    except Sale.DoesNotExist:
        messages.error(request, 'Venda não encontrada!')
        return redirect('vendas:vendas_list')
    
    # Itens da venda
    itens = SaleItem.objects.filter(venda=venda)
    
    # Contas a receber (pode haver múltiplas por parcelamento)
    contas_receber = AccountsReceivable.objects.filter(venda=venda).order_by('data_vencimento')
    
    contexto = {
        'venda': venda,
        'itens': itens,
        'contas_receber': contas_receber,
    }
    
    return render(request, 'vendas/vendas/detail.html', contexto)


@login_required(login_url='vendas:login')
def venda_delete(request, pk):
    """
    View para deletar uma venda.
    
    GET: Retorna página de confirmação
    POST: Deleta a venda
    
    Args:
        pk: ID da venda
    
    Template: vendas/confirm_delete.html
    """
    usuario = request.user
    
    try:
        venda = Sale.objects.get(pk=pk, usuario=usuario)
    except Sale.DoesNotExist:
        messages.error(request, 'Venda não encontrada!')
        return redirect('vendas:vendas_list')
    
    if request.method == 'POST':
        venda_id = venda.id
        venda.delete()
        messages.success(request, f'Venda #{venda_id} deletada com sucesso!')
        return redirect('vendas:vendas_list')
    
    contexto = {
        'venda': venda,
    }
    
    return render(request, 'vendas/vendas/confirm_delete.html', contexto)

# =============================================================================
# FUNÇÃO: Gerar PDF da Venda
# =============================================================================

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime


@login_required(login_url='vendas:login')
def venda_gerar_pdf(request, pk):
    """
    View para gerar PDF da venda.
    
    GET: Gera e retorna o PDF da venda
    
    Args:
        pk: ID da venda
    
    Returns:
        PDF da venda para download
    """
    usuario = request.user
    
    try:
        venda = Sale.objects.get(pk=pk, usuario=usuario)
    except Sale.DoesNotExist:
        messages.error(request, 'Venda não encontrado!')
        return redirect('vendas:vendas_list')
    
    # Itens da venda
    itens = SaleItem.objects.filter(venda=venda)
    
    # Contas a receber
    contas_receber = AccountsReceivable.objects.filter(venda=venda).order_by('data_vencimento')
    
    # Cria o PDF em memória
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5,
    )
    
    # Título
    elements.append(Paragraph('RECIBO DE VENDA', title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Informações da empresa (usuário)
    empresa_info = f"""
    <b>Vendedor:</b> {usuario.first_name or usuario.username}<br/>
    <b>Email:</b> {usuario.email}<br/>
    <b>Data:</b> {venda.data_venda.strftime('%d/%m/%Y %H:%M')}<br/>
    """
    elements.append(Paragraph(empresa_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Informações do cliente
    elements.append(Paragraph('<b>DADOS DO CLIENTE</b>', heading_style))
    cliente_info = f"""
    <b>Nome:</b> {venda.cliente.nome}<br/>
    <b>Email:</b> {venda.cliente.email or '-'}<br/>
    <b>Telefone:</b> {venda.cliente.telefone or '-'}<br/>
    <b>CPF/CNPJ:</b> {venda.cliente.cpf_cnpj or '-'}<br/>
    <b>Endereço:</b> {venda.cliente.endereco or '-'}<br/>
    """
    elements.append(Paragraph(cliente_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Tabela de produtos
    elements.append(Paragraph('<b>PRODUTOS</b>', heading_style))
    
    # Dados da tabela
    data = [
        ['Produto', 'Quantidade', 'Preço Unit.', 'Subtotal']
    ]
    
    for item in itens:
        data.append([
            item.produto.nome,
            str(item.quantidade),
            f'R$ {item.preco_unitario:.2f}',
            f'R$ {item.subtotal:.2f}'
        ])
    
    # Adiciona linha de total
    data.append([
        '',
        '',
        '<b>TOTAL:</b>',
        f'<b>R$ {venda.valor_total:.2f}</b>'
    ])
    
    # Cria a tabela
    table = Table(data, colWidths=[3 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Informações de pagamento
    elements.append(Paragraph('<b>INFORMAÇÕES DE PAGAMENTO</b>', heading_style))
    pagamento_info = f"""
    <b>Forma de Pagamento:</b> {venda.get_forma_pagamento_display()}<br/>
    """
    
    if venda.observacoes:
        pagamento_info += f"<b>Observações:</b> {venda.observacoes}<br/>"
    
    elements.append(Paragraph(pagamento_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Tabela de parcelas
    if contas_receber.count() > 0:
        elements.append(Paragraph('<b>PARCELAS</b>', heading_style))
        
        parcelas_data = [
            ['Parcela', 'Valor', 'Vencimento']
        ]
        
        for idx, conta in enumerate(contas_receber, 1):
            parcelas_data.append([
                f'Parcela {idx}' if contas_receber.count() > 1 else 'Única',
                f'R$ {conta.valor:.2f}',
                conta.data_vencimento.strftime('%d/%m/%Y')
            ])
        
        parcelas_table = Table(parcelas_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        parcelas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(parcelas_table)
        elements.append(Spacer(1, 0.3 * inch))
    
    # Rodapé
    rodape = """
    <i>Este é um recibo de venda. Guarde para sua segurança.<br/>
    Gerado automaticamente pelo sistema Vendas App</i>
    """
    elements.append(Paragraph(rodape, ParagraphStyle(
        'Rodape',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )))
    
    # Constrói o PDF
    doc.build(elements)
    
    # Retorna o PDF
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="venda_{venda.id}.pdf"'
    
    return response
    
    # Cria a tabela
    table = Table(data, colWidths=[3 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Informações de pagamento
    elements.append(Paragraph('<b>INFORMAÇÕES DE PAGAMENTO</b>', heading_style))
    pagamento_info = f"""
    <b>Forma de Pagamento:</b> {venda.get_forma_pagamento_display()}<br/>
    <b>Data de Vencimento:</b> {venda.data_vencimento.strftime('%d/%m/%Y')}<br/>
    """
    
    if venda.observacoes:
        pagamento_info += f"<b>Observações:</b> {venda.observacoes}<br/>"
    
    elements.append(Paragraph(pagamento_info, normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Rodapé
    rodape = """
    <i>Este é um recibo de venda. Guarde para sua segurança.<br/>
    Gerado automaticamente pelo sistema Vendas App</i>
    """
    elements.append(Paragraph(rodape, ParagraphStyle(
        'Rodape',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )))
    
    # Constrói o PDF
    doc.build(elements)
    
    # Retorna o PDF
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="venda_{venda.id}.pdf"'
    
    return response

# =============================================================================
# VIEWS: CONTAS A RECEBER
# =============================================================================

@login_required(login_url='vendas:login')
def contas_receber_list(request):
    """
    View para listar todas as contas a receber do usuário.
    
    GET: Retorna a lista de contas a receber
    
    Contexto:
        - contas_receber: Lista de contas a receber
        - total_contas: Total de contas
        - valor_total: Valor total a receber
        - status_filtro: Status selecionado
    
    Template: contas_receber/list.html
    """
    usuario = request.user
    
    # Busca todas as contas a receber do usuário
    contas = AccountsReceivable.objects.filter(usuario=usuario).order_by('-data_vencimento')
    
    # Atualiza o status de todas as contas
    hoje = timezone.now().date()
    for conta in contas:
        conta.atualizar_status()
    
    # Filtro por status
    status = request.GET.get('status', 'pendente')
    if status in ['pendente', 'vencido', 'pago']:
        contas = contas.filter(status=status)
    elif status == 'todos':
        pass  # Sem filtro
    else:
        contas = contas.filter(status='pendente')
        status = 'pendente'
    
    # Filtro por cliente
    cliente_id = request.GET.get('cliente', '')
    if cliente_id:
        contas = contas.filter(cliente_id=cliente_id)
    
    # Busca por período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if data_inicio:
        try:
            data_inicio_obj = timezone.datetime.strptime(data_inicio, '%Y-%m-%d').date()
            contas = contas.filter(data_vencimento__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            data_fim_obj = timezone.datetime.strptime(data_fim, '%Y-%m-%d').date()
            contas = contas.filter(data_vencimento__lte=data_fim_obj)
        except:
            pass
    
    # Clientes para filtro
    clientes = Client.objects.filter(usuario=usuario, ativo=True)
    
    # Totais
    total_contas = contas.count()
    valor_total = contas.aggregate(Sum('valor'))['valor__sum'] or 0
    
    # Resumo por status
    contas_pendentes = AccountsReceivable.objects.filter(usuario=usuario, status='pendente').aggregate(Sum('valor'))['valor__sum'] or 0
    contas_vencidas = AccountsReceivable.objects.filter(usuario=usuario, status='vencido').aggregate(Sum('valor'))['valor__sum'] or 0
    contas_pagas = AccountsReceivable.objects.filter(usuario=usuario, status='pago').aggregate(Sum('valor'))['valor__sum'] or 0
    
    contexto = {
        'contas_receber': contas,
        'total_contas': total_contas,
        'valor_total': valor_total,
        'status_filtro': status,
        'cliente_filtro': cliente_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'clientes': clientes,
        'contas_pendentes': contas_pendentes,
        'contas_vencidas': contas_vencidas,
        'contas_pagas': contas_pagas,
    }
    
    return render(request, 'vendas/contas_receber/list.html', contexto)


@login_required(login_url='vendas:login')
def conta_receber_detail(request, pk):
    """
    View para visualizar detalhes de uma conta a receber.
    
    GET: Retorna os detalhes da conta
    
    Args:
        pk: ID da conta a receber
    
    Contexto:
        - conta: Dados da conta
        - venda: Dados da venda relacionada
        - itens: Itens da venda
    
    Template: contas_receber/detail.html
    """
    usuario = request.user
    
    try:
        conta = AccountsReceivable.objects.get(pk=pk, usuario=usuario)
    except AccountsReceivable.DoesNotExist:
        messages.error(request, 'Conta a receber não encontrada!')
        return redirect('vendas:contas_receber_list')
    
    # Atualiza o status
    conta.atualizar_status()
    
    # Venda relacionada
    venda = conta.venda
    itens = SaleItem.objects.filter(venda=venda)
    
    contexto = {
        'conta': conta,
        'venda': venda,
        'itens': itens,
    }
    
    return render(request, 'vendas/contas_receber/detail.html', contexto)


@login_required(login_url='vendas:login')
def conta_receber_marcar_pago(request, pk):
    """
    View para marcar uma conta a receber como pago.
    
    GET: Retorna página de confirmação
    POST: Marca como pago
    
    Args:
        pk: ID da conta a receber
    
    Template: contas_receber/marcar_pago.html
    """
    usuario = request.user
    
    try:
        conta = AccountsReceivable.objects.get(pk=pk, usuario=usuario)
    except AccountsReceivable.DoesNotExist:
        messages.error(request, 'Conta a receber não encontrada!')
        return redirect('vendas:contas_receber_list')
    
    if request.method == 'POST':
        data_pagamento = request.POST.get('data_pagamento', '')
        
        if not data_pagamento:
            messages.error(request, 'Data de pagamento é obrigatória!')
            contexto = {'conta': conta}
            return render(request, 'vendas/contas_receber/marcar_pago.html', contexto)
        
        try:
            data_pagamento_obj = timezone.datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            
            conta.data_pagamento = data_pagamento_obj
            conta.status = 'pago'
            conta.save()
            
            messages.success(request, f'Conta #{conta.id} marcada como paga!')
            return redirect('vendas:conta_receber_detail', pk=pk)
        
        except Exception as e:
            messages.error(request, f'Erro ao marcar como pago: {str(e)}')
    
    contexto = {
        'conta': conta,
    }
    
    return render(request, 'vendas/contas_receber/marcar_pago.html', contexto)


@login_required(login_url='vendas:login')
def conta_receber_marcar_nao_pago(request, pk):
    """
    View para marcar uma conta a receber como não pago.
    
    Args:
        pk: ID da conta a receber
    """
    usuario = request.user
    
    try:
        conta = AccountsReceivable.objects.get(pk=pk, usuario=usuario)
    except AccountsReceivable.DoesNotExist:
        messages.error(request, 'Conta a receber não encontrada!')
        return redirect('vendas:contas_receber_list')
    
    conta.data_pagamento = None
    conta.status = 'pendente'
    conta.save()
    
    messages.success(request, f'Conta #{conta.id} marcada como não paga!')
    return redirect('vendas:conta_receber_detail', pk=pk)

# =============================================================================
# VIEWS: CONTAS A PAGAR
# =============================================================================

@login_required(login_url='vendas:login')
def contas_pagar_list(request):
    """
    View para listar todas as contas a pagar do usuário.
    
    GET: Retorna a lista de contas a pagar
    
    Contexto:
        - contas_pagar: Lista de contas a pagar
        - total_contas: Total de contas
        - valor_total: Valor total a pagar
        - status_filtro: Status selecionado
    
    Template: contas_pagar/list.html
    """
    usuario = request.user
    
    # Busca todas as contas a pagar do usuário
    contas = AccountsPayable.objects.filter(usuario=usuario).order_by('-data_vencimento')
    
    # Atualiza o status de todas as contas
    hoje = timezone.now().date()
    for conta in contas:
        conta.atualizar_status()
    
    # Filtro por status
    status = request.GET.get('status', 'pendente')
    if status in ['pendente', 'vencido', 'pago']:
        contas = contas.filter(status=status)
    elif status == 'todos':
        pass  # Sem filtro
    else:
        contas = contas.filter(status='pendente')
        status = 'pendente'
    
    # Busca por descrição
    busca = request.GET.get('busca', '').strip()
    if busca:
        contas = contas.filter(descricao__icontains=busca)
    
    # Busca por período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if data_inicio:
        try:
            data_inicio_obj = timezone.datetime.strptime(data_inicio, '%Y-%m-%d').date()
            contas = contas.filter(data_vencimento__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            data_fim_obj = timezone.datetime.strptime(data_fim, '%Y-%m-%d').date()
            contas = contas.filter(data_vencimento__lte=data_fim_obj)
        except:
            pass
    
    # Totais
    total_contas = contas.count()
    valor_total = contas.aggregate(Sum('valor'))['valor__sum'] or 0
    
    # Resumo por status
    contas_pendentes = AccountsPayable.objects.filter(usuario=usuario, status='pendente').aggregate(Sum('valor'))['valor__sum'] or 0
    contas_vencidas = AccountsPayable.objects.filter(usuario=usuario, status='vencido').aggregate(Sum('valor'))['valor__sum'] or 0
    contas_pagas = AccountsPayable.objects.filter(usuario=usuario, status='pago').aggregate(Sum('valor'))['valor__sum'] or 0
    
    contexto = {
        'contas_pagar': contas,
        'total_contas': total_contas,
        'valor_total': valor_total,
        'status_filtro': status,
        'busca': busca,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'contas_pendentes': contas_pendentes,
        'contas_vencidas': contas_vencidas,
        'contas_pagas': contas_pagas,
    }
    
    return render(request, 'vendas/contas_pagar/list.html', contexto)


@login_required(login_url='vendas:login')
def conta_pagar_create(request):
    """
    View para criar uma nova conta a pagar.
    
    GET: Retorna o formulário de criação
    POST: Cria uma nova conta a pagar
    
    Template: contas_pagar/form.html
    """
    usuario = request.user
    
    if request.method == 'POST':
        descricao = request.POST.get('descricao', '').strip()
        valor = request.POST.get('valor', '').strip()
        data_vencimento = request.POST.get('data_vencimento', '')
        observacoes = request.POST.get('observacoes', '').strip()
        
        # Validações
        if not descricao:
            messages.error(request, 'Descrição é obrigatória!')
            return render(request, 'vendas/contas_pagar/form.html')
        
        if not valor:
            messages.error(request, 'Valor é obrigatório!')
            return render(request, 'vendas/contas_pagar/form.html')
        
        if not data_vencimento:
            messages.error(request, 'Data de vencimento é obrigatória!')
            return render(request, 'vendas/contas_pagar/form.html')
        
        try:
            # Converte valores
            valor = float(valor.replace(',', '.'))
            data_vencimento_obj = timezone.datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            
            # Valida valores
            if valor <= 0:
                messages.error(request, 'Valor deve ser maior que zero!')
                return render(request, 'vendas/contas_pagar/form.html')
            
            # Cria a conta a pagar
            conta = AccountsPayable.objects.create(
                usuario=usuario,
                descricao=descricao,
                valor=valor,
                data_vencimento=data_vencimento_obj,
                observacoes=observacoes if observacoes else None,
            )
            
            messages.success(request, f'Conta a pagar "{descricao}" criada com sucesso!')
            return redirect('vendas:contas_pagar_list')
        
        except ValueError:
            messages.error(request, 'Valor deve ser um número válido!')
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'vendas/contas_pagar/form.html')


@login_required(login_url='vendas:login')
def conta_pagar_edit(request, pk):
    """
    View para editar uma conta a pagar existente.
    
    GET: Retorna o formulário com dados da conta
    POST: Atualiza os dados da conta
    
    Args:
        pk: ID da conta a pagar
    
    Template: contas_pagar/form.html
    """
    usuario = request.user
    
    try:
        conta = AccountsPayable.objects.get(pk=pk, usuario=usuario)
    except AccountsPayable.DoesNotExist:
        messages.error(request, 'Conta a pagar não encontrada!')
        return redirect('vendas:contas_pagar_list')
    
    if request.method == 'POST':
        descricao = request.POST.get('descricao', '').strip()
        valor = request.POST.get('valor', '').strip()
        data_vencimento = request.POST.get('data_vencimento', '')
        observacoes = request.POST.get('observacoes', '').strip()
        
        # Validações
        if not descricao:
            messages.error(request, 'Descrição é obrigatória!')
            contexto = {'conta': conta, 'edicao': True}
            return render(request, 'vendas/contas_pagar/form.html', contexto)
        
        if not valor:
            messages.error(request, 'Valor é obrigatório!')
            contexto = {'conta': conta, 'edicao': True}
            return render(request, 'vendas/contas_pagar/form.html', contexto)
        
        if not data_vencimento:
            messages.error(request, 'Data de vencimento é obrigatória!')
            contexto = {'conta': conta, 'edicao': True}
            return render(request, 'vendas/contas_pagar/form.html', contexto)
        
        try:
            # Converte valores
            valor = float(valor.replace(',', '.'))
            data_vencimento_obj = timezone.datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            
            # Valida valores
            if valor <= 0:
                messages.error(request, 'Valor deve ser maior que zero!')
                contexto = {'conta': conta, 'edicao': True}
                return render(request, 'vendas/contas_pagar/form.html', contexto)
            
            # Atualiza a conta
            conta.descricao = descricao
            conta.valor = valor
            conta.data_vencimento = data_vencimento_obj
            conta.observacoes = observacoes if observacoes else None
            conta.save()
            
            messages.success(request, f'Conta a pagar "{descricao}" atualizada com sucesso!')
            return redirect('vendas:contas_pagar_list')
        
        except ValueError:
            messages.error(request, 'Valor deve ser um número válido!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar conta: {str(e)}')
    
    contexto = {
        'conta': conta,
        'edicao': True,
    }
    
    return render(request, 'vendas/contas_pagar/form.html', contexto)


@login_required(login_url='vendas:login')
def conta_pagar_delete(request, pk):
    """
    View para deletar uma conta a pagar.
    
    GET: Retorna página de confirmação
    POST: Deleta a conta
    
    Args:
        pk: ID da conta a pagar
    
    Template: contas_pagar/confirm_delete.html
    """
    usuario = request.user
    
    try:
        conta = AccountsPayable.objects.get(pk=pk, usuario=usuario)
    except AccountsPayable.DoesNotExist:
        messages.error(request, 'Conta a pagar não encontrada!')
        return redirect('vendas:contas_pagar_list')
    
    if request.method == 'POST':
        descricao = conta.descricao
        conta.delete()
        messages.success(request, f'Conta a pagar "{descricao}" deletada com sucesso!')
        return redirect('vendas:contas_pagar_list')
    
    contexto = {
        'conta': conta,
    }
    
    return render(request, 'vendas/contas_pagar/confirm_delete.html', contexto)


@login_required(login_url='vendas:login')
def conta_pagar_detail(request, pk):
    """
    View para visualizar detalhes de uma conta a pagar.
    
    GET: Retorna os detalhes da conta
    
    Args:
        pk: ID da conta a pagar
    
    Contexto:
        - conta: Dados da conta
    
    Template: contas_pagar/detail.html
    """
    usuario = request.user
    
    try:
        conta = AccountsPayable.objects.get(pk=pk, usuario=usuario)
    except AccountsPayable.DoesNotExist:
        messages.error(request, 'Conta a pagar não encontrada!')
        return redirect('vendas:contas_pagar_list')
    
    # Atualiza o status
    conta.atualizar_status()
    
    contexto = {
        'conta': conta,
    }
    
    return render(request, 'vendas/contas_pagar/detail.html', contexto)


@login_required(login_url='vendas:login')
def conta_pagar_marcar_pago(request, pk):
    """
    View para marcar uma conta a pagar como pago.
    
    GET: Retorna página de confirmação
    POST: Marca como pago
    
    Args:
        pk: ID da conta a pagar
    
    Template: contas_pagar/marcar_pago.html
    """
    usuario = request.user
    
    try:
        conta = AccountsPayable.objects.get(pk=pk, usuario=usuario)
    except AccountsPayable.DoesNotExist:
        messages.error(request, 'Conta a pagar não encontrada!')
        return redirect('vendas:contas_pagar_list')
    
    if request.method == 'POST':
        data_pagamento = request.POST.get('data_pagamento', '')
        
        if not data_pagamento:
            messages.error(request, 'Data de pagamento é obrigatória!')
            contexto = {'conta': conta}
            return render(request, 'vendas/contas_pagar/marcar_pago.html', contexto)
        
        try:
            data_pagamento_obj = timezone.datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            
            conta.data_pagamento = data_pagamento_obj
            conta.status = 'pago'
            conta.save()
            
            messages.success(request, f'Conta #{conta.id} marcada como paga!')
            return redirect('vendas:conta_pagar_detail', pk=pk)
        
        except Exception as e:
            messages.error(request, f'Erro ao marcar como pago: {str(e)}')
    
    contexto = {
        'conta': conta,
    }
    
    return render(request, 'vendas/contas_pagar/marcar_pago.html', contexto)


@login_required(login_url='vendas:login')
def conta_pagar_marcar_nao_pago(request, pk):
    """
    View para marcar uma conta a pagar como não pago.
    
    Args:
        pk: ID da conta a pagar
    """
    usuario = request.user
    
    try:
        conta = AccountsPayable.objects.get(pk=pk, usuario=usuario)
    except AccountsPayable.DoesNotExist:
        messages.error(request, 'Conta a pagar não encontrada!')
        return redirect('vendas:contas_pagar_list')
    
    conta.data_pagamento = None
    conta.status = 'pendente'
    conta.save()
    
    messages.success(request, f'Conta #{conta.id} marcada como não paga!')
    return redirect('vendas:conta_pagar_detail', pk=pk)