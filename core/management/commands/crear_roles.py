from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea los grupos de roles: Admin, Contador, Consulta'

    def handle(self, *args, **options):
        for nombre in ['Admin', 'Contador', 'Consulta']:
            Group.objects.get_or_create(name=nombre)
        self.stdout.write(self.style.SUCCESS('Roles creados'))
