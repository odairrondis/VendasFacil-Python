"""
=============================================================================
ARQUIVO: vendas/management/commands/criar_marcas.py
=============================================================================
Objetivo: Comando para criar marcas padrão no banco de dados
Descrição: Execute com: python manage.py criar_marcas
=============================================================================
"""

from django.core.management.base import BaseCommand
from vendas.models import Marca


class Command(BaseCommand):
    """
    Comando para criar marcas padrão.
    """
    help = 'Cria marcas padrão no banco de dados'

    def handle(self, *args, **options):
        """
        Executa o comando.
        """
        marcas = [
            'Natura',
            'Boticário',
            'Racco',
            'Avon'
        ]

        for nome_marca in marcas:
            marca, criada = Marca.objects.get_or_create(nome=nome_marca)
            if criada:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Marca "{nome_marca}" criada com sucesso')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Marca "{nome_marca}" já existe')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Marcas padrão criadas com sucesso!')
        )